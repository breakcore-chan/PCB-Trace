import tkinter as tk
from tkinter import ttk

from pathlib import Path
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from src.utils.types import Config
from src.utils.environments import PLOT_DIR


# TODO добавить сохранение графиков в файл, возможно сделать менеджер графиков сродни менеджеру конфигов
class PlotWindow:
    def __init__(
        self, root: tk.Tk, config: Config | list[Config], config_name: str
    ) -> None:
        root.title("Графики")
        self.__config_name = config_name

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

        button = ttk.Button(top_level, text="Сохранить график", command=self._save_plot)
        button.pack()

        # Начальный график
        self._create_plot(config)

    def _create_plot(self, config: dict | list[dict]) -> None:
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
                label=f"cxpb: {config['cxpb']} ; mutpb: {config['mutpb']} ; indpb: {config['indpb']} ; seed: {config['seed']}",
            )
        self.__ax.legend()
        self.__ax.set_title("График зависимости fitness от итерации")
        self.__ax.set_xlabel("Поколение")
        self.__ax.set_ylabel("Функция приспособленности")
        self.__canvas.draw()

    def _save_plot(self) -> None:
        target_dir = PLOT_DIR / Path(self.__config_name).stem
        target_dir.mkdir(exist_ok=True)
        self.__fig.savefig(target_dir / "plot.png")
