from typing import Any, List, Protocol, Tuple


class GAProcessorProtocol(Protocol):
    def run(self, config: dict[str, Any]) -> Tuple[List, List]:
        """Основной метод запуска генетического алгоритма"""
        ...
