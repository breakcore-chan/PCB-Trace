import tkinter as tk
from tkinter import ttk
from typing import Any

from src.application.config_manager.protocol import ConfigManagerProtocol
from src.presentation.windows.connection_table import ConnectionTable


class ComponentEditor:
    def __init__(
        self,
        parent: tk.Tk,
        config_manager: ConfigManagerProtocol,
        config: dict[str, Any],
        config_name: str,
    ) -> None:
        self.config_manager = config_manager
        self.config = config
        self.__config_name = config_name
        self.window = tk.Toplevel(parent)
        self.window.title("Редактор компонентов и соединений")
        self.create_widgets()

    def create_widgets(self):
        """Создает интерфейс окна"""
        # Панель для добавления компонентов
        self.component_frame = ttk.LabelFrame(
            self.window, text="Добавление компонентов"
        )
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

        self.add_component_button = tk.Button(
            self.new_component_frame, text="Добавить", command=self.add_component
        )
        self.add_component_button.grid(row=0, column=4, padx=5)

        # Кнопка "Готово" для перехода к таблице соединений
        self.done_button = tk.Button(
            self.component_frame, text="Готово", command=self.open_connection_table
        )
        self.done_button.pack(fill=tk.X, padx=5, pady=5)

    def add_component(self):
        """Добавляет новый компонент"""
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())

            if width > 0 and height > 0:
                self.config["components"].append({"width": width, "height": height})
                self.update_component_list()
                self.width_entry.delete(0, tk.END)
                self.height_entry.delete(0, tk.END)
                self.width_entry.insert(0, "1")
                self.height_entry.insert(0, "1")
        except ValueError:
            pass

    def update_component_list(self):
        """Обновляет список компонентов"""
        self.component_listbox.delete(0, tk.END)
        for i, comp in enumerate(self.config["components"]):
            self.component_listbox.insert(
                tk.END, f"C{i + 1} ({comp['width']}x{comp['height']})"
            )

    def open_connection_table(self):
        """Открывает окно с таблицей соединений"""
        # Сохраняем изменения компонентов
        self.config_manager.update_config(self.__config_name, self.config)
        self.window.destroy()
        ConnectionTable(
            self.window.master, self.config_manager, self.config, self.__config_name
        )
