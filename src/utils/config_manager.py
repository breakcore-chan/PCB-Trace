import json
import os

CONFIGS_DIR = os.path.join("src", "configs")
os.makedirs(CONFIGS_DIR, exist_ok=True)


class ConfigManager:
    def __init__(self):
        self.configs = {}
        self.load_configs()

    def _get_next_config_number(self):
        """Находит минимальный свободный номер для нового конфига"""
        existing = []
        for f in os.listdir(CONFIGS_DIR):
            if f.startswith("config") and f.endswith(".json"):
                try:
                    num = int(f[6:-5])  # Извлекаем число между "config" и ".json"
                    existing.append(num)
                except ValueError:
                    continue  # Пропускаем файлы с некорректными именами
        return min(set(range(1, max(existing or [0]) + 2)) - set(existing))

    def add_config(self, name, config=None):
        """Добавляет новую конфигурацию в отдельный файл"""
        config_number = self._get_next_config_number()
        filename = os.path.join(CONFIGS_DIR, f"config{config_number}.json")
        
        default_config = {
            "board_width": 20,
            "board_height": 20,
            "population_size": 50,
            "generations": 10000,
            "visualization_steps": [10, 50, 100, 200, 500, 1000, 5000, 10000],
            "cxpb": 0.7,
            "mutpb": 0.2,
            "components": [],
            "connections": [],
        }
        
        self.configs[name] = default_config if config is None else config
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({name: self.configs[name]}, f, ensure_ascii=False, indent=4)
        self.load_configs()

    def get_config(self, name):
        """Возвращает конфигурацию по имени, включая компоненты и соединения"""
        return self.configs.get(name)

    def get_config_names(self):
        """Возвращает список имен всех конфигураций"""
        return list(self.configs.keys())

    def save_configs(self):
        """Сохраняет все конфигурации (для обратной совместимости)"""
        # В новой реализации это не нужно, так как каждая конфигурация сохраняется отдельно
        pass

    def load_configs(self):
        """Загружает все конфигурации из папки"""
        self.configs = {}
        for filename in os.listdir(CONFIGS_DIR):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(CONFIGS_DIR, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.configs.update(data)
                except json.JSONDecodeError:
                    continue  # Пропускаем битые JSON-файлы

    def update_config(self, name, new_config):
        """Обновляет существующую конфигурацию"""
        if name in self.configs:
            self.configs[name].update(new_config)
            # Находим и обновляем соответствующий файл
            for filename in os.listdir(CONFIGS_DIR):
                filepath = os.path.join(CONFIGS_DIR, filename)
                try:
                    with open(filepath, "r+", encoding="utf-8") as f:
                        data = json.load(f)
                        if name in data:
                            data[name] = self.configs[name]
                            f.seek(0)
                            f.truncate()
                            json.dump(data, f, ensure_ascii=False, indent=4)
                except (json.JSONDecodeError, PermissionError):
                    continue

    def delete_config(self, name):
        """Удаляет конфигурацию и соответствующий файл"""
        files_to_delete = []
        for filename in os.listdir(CONFIGS_DIR):
            filepath = os.path.join(CONFIGS_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if name in data:
                        files_to_delete.append(filepath)
            except (json.JSONDecodeError, PermissionError):
                continue
        
        # Удаление файлов после закрытия всех дескрипторов
        for filepath in files_to_delete:
            try:
                os.remove(filepath)
            except PermissionError:
                continue
        self.load_configs()