import tkinter as tk
from tkinter import messagebox, ttk

from src.application.genetic_algorithm.protocol import GAProcessorProtocol


class GAWindow:
    def __init__(self, parent: tk.Tk, config, processor: GAProcessorProtocol):
        self.__config = config
        self.__processor = processor
        self._window = tk.Toplevel(parent)
        self._window.title("Запуск генетического алгоритма")
        self._create_widgets()

    def _create_widgets(self):
        """Создает интерфейс окна"""
        ttk.Label(self._window, text="Параметры ГА").pack(pady=10)
        ttk.Button(self._window, text="Запустить", command=self._run_ga).pack(pady=10)

    def _run_ga(self):
        """Запускает генетический алгоритм"""
        try:
            pop, log = self.__processor.run(self.__config)
            print("Результат:", pop, log)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
