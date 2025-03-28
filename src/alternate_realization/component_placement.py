import random
import numpy as np
from deap import base, creator, tools, algorithms

class Component:
    def __init__(self, name, width, height):
        self.name = name.strip().ljust(3)
        self.original_width = width
        self.original_height = height
        self.rotation = 0

    @property
    def width(self):
        return self.original_height if self.rotation else self.original_width

    @property
    def height(self):
        return self.original_width if self.rotation else self.original_height

def create_components():
    components = []
    total_area = 0
    board_area = BOARD_WIDTH * BOARD_HEIGHT
    
    n = int(input("Введите количество компонентов: "))
    for i in range(n):
        while True:
            try:
                w = int(input(f"Ширина компонента {i+1}: "))
                h = int(input(f"Высота компонента {i+1}: "))
                if w <= 0 or h <= 0:
                    raise ValueError("Размеры должны быть положительными")
                
                min_dim = min(w, h)
                if min_dim > BOARD_WIDTH or min_dim > BOARD_HEIGHT:
                    print("Ошибка: компонент не помещается даже с поворотом!")
                    continue
                
                components.append(Component(f"C{i+1}", w, h))
                total_area += w * h
                if total_area > board_area * 1.5:
                    print("Предупреждение: Суммарная площадь превышает 150% платы!")
                break
            except ValueError as e:
                print(f"Ошибка: {e}. Повторите ввод.")
    return components

# Конфигурация
BOARD_WIDTH = 20
BOARD_HEIGHT = 20
COMPONENTS = create_components()
POPULATION_SIZE = 50
GENERATIONS = 10000
CXPB = 0.7
MUTPB = 0.2
VISUALIZATION_STEPS = [10, 50, 100, 200, 500, 1000, 5000, 10000]

# Настройка DEAP
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

def generate_coordinate(component_idx):
    comp = COMPONENTS[component_idx]
    max_x = BOARD_WIDTH - comp.width
    max_y = BOARD_HEIGHT - comp.height
    return (
        random.randint(0, max_x) if max_x >= 0 else 0,
        random.randint(0, max_y) if max_y >= 0 else 0,
        random.randint(0, 1)
    )

def individual_generator():
    ind = []
    for i in range(len(COMPONENTS)):
        x, y, rot = generate_coordinate(i)
        COMPONENTS[i].rotation = rot
        ind.extend([x, y, rot])
    return ind

toolbox.register("individual", tools.initIterate, creator.Individual, individual_generator)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluate(individual):
    placements = np.array(individual).reshape(-1, 3)
    overlaps = 0
    out_of_board = 0

    # Обновление поворотов и проверка границ
    for i, (x, y, rot) in enumerate(placements):
        comp = COMPONENTS[i]
        comp.rotation = rot
        if x + comp.width > BOARD_WIDTH or y + comp.height > BOARD_HEIGHT:
            out_of_board += 1

    # Проверка пересечений
    for i in range(len(COMPONENTS)):
        for j in range(i+1, len(COMPONENTS)):
            xi, yi, _ = placements[i]
            xj, yj, _ = placements[j]
            wi, hi = COMPONENTS[i].width, COMPONENTS[i].height
            wj, hj = COMPONENTS[j].width, COMPONENTS[j].height

            if not (xi + wi <= xj or xj + wj <= xi or yi + hi <= yj or yj + hj <= yi):
                overlaps += 1

    # Расчет длины соединений
    centers = []
    for i, (x, y, _) in enumerate(placements):
        comp = COMPONENTS[i]
        centers.append((x + comp.width/2, y + comp.height/2))
    
    total_wirelength = 0.0
    for i in range(len(centers)):
        for j in range(i+1, len(centers)):
            dx = centers[i][0] - centers[j][0]
            dy = centers[i][1] - centers[j][1]
            total_wirelength += (dx**2 + dy**2)**0.5

    penalty = overlaps * 1000 + out_of_board * 5000
    return (total_wirelength + penalty,)

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutUniformInt, low=0, up=BOARD_WIDTH-1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)

def mutRotation(individual, indpb):
    for i in range(2, len(individual), 3):
        if random.random() < indpb:
            individual[i] = 1 - individual[i]
    return individual,

toolbox.register("mutate_rotation", mutRotation, indpb=0.1)

def main():
    random.seed(42)
    population = toolbox.population(n=POPULATION_SIZE)

    # Основной цикл эволюции
    for gen in range(1, GENERATIONS + 1):
        offspring = toolbox.select(population, len(population))
        offspring = list(map(toolbox.clone, offspring))

        # Кроссовер
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        # Мутация
        for i in range(len(offspring)):
            if random.random() < MUTPB:
                offspring[i], = toolbox.mutate_rotation(offspring[i])
                offspring[i], = toolbox.mutate(offspring[i])
                del offspring[i].fitness.values

        # Оценка
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        population[:] = offspring

        # Визуализация
        if gen in VISUALIZATION_STEPS:
            best_ind = tools.selBest(population, k=1)[0]
            print(f"\n--- Поколение {gen} ---")
            print("Целевая функция:", best_ind.fitness.values[0])
            visualize_placement(best_ind)

    # Финальный результат
    best_individual = tools.selBest(population, k=1)[0]
    print("\n--- Финальный результат ---")
    visualize_placement(best_individual)
    print("Значение функции:", best_individual.fitness.values[0])

    # Проверка кастомных значений
    while True:
        check_custom = input("\nПроверить свое расположение? (да/нет): ").lower()
        if check_custom != 'да':
            break
        test_custom_layout()

def test_custom_layout():
    """Функция для проверки пользовательского расположения"""
    custom_individual = []
    print("\nВведите параметры для каждого компонента:")
    
    for i, comp in enumerate(COMPONENTS):
        print(f"\nКомпонент {comp.name.strip()} (ширина: {comp.original_width}, высота: {comp.original_height}):")
        while True:
            try:
                x = int(input("X координата: "))
                y = int(input("Y координата: "))
                rot = int(input("Поворот (0-нет, 1-да): "))
                if rot not in (0, 1):
                    raise ValueError
                    
                # Проверка границ
                current_width = comp.original_height if rot else comp.original_width
                current_height = comp.original_width if rot else comp.original_height
                if x + current_width > BOARD_WIDTH or y + current_height > BOARD_HEIGHT:
                    print("Предупреждение: Компонент выходит за границы платы!")
                    
                custom_individual.extend([x, y, rot])
                break
            except ValueError:
                print("Некорректный ввод! Повторите.")

    # Расчет целевой функции
    score = evaluate(custom_individual)
    print("\n--- Результат проверки ---")
    print("Координаты:", custom_individual)
    print("Значение целевой функции:", score[0])
    visualize_placement(custom_individual)

def visualize_placement(individual):
    placements = np.array(individual).reshape(-1, 3)
    cell_width = 3
    empty_cell = " " * cell_width
    board = np.full((BOARD_HEIGHT, BOARD_WIDTH), empty_cell, dtype=f'U{cell_width}')
    
    for idx, (x, y, rot) in enumerate(placements):
        comp = COMPONENTS[idx]
        comp.rotation = rot
        w = comp.width
        h = comp.height
        
        if x + w > BOARD_WIDTH or y + h > BOARD_HEIGHT:
            print(f"{comp.name} выходит за границы! [X={x}-{x+w}, Y={y}-{y+h}]")
            continue
            
        symbol = comp.name.strip() + ("'" if rot else " ")
        for dy in range(h):
            for dx in range(w):
                if board[y + dy, x + dx] == empty_cell:
                    board[y + dy, x + dx] = symbol.ljust(cell_width)
                else:
                    board[y + dy, x + dx] = "XX "

    print("\nВизуализация платы:")
    for row in board:
        print("|" + "|".join(row) + "|")

if __name__ == "__main__":
    main()