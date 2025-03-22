import json
import os

class ConfigManager:
    def __init__(self):
        self.configs = {}
        self.load_configs()

    def add_config(self, name, config=None):
        """Добавляет новую конфигурацию"""
        if config is None:
            config = {
                "board_width": 20,
                "board_height": 20,
                "population_size": 50,
                "generations": 1000,
                "visualization_steps": [10, 50, 100, 200, 500, 1000],
                "cxpb": 0.7,
                "mutpb": 0.2,
                "components": [],
                "connections": []
            }
        self.configs[name] = config
        self.save_configs()

    def get_config(self, name):
        """Возвращает конфигурацию по имени"""
        return self.configs.get(name)

    def get_config_names(self):
        """Возвращает список имен конфигураций"""
        return list(self.configs.keys())

    def save_configs(self):
        """Сохраняет конфигурации в файл"""
        with open("configs.json", "w") as f:
            json.dump(self.configs, f)

    def load_configs(self):
        """Загружает конфигурации из файла"""
        if os.path.exists("configs.json"):
            with open("configs.json", "r") as f:
                self.configs = json.load(f)