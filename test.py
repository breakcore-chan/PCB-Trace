from gen_alg.genetic_algorithm_new import GeneticAlgorithm
from src.utils.config_manager_new import ConfigManager

cm = ConfigManager()
ga = GeneticAlgorithm(cm.read_dy_name(name="config1"))
print(len(ga.run()[0]), len(ga.run()[1]))
