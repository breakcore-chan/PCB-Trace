import random
import time
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any


from src.application.genetic_algorithm.processor_v2 import GAProcessorV2
from src.presentation.component_editor import ComponentEditor
from src.presentation.plot_window import PlotWindow
from src.utils.base_config import base_config
from src.application.config_manager.config_manager_v2 import ConfigManagerV2
from src.presentation.ga_window import GAWindow


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конфигурации для размещения элементов")
        self.config_manager = ConfigManagerV2()
        self.fitness = []
        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Левая панель: список конфигураций и кнопки
        left_frame = ttk.LabelFrame(self.root, text="Конфигурации")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Список конфигураций
        self.config_listbox = tk.Listbox(left_frame)
        self.config_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.config_listbox.bind("<<ListboxSelect>>", self.on_config_select)
        self.config_listbox.bind("<Button-3>", self.on_right_click)  # ПКМ для удаления
        self.update_config_list()

        # Кнопка для создания новой конфигурации (под списком)
        self.new_config_button = tk.Button(
            left_frame, text="Добавить конфигурацию", command=self.create_new_config
        )
        self.new_config_button.pack(fill=tk.X, padx=5, pady=5)

        # Кнопка для построения графиков (под списком)
        self.plot_button = tk.Button(
            left_frame, text="Построить графики", command=self.open_plot_window
        )
        self.plot_button.pack(fill=tk.X, padx=5, pady=5)

        # Правая панель: параметры конфигурации
        self.config_frame = ttk.LabelFrame(self.root, text="Параметры конфигурации")
        self.config_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Кнопки для запуска алгоритма и проверки размещения
        self.ga_button = tk.Button(
            self.config_frame, text="Запустить ГА", command=self.open_ga_console
        )
        self.ga_button.pack(side=tk.BOTTOM, pady=5)

        self.custom_layout_button = tk.Button(
            self.config_frame,
            text="Проверить размещение",
            command=self.check_custom_layout,
        )
        self.custom_layout_button.pack(side=tk.BOTTOM, pady=5)

        # Кнопка для открытия редактора компонентов
        self.component_editor_button = tk.Button(
            self.config_frame,
            text="Редактор компонентов",
            command=self.open_component_editor,
        )
        self.component_editor_button.pack(side=tk.BOTTOM, pady=5)

        # Отображение параметров конфигурации
        self.config_params_frame = ttk.Frame(self.config_frame)
        self.config_params_frame.pack(fill=tk.BOTH, expand=True)

        self.config_params_labels = {}
        self.update_config_params()

    def update_config_list(self):
        """Обновляет список конфигураций"""
        self.config_listbox.delete(0, tk.END)
        for config_name in self.config_manager.get_config_list():
            self.config_listbox.insert(tk.END, config_name)

    def create_new_config(self):
        """Создает новую конфигурацию"""
        new_config_name = (
            f"Конфигурация {len(self.config_manager.get_config_list()) + 1}"
        )
        self.config_manager.add_config(new_config_name)
        self.update_config_list()
        self.update_config_params()

    def on_config_select(self, event):
        """Обработчик выбора конфигурации"""
        self.update_config_params()

    def on_right_click(self, event):
        """Обработчик ПКМ для удаления конфигурации"""
        selected_config = self.config_listbox.get(tk.ACTIVE)
        if selected_config:
            self.config_manager.delete_config(selected_config)  # Измененная строка
            self.update_config_list()
            self.update_config_params()

    def update_config_params(self):
        """Обновляет отображение параметров конфигурации"""
        selected_config = self.config_listbox.get(tk.ACTIVE)
        if selected_config:
            config = self.config_manager.get_config(selected_config)
            if not isinstance(config, dict):
                messagebox.showerror("Ошибка", "Конфигурация должна быть словарём.")
                return

            for widget in self.config_params_frame.winfo_children():
                widget.destroy()

            row = 0
            for key, value in config.items():
                if key in ["components", "connections"]:
                    continue  # Пропускаем компоненты и соединения

                ttk.Label(self.config_params_frame, text=f"{key}:").grid(
                    row=row, column=0, sticky=tk.W
                )

                # Поле для ввода значения
                entry = ttk.Entry(self.config_params_frame)
                entry.insert(0, str(value))  # Вставляем значение по умолчанию
                entry.grid(row=row, column=1, sticky=tk.W)

                # Если значение по умолчанию, делаем текст серым
                entry.config(foreground="gray")
                entry.bind(
                    "<FocusIn>", lambda event, e=entry: self.on_entry_focus_in(e)
                )
                entry.bind(
                    "<FocusOut>",
                    lambda event, e=entry, k=key: self.on_entry_focus_out(e, k, config),
                )

                row += 1

    def on_entry_focus_in(self, entry):
        """Обработчик события фокуса на поле ввода"""
        if entry.get() == str(
            self.config_manager.get_config(self.config_listbox.get(tk.ACTIVE)).get(
                entry.cget("text").rstrip(":")
            )
        ):
            entry.delete(0, tk.END)
            entry.config(foreground="black")

    def on_entry_focus_out(self, entry, key, config):
        """Обработчик события потери фокуса на поле ввода"""
        if entry.get() == "":
            entry.insert(0, str(config[key]))
            entry.config(foreground="gray")
        else:
            # Обновляем значение в конфигурации
            try:
                if key in [
                    "board_width",
                    "board_height",
                    "population_size",
                    "generations",
                ]:
                    config[key] = int(entry.get())
                elif key in ["cxpb", "mutpb"]:
                    config[key] = float(entry.get())
                elif key in ["visualization_steps"]:
                    config[key] = list(map(int, entry.get().split(",")))
                else:
                    config[key] = entry.get()
            except ValueError:
                # Если ввод некорректен, восстанавливаем значение по умолчанию
                entry.delete(0, tk.END)
                entry.insert(0, str(config[key]))
                entry.config(foreground="gray")

    def __get_active_config(self) -> dict[str, Any] | None:
        selected_config = self.config_listbox.get(tk.ACTIVE)
        if selected_config:
            return self.config_manager.get_config(selected_config)

    def open_ga_console(self):
        """Открывает окно с консолью для запуска генетического алгоритма"""
        config = self.__get_active_config()
        if config:
            GAWindow(self.root, config)
        else:
            messagebox.showwarning("Необходимо выбрать конфиг")

    def __run_ga(
        self, config_name
    ):  # todo: удалить, если больше не будете использовать
        """Запускает генетический алгоритм и выводит результаты в консоль"""
        config = self.config_manager.get_config(config_name)
        ga = GAProcessorV2()

        def log(message):
            """Выводит сообщение в консоль"""
            self.console.insert(tk.END, message + "\n")
            self.console.see(tk.END)

        try:
            start_time = time.time()
            pop, self.fitness = ga.run(
                config
            )  # Передаем функцию log и шаги визуализации
            stop_time = time.time()
            log(f"\nФинальное поколение: {config['generations']}")
            log("Генетический алгоритм завершён.")
            log(f"Время выполнения: {stop_time - start_time}")
        except Exception as e:
            log(f"Ошибка: {str(e)}")

    def check_custom_layout(self):
        """Проверяет кастомное размещение"""
        selected_config = self.config_listbox.get(tk.ACTIVE)
        if selected_config:
            config = self.config_manager.get_config(selected_config)
            placements = []
            for i, comp in enumerate(config["components"]):
                x = random.randint(0, config["board_width"] - 1)
                y = random.randint(0, config["board_height"] - 1)
                rot = random.randint(0, 1)
                placements.extend([x, y, rot])
            messagebox.showinfo("Кастомное размещение", f"Размещение: {placements}")

    def open_plot_window(self):
        """Открывает окно для построения графиков"""
        # PlotWindow(
        #     parent=self.root, config_manager=self.config_manager, fitness=self.fitness
        # )
        config = self.__get_active_config()
        if config:
            plot = PlotWindow()
            plot.create_plot(config)

    def open_component_editor(self):
        """Открывает окно редактора компонентов"""
        config_name = self.config_listbox.get(tk.ACTIVE)
        config = self.__get_active_config()
        if config:
            ComponentEditor(self.root, self.config_manager, config, config_name)
