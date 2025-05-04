from src.gen_alg.genetic_algorithm_new import GeneticAlgorithm
from src.presentation.plot_window import PlotWindow
from src.utils.config_manager_new import ConfigManager

cm = ConfigManager()
ga = GeneticAlgorithm(cm.read_by_name(name="config1"))


cnf = cm.read_by_name(name="test")
cnf["fitness"] = ga.run()[1]
cm.update(name="test", config=cnf)
print(cm.read_by_name(name="test"))
# print(len(ga.run()[0]), len(ga.run()[1]))
pw = PlotWindow(cm.read_by_name(name="test"))
pw.create_widgets()
