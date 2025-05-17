import os
import shutil
import uuid
from pathlib import Path

import orjson
from pydantic import ValidationError

from src.application.config_manager.protocol import ConfigManagerProtocol
from src.utils.environments import CONFIGS_DIR
from src.utils.exceptions import InternalError, WrongFileFormat
from src.utils.types import BASE_CONFIG, Config, config_type_checker


class ConfigManagerV2(ConfigManagerProtocol):
    def add_config(self, name: str = "", config: Config | None = None) -> None:
        if name:
            filename = f"{name}.json"
        else:
            filename = f"{uuid.uuid4()}.json"

        filepath = (CONFIGS_DIR / filename).resolve()
        config = BASE_CONFIG if config is None else config

        with open(filepath, "wb") as file:
            file.write(orjson.dumps(config))

    def add_config_from_path(self, path: str) -> None:
        file_path = Path(path).resolve()
        try:
            with open(file_path, "rb") as file:
                config_type_checker.validate_python(orjson.loads(file.read()))
        except ValidationError:
            raise WrongFileFormat
        target_path = CONFIGS_DIR / f"{file_path.stem}.json"
        k = 1
        while target_path.exists():
            target_path = CONFIGS_DIR / f"{file_path.stem}-{k}.json"
            k += 1
        shutil.copyfile(file_path, target_path)

    def get_config(self, name: str) -> Config:
        filepath = CONFIGS_DIR / name
        if not filepath.exists():
            raise InternalError(f"Filepath {filepath} doesn't exist")

        with open(filepath, "rb") as file:
            config = Config(orjson.loads(file.read()))
        return config

    def get_config_list(self) -> list[str]:
        try:
            return list(
                filter(lambda p: Path(p).suffix == ".json", os.listdir(CONFIGS_DIR))
            )
        except Exception as e:
            raise InternalError(str(e))

    def update_config(self, name: str, new_config: dict) -> None:
        filepath = CONFIGS_DIR / name
        if not filepath.exists():
            raise InternalError(f"File {name} doesn't exist")
        try:
            with open(filepath, "wb") as f:
                f.write(orjson.dumps(new_config))
        except orjson.JSONDecodeError as e:
            raise InternalError(e)

    def delete_config(self, name: str) -> None:
        filepath = CONFIGS_DIR / name
        if not filepath.exists():
            raise InternalError(f"File {name} doesn't exist")
        try:
            os.remove(filepath)
        except Exception as e:
            raise InternalError(e)

    @staticmethod
    def read_by_name(name: str) -> dict | str:
        filepath = CONFIGS_DIR / f"{name}.json"
        try:
            with open(filepath, "rb") as file:
                return orjson.loads(file.read())
        except (FileNotFoundError, orjson.JSONDecodeError) as e:
            return str(e)
