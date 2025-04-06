import random
import tkinter as tk
from tkinter import scrolledtext, ttk

import numpy as np
from deap import base, creator, tools


class GeneticAlgorithm:
    def __init__(self, config):
        self.config = config
        self.setup_ga()
        self.visualization_window = None
        self.generations_data = []
        self.current_generation_idx = 0

    def setup_ga(self):
        """Инициализация генетического алгоритма"""
        if not hasattr(creator, "FitnessMin"):
            creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMin)

        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self.individual_generator)
        self.toolbox.register(
            "population", tools.initRepeat, list, self.toolbox.individual
        )
        self.toolbox.register("evaluate", self.evaluate)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register(
            "mutate",
            tools.mutUniformInt,
            low=0,
            up=max(self.config["board_width"], self.config["board_height"]) - 1,
            indpb=0.1,
        )
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("mutate_rotation", self.mutRotation, indpb=0.1)

    def individual_generator(self):
        """Генерация случайной особи"""
        ind = []
        for comp in self.config["components"]:
            max_x = self.config["board_width"] - comp["width"]
            max_y = self.config["board_height"] - comp["height"]
            x = random.randint(0, max_x) if max_x >= 0 else 0
            y = random.randint(0, max_y) if max_y >= 0 else 0
            rot = random.randint(0, 1)
            ind.extend([x, y, rot])
        return creator.Individual(ind)

    def mutRotation(self, individual, indpb):
        """Мутация поворота компонента"""
        for i in range(2, len(individual), 3):
            if random.random() < indpb:
                individual[i] = 1 - individual[i]
        return (individual,)

    def evaluate(self, individual):
        """Функция оценки особи"""
        placements = np.array(individual).reshape(-1, 3)
        overlaps = 0
        out_of_board = 0

        for i, (x, y, rot) in enumerate(placements):
            comp = self.config["components"][i]
            width = comp["height"] if rot else comp["width"]
            height = comp["width"] if rot else comp["height"]
            if (
                x + width > self.config["board_width"]
                or y + height > self.config["board_height"]
            ):
                out_of_board += 1

        for i in range(len(self.config["components"])):
            for j in range(i + 1, len(self.config["components"])):
                xi, yi, _ = placements[i]
                xj, yj, _ = placements[j]
                wi = (
                    self.config["components"][i]["height"]
                    if placements[i][2]
                    else self.config["components"][i]["width"]
                )
                hi = (
                    self.config["components"][i]["width"]
                    if placements[i][2]
                    else self.config["components"][i]["height"]
                )
                wj = (
                    self.config["components"][j]["height"]
                    if placements[j][2]
                    else self.config["components"][j]["width"]
                )
                hj = (
                    self.config["components"][j]["width"]
                    if placements[j][2]
                    else self.config["components"][j]["height"]
                )

                if not (
                    xi + wi <= xj or xj + wj <= xi or yi + hi <= yj or yj + hj <= yi
                ):
                    overlaps += 1

        centers = []
        for i, (x, y, rot) in enumerate(placements):
            comp = self.config["components"][i]
            width = comp["height"] if rot else comp["width"]
            height = comp["width"] if rot else comp["height"]
            centers.append((x + width / 2, y + height / 2))

        total_wirelength = 0.0
        for a, b in self.config["connections"]:
            dx = centers[a][0] - centers[b][0]
            dy = centers[a][1] - centers[b][1]
            total_wirelength += (dx**2 + dy**2) ** 0.5

        penalty = overlaps * 1000 + out_of_board * 5000
        return (total_wirelength + penalty,)

    def create_visualization_window(self):
        """Создание окна для визуализации с навигацией"""
        self.visualization_window = tk.Toplevel()
        self.visualization_window.title("Визуализация размещения компонентов")

        # Фрейм для навигации и информации
        nav_frame = ttk.Frame(self.visualization_window)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)

        # Кнопки навигации
        self.prev_btn = ttk.Button(
            nav_frame, text="← Предыдущее", command=self.show_prev_generation
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(
            nav_frame, text="Следующее →", command=self.show_next_generation
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)

        # Информация о поколении
        info_frame = ttk.Frame(nav_frame)
        info_frame.pack(side=tk.LEFT, padx=20)

        ttk.Label(info_frame, text="Поколение:").pack(side=tk.LEFT)
        self.generation_label = ttk.Label(
            info_frame, text="0", font=("Arial", 10, "bold")
        )
        self.generation_label.pack(side=tk.LEFT, padx=5)

        ttk.Label(info_frame, text="Целевая функция:").pack(side=tk.LEFT)
        self.fitness_label = ttk.Label(
            info_frame, text="0.0", font=("Arial", 10, "bold")
        )
        self.fitness_label.pack(side=tk.LEFT, padx=5)

        # Область для отображения платы
        board_frame = ttk.Frame(self.visualization_window)
        board_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.board_text = scrolledtext.ScrolledText(
            board_frame, width=60, height=30, font=("Courier New", 10), wrap=tk.NONE
        )
        self.board_text.pack(fill=tk.BOTH, expand=True)

        # Информация о компонентах
        self.components_info = scrolledtext.ScrolledText(
            self.visualization_window, height=8, font=("Arial", 9)
        )
        self.components_info.pack(fill=tk.X, padx=5, pady=5)

    def show_prev_generation(self):
        """Показать предыдущее сохраненное поколение"""
        if self.current_generation_idx > 0:
            self.current_generation_idx -= 1
            self.display_generation(self.current_generation_idx)
            self.update_navigation_buttons()

    def show_next_generation(self):
        """Показать следующее сохраненное поколение"""
        if self.current_generation_idx < len(self.generations_data) - 1:
            self.current_generation_idx += 1
            self.display_generation(self.current_generation_idx)
            self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Обновить состояние кнопок навигации"""
        self.prev_btn.config(
            state=tk.NORMAL if self.current_generation_idx > 0 else tk.DISABLED
        )
        self.next_btn.config(
            state=(
                tk.NORMAL
                if self.current_generation_idx < len(self.generations_data) - 1
                else tk.DISABLED
            )
        )

    def display_generation(self, gen_idx):
        """Отобразить указанное поколение"""
        if 0 <= gen_idx < len(self.generations_data):
            gen_data = self.generations_data[gen_idx]
            individual, gen, fitness = gen_data

            self.generation_label.config(text=str(gen))
            self.fitness_label.config(text=f"{fitness:.2f}")

            self.board_text.delete(1.0, tk.END)
            self.components_info.delete(1.0, tk.END)

            # Визуализация платы
            placements = np.array(individual).reshape(-1, 3)
            cell_width = 3
            empty_cell = " " * cell_width
            board = np.full(
                (self.config["board_height"], self.config["board_width"]),
                empty_cell,
                dtype=f"U{cell_width}",
            )

            components_data = []
            out_of_bounds = []

            for idx, (x, y, rot) in enumerate(placements):
                comp = self.config["components"][idx]
                width = comp["height"] if rot else comp["width"]
                height = comp["width"] if rot else comp["height"]

                if (
                    x + width > self.config["board_width"]
                    or y + height > self.config["board_height"]
                ):
                    out_of_bounds.append(
                        f"Компонент {idx+1} ({width}x{height}) выходит за границы! [X={x}-{x+width}, Y={y}-{y+height}]"
                    )
                    continue

                symbol = f"C{idx + 1}" + ("'" if rot else " ")
                for dy in range(height):
                    for dx in range(width):
                        if board[y + dy, x + dx] == empty_cell:
                            board[y + dy, x + dx] = symbol.ljust(cell_width)
                        else:
                            board[y + dy, x + dx] = "XX "

                components_data.append(
                    f"Компонент {idx+1}: X={x}, Y={y}, Поворот={rot}, Размер={width}x{height}"
                )

            self.board_text.insert(tk.END, "Плата:\n")
            for row in board:
                self.board_text.insert(tk.END, "|" + "|".join(row) + "|\n")

            self.components_info.insert(tk.END, "Расположение компонентов:\n")
            self.components_info.insert(tk.END, "\n".join(components_data))

            if out_of_bounds:
                self.components_info.insert(tk.END, "\n\nОшибки:\n")
                self.components_info.insert(tk.END, "\n".join(out_of_bounds))

            self.board_text.see(tk.END)
            self.components_info.see(tk.END)

    def run(self, log=None, visualization_steps=None):
        """Основной метод запуска генетического алгоритма"""
        if len(self.config["components"]) == 0:
            raise ValueError(
                "Нет компонентов для размещения. Добавьте компоненты в конфигурацию."
            )

        vis_steps = (
            visualization_steps
            if visualization_steps is not None
            else self.config.get("visualization_steps", [])
        )
        self.generations_data = []

        population = self.toolbox.population(n=self.config["population_size"])

        # Инициализация fitness
        for ind in population:
            ind.fitness.values = self.toolbox.evaluate(ind)

        # Создаем окно визуализации
        self.create_visualization_window()

        # Сохраняем начальную популяцию
        best_ind = tools.selBest(population, k=1)[0]
        self.generations_data.append((best_ind, 0, best_ind.fitness.values[0]))
        self.display_generation(0)
        self.update_navigation_buttons()

        if log:
            log("Начальная популяция:")
            log("Поколение: 0")
            log(f"Оценочная функция: {best_ind.fitness.values[0]}")

        # Основной цикл генетического алгоритма
        for gen in range(1, self.config["generations"] + 1):
            # Селекция и создание потомков
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))

            # Кроссовер
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.config["cxpb"]:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Мутация
            for mutant in offspring:
                if random.random() < self.config["mutpb"]:
                    self.toolbox.mutate(mutant)
                    self.toolbox.mutate_rotation(mutant)
                    del mutant.fitness.values

            # Оценка новых особей
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            population[:] = offspring

            # Сохраняем поколения для визуализации
            if gen in vis_steps or gen == self.config["generations"]:
                best_ind = tools.selBest(population, k=1)[0]
                self.generations_data.append(
                    (best_ind, gen, best_ind.fitness.values[0])
                )

                # Автоматически показываем последнее сохраненное поколение
                self.current_generation_idx = len(self.generations_data) - 1
                self.display_generation(self.current_generation_idx)
                self.update_navigation_buttons()

                if log:
                    log(f"\nПоколение {gen}:")
                    log(f"Оценочная функция: {best_ind.fitness.values[0]}")

        return population, None
