from typing import Protocol

from src.utils.types import Config


class ConfigManagerProtocol(Protocol):

    def add_config(self, name: str = "", config: Config | None = None) -> None:
        """Добавляет новую конфигурацию в отдельный файл"""
        ...

    def add_config_from_path(self, path: str) -> None:
        """Добавляет новую конфигурацию в отдельный файл из существующего файла"""
        ...

    def get_config(self, name: str) -> Config | None:
        """Возвращает конфигурацию по имени, включая компоненты и соединения"""
        ...

    def get_config_list(self) -> list[str]:
        """Возвращает список имен всех конфигураций"""
        ...

    def update_config(self, name: str, new_config: Config) -> None:
        """Обновляет существующую конфигурацию"""
        ...

    def delete_config(self, name: str) -> None:
        """Удаляет конфигурацию и соответствующий файл"""
        ...
