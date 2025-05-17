import matplotlib.pyplot as plt


# TODO добавить сохранение графиков в файл, возможно сделать менеджер графиков сродни менеджеру конфигов
class PlotWindow:

    def create_plot(self, config: dict | list[dict]) -> None:
        if type(config) is list:
            for func in config:
                plt.plot(
                    func["visualization_steps"],
                    func["fitness"],
                    label=f"cxpb: {func['cxpb']} ; mutpb: {func['mutpb']} ; indpb: {func['indpb']} ; seed: {func['seed']}",
                )
        else:
            plt.plot(
                config["visualization_steps"],
                config["fitness"],
                label=f"cxpb: {config['cxpb']} ; mutpb: {config['mutpb']} ; indpb: {config['indpb']} ; seed: {config['seed']}",
            )
        plt.legend()
        plt.title("График зависимости fitness от итерации")
        plt.xlabel("Поколение")
        plt.ylabel("Функция приспособленности")
        plt.show()
