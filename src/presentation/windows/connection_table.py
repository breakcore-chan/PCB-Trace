import tkinter as tk
from tkinter import ttk
from typing import Any

from src.application.config_manager.protocol import ConfigManagerProtocol


class ConnectionTable:
    def __init__(
        self,
        parent,
        config_manager: ConfigManagerProtocol,
        config: dict[str, Any],
        config_name: str,
    ) -> None:
        self.__config_name = config_name
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
        if num_components == 0:
            return

        self.connection_buttons = [
            [None for _ in range(num_components)] for _ in range(num_components)
        ]

        # Заголовки для строк и столбцов
        for i in range(num_components):
            ttk.Label(self.connection_frame, text=f"C{i + 1}").grid(row=i + 1, column=0)
            ttk.Label(self.connection_frame, text=f"C{i + 1}").grid(row=0, column=i + 1)

        # Кнопки для соединений
        for i in range(num_components):
            for j in range(num_components):
                if i == j:
                    btn = ttk.Button(self.connection_frame, text="X", state=tk.DISABLED)
                else:
                    is_connected = any(
                        (a == i and b == j) or (a == j and b == i)
                        for (a, b) in self.config.get("connections", [])
                    )
                    btn_text = "✓" if is_connected else " "
                    btn = ttk.Button(
                        self.connection_frame,
                        text=btn_text,
                        command=lambda i=i, j=j: self.toggle_connection(i, j),
                    )
                btn.grid(row=i + 1, column=j + 1)
                self.connection_buttons[i][j] = btn

    def toggle_connection(self, i, j):
        """Переключает соединение между компонентами"""
        connections = self.config.setdefault("connections", [])
        connection_exists = any(
            (a == i and b == j) or (a == j and b == i) for (a, b) in connections
        )

        if connection_exists:
            self.config["connections"] = [
                (a, b)
                for (a, b) in connections
                if not ((a == i and b == j) or (a == j and b == i))
            ]
            self.connection_buttons[i][j].config(text=" ")
            self.connection_buttons[j][i].config(text=" ")
        else:
            if i < j:
                self.config["connections"].append((i, j))
            else:
                self.config["connections"].append((j, i))
            self.connection_buttons[i][j].config(text="✓")
            self.connection_buttons[j][i].config(text="✓")

        # Сохраняем изменения
        self.config_manager.update_config(self.__config_name, self.config)

    def on_done(self):
        """Закрывает окно"""
        self.window.destroy()
