class Config:
    BOARD_WIDTH = 20 # Высота платы
    BOARD_HEIGHT = 20 # Ширина платы
    POPULATION_SIZE = 50 # Размер популяции
    GENERATIONS = 1000 # Количество поколений
    CXPB = 0.7  # Вероятность спаривания двух особей
    MUTPB = 0.2  # Вероятность мутации особи
    VISUALIZATION_STEPS = [i for i in range(0, 100 + 10, 10)]
    SEED = 42 # Сид для генератора случайных чисел
    INDPB = 0.2  # Вероятность вызова мутации поворота
    COMPONENTS = [] # Список компонентов в формате {"width": 1, "height": 1 }
    CONNECTIONS = [] # Список соединений в формате [ 0, 1 ]
    FITNESS = [] # Список значений функции приспособленности, нужно для графиков
    
base_config = Config()
