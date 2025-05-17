import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from src.application.config_manager.protocol import ConfigManagerProtocol
from src.application.genetic_algorithm.protocol import GAProcessorProtocol
from src.utils.types import Config


class GAWindow:

    def __init__(
        self,
        parent: tk.Tk,
        config_manager: ConfigManagerProtocol,
        processor: GAProcessorProtocol,
        config: Config,
        config_name: str,
    ):
        self.__config = config
        self.__config_name = config_name
        self.__processor = processor
        self.__config_manager = config_manager
        self._window = tk.Toplevel(parent)
        self.__root = parent
        self._window.title("Запуск генетического алгоритма")
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Создает интерфейс окна"""
        ttk.Label(self._window, text="Параметры ГА").pack(pady=10)
        ttk.Button(self._window, text="Запустить", command=self._run_ga).pack(pady=10)

    def _log(self, message: str) -> None:
        """Выводит сообщение в консоль"""
        self.__console.insert(tk.END, message + "\n")
        self.__console.see(tk.END)

    def _create_console(self) -> None:
        """Открывает окно с консолью для запуска генетического алгоритма"""
        ga_console = tk.Toplevel(self.__root)
        ga_console.title("Размещение элементов")
        ga_console.geometry(
            f"{self.__config['board_width'] * 30}x{self.__config['board_height'] * 30}"
        )  # Размер окна зависит от платы

        # Консоль для вывода
        self.__console = scrolledtext.ScrolledText(
            ga_console, wrap=tk.WORD, font=("Courier", 10)
        )
        self.__console.pack(fill=tk.BOTH, expand=True)

    def _run_ga(self) -> None:
        """Запускает генетический алгоритм"""
        self._create_console()

        try:
            start_time = time.perf_counter()
            pop, fitness = self.__processor.run(self.__config)
            stop_time = time.perf_counter()
            self._log(f"\nФинальное поколение: {self.__config['generations']}")
            self._log("Генетический алгоритм завершён.")
            self._log(f"Время выполнения: {round(stop_time - start_time, 4)}с")
            self._log(f"\nРезультат: {pop, fitness}")
            self.__config["fitness"] = fitness
            self.__config_manager.update_config(self.__config_name, self.__config)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
