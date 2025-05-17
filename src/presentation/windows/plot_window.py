import tkinter as tk
import uuid
from pathlib import Path
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.utils.environments import PLOT_DIR
from src.utils.types import Config


# TODO добавить сохранение графиков в файл, возможно сделать менеджер графиков сродни менеджеру конфигов
class PlotWindow:
    def __init__(self, root: tk.Tk) -> None:
        root.title("Графики")

        # Создаем фрейм для графика
        top_level = tk.Toplevel(root)
        frame = ttk.Frame(top_level)
        frame.pack(fill=tk.BOTH, expand=True)

        # Создаем фигуру Matplotlib
        self.__fig = Figure()
        self.__ax = self.__fig.add_subplot(111)

        # Создаем холст Tkinter для Matplotlib
        self.__canvas = FigureCanvasTkAgg(self.__fig, master=frame)
        self.__canvas.draw()
        self.__canvas_widget = self.__canvas.get_tk_widget()
        self.__canvas_widget.pack(fill=tk.BOTH, expand=True)

        ttk.Label(top_level, text="Название графика:").pack()
        self.__amplitude_entry = ttk.Entry(top_level)
        self.__amplitude_entry.insert(0, str(uuid.uuid4()))
        self.__amplitude_entry.pack()

        button = ttk.Button(top_level, text="Сохранить график", command=self._save_plot)
        button.pack()
        button = ttk.Button(top_level, text="Очистить графики", command=self._clear_fig)
        button.pack()

    def create_plot(self, config: dict | list[dict], config_name: str) -> None:
        if isinstance(config, list):
            for func in config:
                self.__ax.plot(
                    func["visualization_steps"],
                    func["fitness"],
                    label=f"cxpb: {func['cxpb']} ; mutpb: {func['mutpb']} ; indpb: {func['indpb']} ; seed: {func['seed']}",
                )
        else:
            self.__ax.plot(
                config["visualization_steps"],
                config["fitness"],
                label=f"{config_name} | cxpb: {config['cxpb']} ; mutpb: {config['mutpb']} ; indpb: {config['indpb']} ; seed: {config['seed']}",
            )
        self.__ax.legend()
        self.__ax.set_title("График зависимости fitness от итерации")
        self.__ax.set_xlabel("Поколение")
        self.__ax.set_ylabel("Функция приспособленности")
        self.__canvas.draw()

    def _clear_fig(self) -> None:
        self.__ax.clear()
        self.__canvas.draw()

    def _save_plot(self) -> None:
        target_file = PLOT_DIR / f"{self.__amplitude_entry.get()}.png"
        self.__fig.savefig(target_file)
