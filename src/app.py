import tkinter as tk

from src.application.config_manager.config_manager_v2 import ConfigManagerV2
from src.application.genetic_algorithm.processor_v2 import GAProcessorV2
from src.presentation.core import FrontApp


class GAProcessApplication:
    def __init__(self) -> None:
        self.__tkinter_app = tk.Tk()
        self.__config_manager = ConfigManagerV2()
        self.__processor = GAProcessorV2()
        self.__frontend = FrontApp(
            self.__tkinter_app, self.__processor, self.__config_manager
        )

    def run(self) -> None:
        self.__frontend.run()
