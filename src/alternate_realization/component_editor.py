import tkinter as tk
from tkinter import ttk

class ComponentEditor:
    def __init__(self, parent, config_manager, config):
        self.config_manager = config_manager
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("Редактор компонентов и соединений")
        self.create_widgets()

    def create_widgets(self):
        """Создает интерфейс окна"""
        # Панель для добавления компонентов
        self.component_frame = ttk.LabelFrame(self.window, text="Добавление компонентов")
        self.component_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Список компонентов
        self.component_listbox = tk.Listbox(self.component_frame)
        self.component_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.update_component_list()

        # Поля для добавления нового компонента
        self.new_component_frame = ttk.Frame(self.component_frame)
        self.new_component_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(self.new_component_frame, text="Ширина:").grid(row=0, column=0)
        self.width_entry = ttk.Entry(self.new_component_frame)
        self.width_entry.insert(0, "1")
        self.width_entry.grid(row=0, column=1)

        ttk.Label(self.new_component_frame, text="Высота:").grid(row=0, column=2)
        self.height_entry = ttk.Entry(self.new_component_frame)
        self.height_entry.insert(0, "1")
        self.height_entry.grid(row=0, column=3)

        self.add_component_button = tk.Button(self.new_component_frame, text="Добавить", command=self.add_component)
        self.add_component_button.grid(row=0, column=4, padx=5)

        # Кнопка "Готово" для перехода к таблице соединений
        self.done_button = tk.Button(self.component_frame, text="Готово", command=self.open_connection_table)
        self.done_button.pack(fill=tk.X, padx=5, pady=5)

    def add_component(self):
        """Добавляет новый компонент"""
        width = int(self.width_entry.get())
        height = int(self.height_entry.get())

        if width > 0 and height > 0:
            # Автоматическое именование компонентов (C1, C2, C3, ...)
            component_name = f"C{len(self.config['components']) + 1}"
            self.config["components"].append({"width": width, "height": height})
            self.update_component_list()
            self.width_entry.delete(0, tk.END)
            self.height_entry.delete(0, tk.END)
            self.width_entry.insert(0, "1")
            self.height_entry.insert(0, "1")

    def update_component_list(self):
        """Обновляет список компонентов"""
        self.component_listbox.delete(0, tk.END)
        for i, comp in enumerate(self.config["components"]):
            self.component_listbox.insert(tk.END, f"C{i + 1} ({comp['width']}x{comp['height']})")

    def open_connection_table(self):
        """Открывает окно с таблицей соединений и сохраняет конфигурацию"""
        self.config_manager.save_configs()  # Сохраняем компоненты перед переходом
        self.window.destroy()
        ConnectionTable(self.window.master, self.config_manager, self.config)  # Передаем config_manager


class ConnectionTable:
    def __init__(self, parent, config_manager, config):
        self.config_manager = config_manager
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("Таблица соединений")
        self.create_widgets()

    def create_widgets(self):
        """Создает интерфейс окна"""
        # Панель для таблицы соединений
        self.connection_frame = ttk.LabelFrame(self.window, text="Соединения")
        self.connection_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаем таблицу соединений
        self.connection_buttons = []
        self.create_connection_table()

        # Кнопка "Готово" для закрытия окна
        self.done_button = tk.Button(self.window, text="Готово", command=self.on_done)
        self.done_button.pack(fill=tk.X, padx=5, pady=5)

    def create_connection_table(self):
        """Создает таблицу соединений с загрузкой существующих соединений"""
        num_components = len(self.config["components"])
        self.connection_buttons = [[None for _ in range(num_components)] for _ in range(num_components)]

        # Заголовки для строк и столбцов
        for i in range(num_components):
            ttk.Label(self.connection_frame, text=f"C{i+1}").grid(row=i+1, column=0)
            ttk.Label(self.connection_frame, text=f"C{i+1}").grid(row=0, column=i+1)

        # Кнопки для соединений
        for i in range(num_components):
            for j in range(num_components):
                if i == j:
                    # Диагональные кнопки недоступны
                    btn = ttk.Button(self.connection_frame, text="X", state=tk.DISABLED)
                else:
                    # Проверяем, есть ли соединение (i,j) или (j,i)
                    is_connected = any(
                        (a == i and b == j) or (a == j and b == i)
                        for (a, b) in self.config["connections"]
                    )
                    btn_text = "✓" if is_connected else " "
                    btn = ttk.Button(
                        self.connection_frame,
                        text=btn_text,
                        command=lambda i=i, j=j: self.toggle_connection(i, j)
                    )
                btn.grid(row=i+1, column=j+1)
                self.connection_buttons[i][j] = btn

    def toggle_connection(self, i, j):
        """Переключает соединение между компонентами, избегая дубликатов"""
        # Проверяем наличие соединения в любом порядке
        connection_exists = any(
            (a == i and b == j) or (a == j and b == i)
            for (a, b) in self.config["connections"]
        )
        
        if connection_exists:
            # Удаляем оба варианта соединения если существуют
            self.config["connections"] = [
                (a, b) for (a, b) in self.config["connections"]
                if not ((a == i and b == j) or (a == j and b == i))
            ]
            self.connection_buttons[i][j].config(text=" ")
            self.connection_buttons[j][i].config(text=" ")
        else:
            # Добавляем только один вариант (i,j) где i < j
            if i < j:
                self.config["connections"].append((i, j))
            else:
                self.config["connections"].append((j, i))
            self.connection_buttons[i][j].config(text="✓")
            self.connection_buttons[j][i].config(text="✓")
        
        # Сохраняем изменения
        self.config_manager.save_configs()

    def update_connection_buttons(self):
        """Обновляет все кнопки соединений на основе config["connections"]"""
        for i in range(len(self.config["components"])):
            for j in range(len(self.config["components"])):
                if i == j:
                    continue
                if any((a, b) == (i, j) or (a, b) == (j, i) for (a, b) in self.config["connections"]):
                    self.connection_buttons[i][j].config(text="✓")
                else:
                    self.connection_buttons[i][j].config(text=" ")

    def on_done(self):
            """Сохраняет конфигурацию и закрывает окно"""
            self.config_manager.save_configs()  # Сохраняем соединения
            self.window.destroy()