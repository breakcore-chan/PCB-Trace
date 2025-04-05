import json
import os


class ConfigManager:
    def __init__(self):
        self.configs = {}
        self.load_configs()

    def add_config(self, name, config=None):
        """Добавляет новую конфигурацию с компонентами и соединениями"""
        if config is None:
            config = {
                "board_width": 20,
                "board_height": 20,
                "population_size": 50,
                "generations": 10000,
                "visualization_steps": [10, 50, 100, 200, 500, 1000, 5000, 10000],
                "cxpb": 0.7,
                "mutpb": 0.2,
                "components": [],  # Список компонентов: [{"width": int, "height": int}, ...]
                "connections": [],  # Список соединений: [(int, int), ...]
            }
        self.configs[name] = config
        self.save_configs()

    def get_config(self, name):
        """Возвращает конфигурацию по имени, включая компоненты и соединения"""
        return self.configs.get(name)

    def get_config_names(self):
        """Возвращает список имен всех конфигураций"""
        return list(self.configs.keys())

    # TODO 1 json = 1 конфигурация
    def save_configs(self):
        """Сохраняет конфигурации в JSON, включая компоненты и соединения"""
        with open("configs.json", "w", encoding="utf-8") as f:
            json.dump(self.configs, f, ensure_ascii=False, indent=4)

    # TODO если нет файла сообщить об этом
    def load_configs(self):
        """Загружает конфигурации из JSON, включая компоненты и соединения"""
        if os.path.exists("configs.json"):
            with open("configs.json", "r", encoding="utf-8") as f:
                self.configs = json.load(f)
                # Проверяем, что у всех конфигураций есть поля components и connections
                for config in self.configs.values():
                    if "components" not in config:
                        config["components"] = []
                    if "connections" not in config:
                        config["connections"] = []

    def update_config(self, name, new_config):
        """Обновляет существующую конфигурацию"""
        if name in self.configs:
            self.configs[name].update(new_config)
            self.save_configs()
