import random
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from src.gen_alg.genetic_algorithm import GeneticAlgorithm
from src.presentation.component_editor import ComponentEditor
from src.presentation.plot_window import PlotWindow
from src.utils.config_manager import ConfigManager

# Параметры конфигурации по умолчанию
BOARD_WIDTH = 20
BOARD_HEIGHT = 20
POPULATION_SIZE = 50
GENERATIONS = 10000
CXPB = 0.7
MUTPB = 0.2
VISUALIZATION_STEPS = [10, 50, 100, 200, 500, 1000, 5000, 10000]


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конфигурации для размещения элементов")
        self.config_manager = ConfigManager()

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
        for config_name in self.config_manager.get_config_names():
            self.config_listbox.insert(tk.END, config_name)

    def create_new_config(self):
        """Создает новую конфигурацию"""
        new_config_name = f"Конфигурация {len(self.config_manager.configs) + 1}"
        self.config_manager.add_config(
            new_config_name,
            {
                "board_width": BOARD_WIDTH,
                "board_height": BOARD_HEIGHT,
                "population_size": POPULATION_SIZE,
                "generations": GENERATIONS,
                "visualization_steps": VISUALIZATION_STEPS,
                "cxpb": CXPB,
                "mutpb": MUTPB,
                "components": [],
                "connections": [],
            },
        )
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

    def open_ga_console(self):
        """Открывает окно с консолью для запуска генетического алгоритма"""
        selected_config = self.config_listbox.get(tk.ACTIVE)
        if selected_config:
            config = self.config_manager.get_config(selected_config)
            ga_console = tk.Toplevel(self.root)
            ga_console.title("Размещение элементов")
            ga_console.geometry(
                f"{config['board_width'] * 30}x{config['board_height'] * 30}"
            )  # Размер окна зависит от платы

            # Консоль для вывода
            self.console = scrolledtext.ScrolledText(
                ga_console, wrap=tk.WORD, font=("Courier", 10)
            )
            self.console.pack(fill=tk.BOTH, expand=True)

            # Запуск генетического алгоритма
            self.run_ga(selected_config)

    def run_ga(self, config_name):
        """Запускает генетический алгоритм и выводит результаты в консоль"""
        config = self.config_manager.get_config(config_name)
        ga = GeneticAlgorithm(config)

        def log(message):
            """Выводит сообщение в консоль"""
            self.console.insert(tk.END, message + "\n")
            self.console.see(tk.END)

        try:
            pop, logbook = ga.run(
                log, config["visualization_steps"]
            )  # Передаем функцию log и шаги визуализации
            log(f"\nФинальное поколение: {config['generations']}")
            log("Генетический алгоритм завершён.")
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
        PlotWindow(self.root, self.config_manager)

    def open_component_editor(self):
        """Открывает окно редактора компонентов"""
        selected_config = self.config_listbox.get(tk.ACTIVE)
        if selected_config:
            config = self.config_manager.get_config(selected_config)
            # Передаем config_manager в ComponentEditor
            ComponentEditor(self.root, self.config_manager, config)
