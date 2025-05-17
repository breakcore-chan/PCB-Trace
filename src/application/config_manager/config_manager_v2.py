import uuid
import json
import os

from pathlib import Path
from typing import Any
from src.utils.environments import CONFIGS_DIR
from src.application.config_manager.protocol import ConfigManagerProtocol
from src.utils.base_config import base_config
from src.utils.exceptions import InternalError


class ConfigManagerV2(ConfigManagerProtocol):
    def add_config(self, name: str = "", config: dict | None = None) -> None:
        if not name:
            filename = f"{name}.json"
        else:
            filename = f"{uuid.uuid4()}.json"

        filepath = os.path.join(CONFIGS_DIR, filename)
        config = base_config if config is None else config

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False)

    def get_config(self, name: str) -> dict[str, Any]:
        filepath = Path(os.path.join(CONFIGS_DIR, name))
        if not filepath.exists():
            raise InternalError(f"Filepath {filepath} doesn't exist")

        with open(filepath, "r", encoding="utf-8") as file:
            config = json.load(file)
        return config

    def get_config_list(self) -> list[str]:
        try:
            return os.listdir(CONFIGS_DIR)
        except Exception as e:
            raise InternalError(str(e))

    def update_config(self, name: str, new_config: dict) -> None | str:
        if name not in os.listdir(CONFIGS_DIR):
            raise InternalError(f"File {name} doesn't exist")
        try:
            filepath = os.path.join(CONFIGS_DIR, name)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(new_config, f, ensure_ascii=False)
        except json.JSONDecodeError as e:
            return e

    def delete_config(self, name: str) -> None:
        if name not in os.listdir(CONFIGS_DIR):
            raise InternalError(f"Filepath {name} doesn't exist")

        filepath = os.path.join(CONFIGS_DIR, f"{name}.json")
        try:
            os.remove(filepath)
        except Exception as e:
            raise InternalError(e)

    @staticmethod
    def read_by_name(name: str) -> dict | str:
        filepath = os.path.join(CONFIGS_DIR, f"{name}.json")
        try:
            with open(filepath, "r") as file:
                return json.loads(file.read())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return str(e)
