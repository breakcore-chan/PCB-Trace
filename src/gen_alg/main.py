from deap import base, algorithms
from deap import creator
from deap import tools

import random
import matplotlib.pyplot as plt
import numpy as np

# константы задачи
ONE_MAX_LENGTH = 100    # длина подлежащей оптимизации битовой строки

# константы генетического алгоритма
POPULATION_SIZE = 200   # количество индивидуумов в популяции
P_CROSSOVER = 0.9       # вероятность скрещивания
P_MUTATION = 0.1        # вероятность мутации индивидуума
MAX_GENERATIONS = 50    # максимальное количество поколений

RANDOM_SEED = 2
random.seed(RANDOM_SEED)

# по сути это другой виз записи создания класса
# 1 - имя, 2 - от кого наследуемся, далее - параметры
# неизменяемые - атрибуты класса, изменяемые - атрибуты объекта
# fitness - операции над значениями приспособленности индивида
# weights - кортеж весов параметров приспособленности
creator.create("FitnessMax", base.Fitness, weights=(1.0,)) # создание поля приспособленности индивида
creator.create("Individual", list, fitness=creator.FitnessMax) # создание класса индивида(поскольку наследуемся от списка, то индивид - это список генов)

# функция вычисления приспособленности конкретного индивидуума
def oneMaxFitness(individual):
    return sum(individual), # кортеж

# объявляем "пространство имён" функций для алгоритма
toolbox = base.Toolbox()

# 1 - алиас, 2 - ссылка на функцию, далее - параметры переданной функции
toolbox.register("zeroOrOne", random.randint, 0, 1) # функция, возвращающая случайно 0 или 1
# tools.initRepeat - встроенная функция генерации списков
# Individual - контейнер для хранения генов, 2 - функция вычисления генов, 3 - число генов в хромосоме
toolbox.register("individualCreator", tools.initRepeat, creator.Individual, toolbox.zeroOrOne, ONE_MAX_LENGTH) # функция создания индивида
toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator) # функция создания популяции

population = toolbox.populationCreator(n=POPULATION_SIZE)

# предопределённые алиасы, нужно писать именно такие имена
toolbox.register("evaluate", oneMaxFitness) # вычисление приспособленности
toolbox.register("select", tools.selTournament, tournsize=3) # турнирный отбор
toolbox.register("mate", tools.cxOnePoint) # скрещивание
toolbox.register("mutate", tools.mutFlipBit, indpb=1.0/ONE_MAX_LENGTH) # мутация

stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("max", np.max)
stats.register("avg", np.mean)

population, logbook = algorithms.eaSimple(population, toolbox,
                                        cxpb=P_CROSSOVER,
                                        mutpb=P_MUTATION,
                                        ngen=MAX_GENERATIONS,
                                        stats=stats,
                                        verbose=True)

# максимально и среднее значение приспособленности особи в популяции
maxFitnessValues, meanFitnessValues = logbook.select("max", "avg")

plt.plot(maxFitnessValues, color='red')
plt.plot(meanFitnessValues, color='green')
plt.xlabel('Поколение')
plt.ylabel('Макс/средняя приспособленность')
plt.title('Зависимость максимальной и средней приспособленности от поколения')
# plt.show()
plt.savefig("src\plots\plot.png")

