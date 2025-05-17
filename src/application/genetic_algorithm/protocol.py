from typing import Protocol, Any, Tuple, List


class GAProcessorProtocol(Protocol):
    def run(self, config: dict[str, Any]) -> Tuple[List, List]:
        """Основной метод запуска генетического алгоритма"""
        ...
