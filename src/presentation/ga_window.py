import tkinter as tk
from tkinter import messagebox, ttk

from src.application.genetic_algorithm.processor_v2 import GAProcessorV2


class GAWindow:
    def __init__(self, parent, config):
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("Запуск генетического алгоритма")
        self.create_widgets()

    def create_widgets(self):
        """Создает интерфейс окна"""
        ttk.Label(self.window, text="Параметры ГА").pack(pady=10)
        ttk.Button(self.window, text="Запустить", command=self.run_ga).pack(pady=10)

    def run_ga(self):
        """Запускает генетический алгоритм"""
        try:
            ga = GAProcessorV2()
            pop, log = ga.run(self.config)
            print("Результат:", pop, log)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
