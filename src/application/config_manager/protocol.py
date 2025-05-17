from typing import Any, Protocol


class ConfigManagerProtocol(Protocol):

    def add_config(self, name: str = "", config: dict[str, Any] | None = None) -> None:
        """Добавляет новую конфигурацию в отдельный файл"""
        ...

    def get_config(self, name: str) -> dict[str, Any] | None:
        """Возвращает конфигурацию по имени, включая компоненты и соединения"""
        ...

    def get_config_list(self) -> list[str]:
        """Возвращает список имен всех конфигураций"""
        ...

    def update_config(self, name: str, new_config: dict[str, Any]) -> None:
        """Обновляет существующую конфигурацию"""
        ...

    def delete_config(self, name: str) -> None:
        """Удаляет конфигурацию и соответствующий файл"""
        ...
