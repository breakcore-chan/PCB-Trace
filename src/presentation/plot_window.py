import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils.base_config import base_config


class PlotWindow:
    def __init__(self, parent, config_manager, fitness: list):
        self.config_manager = config_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Графики")
        self.fitness = fitness
        self.create_widgets()

    def create_widgets(self):
        """Создает интерфейс окна"""
        fig, ax = plt.subplots()
        for config_name in self.config_manager.get_config_names():
            print(base_config.VISUALIZATION_STEPS, self.fitness)
            ax.plot(base_config.VISUALIZATION_STEPS, self.fitness, label=config_name)
        ax.legend()
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
