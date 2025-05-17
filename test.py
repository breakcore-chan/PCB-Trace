from src.gen_alg.genetic_algorithm_new import GeneticAlgorithm
from src.presentation.plot_window import PlotWindow
from src.utils.config_manager_new import ConfigManager

config_manager = ConfigManager()
genetic_algotithm = GeneticAlgorithm()
pw = PlotWindow()

graphics = []
for i in range(11):
    # config_manager.create(name=str(i))
    cnf = config_manager.read_by_name(name=str(i))
    cnf["fitness"] = genetic_algotithm.run(config=cnf)[1]
    config_manager.update(name=str(i), config=cnf)
    graphics.append(cnf)

pw.create_plot(config=graphics)
