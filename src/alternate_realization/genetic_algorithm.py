import random
import numpy as np
from deap import base, creator, tools, algorithms

class GeneticAlgorithm:
    def __init__(self, config):
        self.config = config
        self.setup_ga()

    def setup_ga(self):
        """Настраивает генетический алгоритм"""
        # Проверяем, существует ли уже класс FitnessMin
        if not hasattr(creator, "FitnessMin"):
            creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        
        # Проверяем, существует ли уже класс Individual
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMin)

        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self.individual_generator)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluate)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutUniformInt, low=0, up=self.config["board_width"]-1, indpb=0.1)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def individual_generator(self):
        """Генератор особи"""
        ind = []
        for _ in range(len(self.config["components"])):
            x = random.randint(0, self.config["board_width"] - 1)
            y = random.randint(0, self.config["board_height"] - 1)
            rot = random.randint(0, 1)
            ind.extend([x, y, rot])
        
        # Создаем объект Individual и инициализируем его fitness
        individual = creator.Individual(ind)
        individual.fitness = creator.FitnessMin()
        return individual

    def evaluate(self, individual):
        """Оценивает приспособленность особи"""
        placements = np.array(individual).reshape(-1, 3)
        overlaps = 0
        out_of_board = 0

        # Проверка пересечений и границ
        for i, (x, y, rot) in enumerate(placements):
            comp = self.config["components"][i]
            if x + comp["width"] > self.config["board_width"] or y + comp["height"] > self.config["board_height"]:
                out_of_board += 1

        for i in range(len(self.config["components"])):
            for j in range(i+1, len(self.config["components"])):
                xi, yi, _ = placements[i]
                xj, yj, _ = placements[j]
                wi, hi = self.config["components"][i]["width"], self.config["components"][i]["height"]
                wj, hj = self.config["components"][j]["width"], self.config["components"][j]["height"]

                if not (xi + wi <= xj or xj + wj <= xi or yi + hi <= yj or yj + hj <= yi):
                    overlaps += 1

        # Расчет длины соединений
        centers = []
        for i, (x, y, _) in enumerate(placements):
            comp = self.config["components"][i]
            centers.append((x + comp["width"]/2, y + comp["height"]/2))
        
        total_wirelength = 0.0
        for a, b in self.config["connections"]:
            dx = centers[a][0] - centers[b][0]
            dy = centers[a][1] - centers[b][1]
            total_wirelength += (dx**2 + dy**2)**0.5

        penalty = overlaps * 1000 + out_of_board * 5000
        return (total_wirelength + penalty,)

    def visualize_placement(self, individual, log):
        """Визуализирует размещение элементов на плате"""
        placements = np.array(individual).reshape(-1, 3)
        cell_width = 3
        empty_cell = " " * cell_width
        board = np.full((self.config["board_height"], self.config["board_width"]), empty_cell, dtype=f'U{cell_width}')
        
        for idx, (x, y, rot) in enumerate(placements):
            comp = self.config["components"][idx]
            w = comp["width"]
            h = comp["height"]
            
            if x + w > self.config["board_width"] or y + h > self.config["board_height"]:
                log(f"Компонент {idx + 1} выходит за границы! [X={x}-{x+w}, Y={y}-{y+h}]")
                continue
                
            symbol = f"C{idx + 1}" + ("'" if rot else " ")
            for dy in range(h):
                for dx in range(w):
                    if board[y + dy, x + dx] == empty_cell:
                        board[y + dy, x + dx] = symbol.ljust(cell_width)
                    else:
                        board[y + dy, x + dx] = "XX "

        log("\nВизуализация платы:")
        for row in board:
            log("|" + "|".join(row) + "|")

    def run(self, log=None, visualization_steps=None):
        """Запускает генетический алгоритм"""
        if len(self.config["components"]) == 0:
            raise ValueError("Нет компонентов для размещения. Добавьте компоненты в конфигурацию.")

        population = self.toolbox.population(n=self.config["population_size"])
        
        # Инициализируем fitness для каждой особи
        for individual in population:
            individual.fitness.values = self.toolbox.evaluate(individual)
        
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)

        # Логирование начальной популяции
        if log:
            log("Начальная популяция:")
            best_ind = tools.selBest(population, k=1)[0]
            self.visualize_placement(best_ind, log)
            log(f"Оценочная функция: {best_ind.fitness.values[0]}")

        # Основной цикл генетического алгоритма
        for gen in range(self.config["generations"]):
            population = algorithms.varAnd(population, self.toolbox, cxpb=self.config["cxpb"], mutpb=self.config["mutpb"])
            
            # Оценка приспособленности новых особей
            for ind in population:
                ind.fitness.values = self.toolbox.evaluate(ind)
            
            # Логирование текущего поколения, если оно указано в visualization_steps
            if log and visualization_steps and gen in visualization_steps:
                log(f"\nПоколение {gen}:")
                best_ind = tools.selBest(population, k=1)[0]
                self.visualize_placement(best_ind, log)
                log(f"Оценочная функция: {best_ind.fitness.values[0]}")

        # Логирование финальной популяции
        if log:
            log("\nФинальная популяция:")
            best_ind = tools.selBest(population, k=1)[0]
            self.visualize_placement(best_ind, log)
            log(f"Оценочная функция: {best_ind.fitness.values[0]}")

        return population, None