import random
import tkinter as tk
from tkinter import scrolledtext, ttk

import numpy as np
from deap import base, creator, tools

from src.utils.base_config import base_config
from src.application.genetic_algorithm.protocol import GAProcessorProtocol


class GAProcessorV1(GAProcessorProtocol):
    def __init__(self, config: dict):
        self.config = config  # Используемый конфиг из дериктории
        self.setup_ga()
        self.visualization_window = None
        self.generations_data = []
        self.current_generation_idx = 0
        self.fitness = []

    def setup_ga(self):
        """Инициализация генетического алгоритма"""
        if not hasattr(creator, "FitnessMin"):  # Если не задана функция минимизации
            creator.create(
                "FitnessMin", base.Fitness, weights=(-1.0,)
            )  # Создаём функцию оценки(минимизации) с параметром до куда нужно минимизировать
        if not hasattr(creator, "Individual"):  # Если не задан индивид
            creator.create(
                "Individual", list, fitness=creator.FitnessMin
            )  # Создаём индивида, в виде генома(листа), с заданой функцией оценки как локальное свойство класса индивида

        self.toolbox = (
            base.Toolbox()
        )  # Класс для создания функций для работы с индивидами и популяцией
        self.toolbox.register(
            "individual", self.individual_generator
        )  # Алиас для вызова функции создания индивида
        self.toolbox.register(
            "population", tools.initRepeat, list, self.toolbox.individual
        )  # Создание популяции, популяция - список, каждый элемент которого - список, хромосома особи
        self.toolbox.register(
            "evaluate", self.evaluate
        )  # Алиас для функции оценки особи
        self.toolbox.register("mate", tools.cxTwoPoint)  # Алиас для функции скрещивания
        self.toolbox.register(
            "mutate",
            tools.mutUniformInt,
            low=0,
            up=max(self.config["board_width"], self.config["board_height"]) - 1,
            indpb=0.1,
        )  # Алиас для функции мутации
        # TODO добавить в конфиг возможность выбора функции отбора и размера турнирной сетки
        self.toolbox.register(
            "select", tools.selTournament, tournsize=3
        )  # Алиас для функции отбора(в данном случае турнирного)
        self.toolbox.register(
            "mutate_rotation", self.mutRotation, indpb=base_config["indpb"]
        )  # Алиас для функции мутации поворота, срабатывает с шансом
        # TODO добавить в конфиг параметр indpb - вероятность конкрентой мутации(у нас вероятность поворота)

    def individual_generator(self):
        """Генерация случайной особи"""
        genome = []
        for comp in self.config["components"]:  # Перебираем все компоненты в конфиге
            max_x = (
                self.config["board_width"] - comp["width"]
            )  # В каком диапазоне может появиться компонент по ширине
            max_y = (
                self.config["board_height"] - comp["height"]
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

    def mutRotation(self, individual: list, indpb: float):
        """Мутация поворота компонента"""
        for i in range(2, len(individual), 3):
            if (
                random.random() < indpb
            ):  # Поворачиваем компонент, если сработала вераятность
                individual[i] = 1 - individual[i]
        return (individual,)

    def evaluate(self, individual):
        """Функция оценки особи"""
        placements = np.array(individual).reshape(-1, 3)  # Преобразуем в матрицу N x 3
        overlaps = 0  # Количество пересечений
        out_of_board = 0  # Выход за границы платы

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

        self.fitness.append(best_ind.fitness.values[0])

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

                self.fitness.append(best_ind.fitness.values[0])

                # Автоматически показываем последнее сохраненное поколение
                self.current_generation_idx = len(self.generations_data) - 1
                self.display_generation(self.current_generation_idx)
                self.update_navigation_buttons()

                if log:
                    log(f"\nПоколение {gen}:")
                    log(f"Оценочная функция: {best_ind.fitness.values[0]}")

        return population, self.fitness
