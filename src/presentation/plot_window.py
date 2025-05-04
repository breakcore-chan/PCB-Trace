import matplotlib.pyplot as plt


class PlotWindow:
    def __init__(self, config: dict):
        self.config = config

    def create_widgets(self):
        plt.plot(
            self.config["visualization_steps"],
            self.config["fitness"],
        )
        plt.title("График зависимости fitness от итерации")
        plt.xlabel("Поколение")
        plt.ylabel("Функция приспособленности")
        plt.show()
