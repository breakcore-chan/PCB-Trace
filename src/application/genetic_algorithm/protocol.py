from typing import List, Protocol, Tuple

from src.utils.types import Config


class GAProcessorProtocol(Protocol):

    def run(self, config: Config) -> Tuple[List, List]:
        """Основной метод запуска генетического алгоритма"""
        ...
