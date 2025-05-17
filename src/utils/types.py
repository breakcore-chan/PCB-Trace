from pydantic import TypeAdapter
from typing_extensions import NotRequired, TypedDict


class Component(TypedDict):
    width: int
    height: int


class Config(TypedDict):
    name: NotRequired[str]
    board_width: int
    board_height: int
    population_size: int
    generations: int
    cxpb: float
    mutpb: float
    indpb: float
    seed: int
    visualization_steps: list[int]
    components: list[Component]
    connections: list[list[int]]
    fitness: list[float]


config_type_checker = TypeAdapter(Config)

BASE_CONFIG = Config(
    {
        "board_width": 20,  # Высота платы
        "board_height": 20,  # Ширина платы
        "population_size": 50,  # Размер популяции
        "generations": 1000,  # Количество поколений
        "cxpb": 0.7,  # Вероятность спаривания двух особей
        "mutpb": 0.2,  # Вероятность мутации особи
        "indpb": 0.2,  # Вероятность вызова мутации поворота
        "seed": 42,  # Сид для генератора случайных чисел
        "visualization_steps": [i for i in range(0, 100 + 10, 10)],
        "components": [
            {"width": 1, "height": 1},
            {"width": 7, "height": 2},
            {"width": 8, "height": 9},
            {"width": 2, "height": 3},
        ],  # Список компонентов в формате {"width": 1, "height": 1 }
        "connections": [  # Список соединений в формате [ 0, 1 ][
            [0, 1],
            [0, 3],
            [1, 3],
            [1, 2],
        ],
        "fitness": [],  # Список значений функции приспособленности, нужно для графиков
    }
)
