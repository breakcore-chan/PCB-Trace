from src.application.genetic_algorithm.processor_v2 import GAProcessorV2
from src.presentation.plot_window import PlotWindow
from src.application.config_manager.config_manager_v2 import ConfigManagerV2

config_manager = ConfigManagerV2()
genetic_algotithm = GAProcessorV2()
pw = PlotWindow()

graphics = []
for i in range(11):
    # config_manager.create(name=str(i))
    cnf = config_manager.read_by_name(name=str(i))
    cnf["fitness"] = genetic_algotithm.run(config=cnf)[1]
    config_manager.update_config(name=f"{i}.json", new_config=cnf)
    graphics.append(cnf)

pw.create_plot(config=graphics)
