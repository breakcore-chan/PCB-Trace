import json
import os
import re

from environments import CONFIGS_DIR
from src.utils.base_config import base_config


class ConfigManager:
    def __init__(self):
        pass

    def _get_next_config_number(self):
        pattern = r"^\d+\.json$"
        existing = [
            int(num.split(".")[0])
            for num in os.listdir(CONFIGS_DIR)
            if re.fullmatch(pattern=pattern, string=num)
        ]
        return max(existing) + 1

    def create(self, name: str = "", config: dict = None) -> None:
        if name != "":
            filename = f"{name}.json"
        else:
            filename = f"{self._get_next_config_number()}.json"

        filepath = os.path.join(CONFIGS_DIR, filename)
        config = base_config if config is None else config

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False)

    def read_by_name(self, name: str) -> dict | str:
        filepath = os.path.join(CONFIGS_DIR, f"{name}.json")
        try:
            with open(filepath, "r") as file:
                return json.loads(file.read())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return e

    def read_all(self) -> list[dict] | str:
        configs_list = []
        for name in os.listdir(CONFIGS_DIR):
            try:
                filepath = os.path.join(CONFIGS_DIR, f"{name}.json")
                with open(filepath, "r") as file:
                    configs_list.append(json.loads(file.read()))
            except (
                IsADirectoryError,
                json.JSONDecodeError,
            ):  # Если в директории с конфиками директория - пропуск
                pass
        return configs_list

    def read_all_names(self) -> list[str] | str:
        try:
            return os.listdir(CONFIGS_DIR)
        except ... as e:
            return e

    def update(self, name: str, config: dict) -> None | str:
        try:
            if f"{name}.json" not in os.listdir(CONFIGS_DIR):
                raise FileNotFoundError
        except FileExistsError as e:
            return e
        try:
            filepath = os.path.join(CONFIGS_DIR, f"{name}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False)
        except json.JSONDecodeError as e:
            return e

    def delete(self, name: str) -> None | str:
        try:
            if f"{name}.json" not in os.listdir(CONFIGS_DIR):
                raise FileNotFoundError
        except FileExistsError as e:
            return e

        filepath = os.path.join(CONFIGS_DIR, f"{name}.json")

        try:
            os.remove(filepath)
        except ... as e:
            return e
