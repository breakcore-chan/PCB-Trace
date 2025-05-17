import random
from typing import Any

import numpy as np
from deap import base, creator, tools

from src.application.genetic_algorithm.protocol import GAProcessorProtocol
from src.utils.base_config import base_config


class GAProcessorV2(GAProcessorProtocol):
    def _setup_ga(self, config: dict[str, Any]) -> base.Toolbox:
        """Инициализация генетического алгоритма"""
        if not hasattr(creator, "FitnessMin"):  # Если не задана функция минимизации
            creator.create(
                "FitnessMin", base.Fitness, weights=(-1.0,)
            )  # Создаём функцию оценки(минимизации) с параметром до куда нужно минимизировать
        if not hasattr(creator, "Individual"):  # Если не задан индивид
            creator.create(
                "Individual", list, fitness=creator.FitnessMin
            )  # Создаём индивида, в виде генома(листа), с заданой функцией оценки как локальное свойство класса индивида

        toolbox = (
            base.Toolbox()
        )  # Класс для создания функций для работы с индивидами и популяцией
        toolbox.register(
            "individual", self._individual_generator
        )  # Алиас для вызова функции создания индивида
        toolbox.register(
            "population", tools.initRepeat, list, toolbox.individual
        )  # Создание популяции, популяция - список, каждый элемент которого - список, хромосома особи
        toolbox.register("_evaluate", self._evaluate)  # Алиас для функции оценки особи
        toolbox.register("mate", tools.cxTwoPoint)  # Алиас для функции скрещивания
        toolbox.register(
            "mutate",
            tools.mutUniformInt,
            low=0,
            up=max(config["board_width"], config["board_height"]) - 1,
            indpb=base_config["indpb"],
        )  # Алиас для функции мутации
        # TODO добавить в конфиг возможность выбора функции отбора и размера турнирной сетки
        toolbox.register(
            "select", tools.selTournament, tournsize=3
        )  # Алиас для функции отбора(в данном случае турнирного)
        toolbox.register(
            "mutate_rotation", self._mut_rotation, indpb=base_config["indpb"]
        )  # Алиас для функции мутации поворота, срабатывает с шансом
        return toolbox

    def _individual_generator(self):
        """Генерация случайной особи"""
        genome = []
        for comp in self.__config["components"]:  # Перебираем все компоненты в конфиге
            max_x = (
                self.__config["board_width"] - comp["width"]
            )  # В каком диапазоне может появиться компонент по ширине
            max_y = (
                self.__config["board_height"] - comp["height"]
            )  # В каком диапазоне может появиться компонент по высоте
            x = (
                random.randint(0, max_x) if max_x >= 0 else 0
            )  # Случайная координата по x
            y = (
                random.randint(0, max_y) if max_y >= 0 else 0
            )  # Случайная координата по y
            rot = random.randint(0, 1)  # Повёрнут или нет
            genome.extend(
                [x, y, rot]
            )  # Итоговый геном одной особи состоит из 3-х хромосом
        return creator.Individual(genome)  # Геном особи - размещение всех компонентов

    def _mut_rotation(self, individual: list, indpb: float):
        """Мутация поворота компонента"""
        for i in range(2, len(individual), 3):
            if (
                random.random() < indpb
            ):  # Поворачиваем компонент, если сработала вераятность
                individual[i] = 1 - individual[i]
        return (individual,)

    def _evaluate(self, individual) -> tuple[float,]:
        """Функция оценки особи"""
        placements = np.array(individual).reshape(-1, 3)  # Преобразуем в матрицу N x 3
        overlaps = 0  # Количество пересечений
        out_of_board = 0  # Выход за границы платы

        for i, (x, y, rot) in enumerate(placements):
            comp = self.__config["components"][i]
            width = comp["height"] if rot else comp["width"]
            height = comp["width"] if rot else comp["height"]
            if (
                x + width > self.__config["board_width"]
                or y + height > self.__config["board_height"]
            ):
                out_of_board += 1

        for i in range(len(self.__config["components"])):
            for j in range(i + 1, len(self.__config["components"])):
                xi, yi, _ = placements[i]
                xj, yj, _ = placements[j]
                wi = (
                    self.__config["components"][i]["height"]
                    if placements[i][2]
                    else self.__config["components"][i]["width"]
                )
                hi = (
                    self.__config["components"][i]["width"]
                    if placements[i][2]
                    else self.__config["components"][i]["height"]
                )
                wj = (
                    self.__config["components"][j]["height"]
                    if placements[j][2]
                    else self.__config["components"][j]["width"]
                )
                hj = (
                    self.__config["components"][j]["width"]
                    if placements[j][2]
                    else self.__config["components"][j]["height"]
                )

                if not (
                    xi + wi <= xj or xj + wj <= xi or yi + hi <= yj or yj + hj <= yi
                ):
                    overlaps += 1

        centers = []
        for i, (x, y, rot) in enumerate(placements):
            comp = self.__config["components"][i]
            width = comp["height"] if rot else comp["width"]
            height = comp["width"] if rot else comp["height"]
            centers.append((x + width / 2, y + height / 2))

        total_wirelength = 0.0
        for a, b in self.__config["connections"]:
            dx = centers[a][0] - centers[b][0]
            dy = centers[a][1] - centers[b][1]
            total_wirelength += (dx**2 + dy**2) ** 0.5

        penalty = overlaps * 1000 + out_of_board * 5000
        return (total_wirelength + penalty,)

    def run(self, config: dict) -> tuple[list, list]:
        """Запуск генетического алгоритма для `config` без сохранения состояния"""
        self.__config = config
        toolbox = self._setup_ga(config)
        if len(self.__config["components"]) == 0:
            raise ValueError(
                "Нет компонентов для размещения. Добавьте компоненты в конфигурацию."
            )

        fitness_list = []  # Список значений функции приспособленности

        # Инициализация популяции
        population = toolbox.population(n=self.__config["population_size"])

        # Инициализация fitness
        for ind in population:
            ind.fitness.values = toolbox._evaluate(ind)

        # Основной цикл генетического алгоритма
        for generation in range(0, self.__config["generations"] + 1):
            # Селекция и создание потомков
            offspring = toolbox.select(population, len(population))
            offspring = list(map(toolbox.clone, offspring))

            # Кроссовер
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.__config["cxpb"]:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Мутация
            for mutant in offspring:
                if random.random() < self.__config["mutpb"]:
                    toolbox.mutate(mutant)
                    toolbox.mutate_rotation(mutant)
                    del mutant.fitness.values

            # Оценка новых особей
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox._evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            population[:] = offspring

            # Сохраняем поколения для визуализации
            if generation in self.__config["visualization_steps"]:
                best_ind = tools.selBest(population, k=1)[0]
                fitness_list.append(float(best_ind.fitness.values[0]))
        return population, fitness_list
