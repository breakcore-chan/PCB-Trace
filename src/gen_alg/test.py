import math
import random

import numpy
from deap import algorithms, base, creator, tools

# Параметры задачи
WIDTH = 100  # Ширина платы
HEIGHT = 100  # Высота платы
NUM_ELEMENTS = 10  # Количество элементов
CONNECTIONS = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (8, 9),
]  # Связи
ELEMENT_RADIUS = 5  # Радиус элемента (для проверки пересечений)
PENALTY_MULTIPLIER = 1000  # Множитель штрафа за пересечение

# Настройка типов DEAP
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

# Генераторы атрибутов
toolbox.register("attr_x", random.uniform, 0, WIDTH)
toolbox.register("attr_y", random.uniform, 0, HEIGHT)

# Создание особи
toolbox.register(
    "individual",
    tools.initCycle,
    creator.Individual,
    (toolbox.attr_x, toolbox.attr_y),
    n=NUM_ELEMENTS,
)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


# Функция оценки
def evaluate(individual):
    total_length = 0.0
    # Сумма длин связей
    for i, j in CONNECTIONS:
        x1, y1 = individual[2 * i], individual[2 * i + 1]
        x2, y2 = individual[2 * j], individual[2 * j + 1]
        total_length += math.hypot(x2 - x1, y2 - y1)

    # Штраф за пересечения
    penalty = 0
    for a in range(NUM_ELEMENTS):
        xa, ya = individual[2 * a], individual[2 * a + 1]
        for b in range(a + 1, NUM_ELEMENTS):
            xb, yb = individual[2 * b], individual[2 * b + 1]
            distance = math.hypot(xb - xa, yb - ya)
            if distance < 2 * ELEMENT_RADIUS:
                penalty += PENALTY_MULTIPLIER

    return (total_length + penalty,)


# Регистрация операторов
toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=3, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)


def main():
    # Параметры алгоритма
    pop_size = 100
    num_generations = 50
    cx_prob = 0.7
    mut_prob = 0.2

    # Инициализация популяции
    pop = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("min", numpy.min)

    # Запуск генетического алгоритма
    pop, log = algorithms.eaSimple(
        pop,
        toolbox,
        cxpb=cx_prob,
        mutpb=mut_prob,
        ngen=num_generations,
        stats=stats,
        halloffame=hof,
        verbose=True,
    )

    # Вывод результата
    best_ind = hof[0]
    print(f"Лучшее решение: {best_ind}")
    # print(f"Длина связей: {best_ind.fitness.values[0] - sum(penalty for _ in range(1))}")  # Условный вывод


if __name__ == "__main__":
    main()
