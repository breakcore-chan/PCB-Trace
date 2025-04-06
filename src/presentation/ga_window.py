import tkinter as tk
from tkinter import messagebox, ttk

from gen_alg.genetic_algorithm import GeneticAlgorithm


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
            ga = GeneticAlgorithm(self.config)
            pop, log = ga.run()
            print("Результат:", pop, log)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
