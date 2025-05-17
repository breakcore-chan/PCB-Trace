import tkinter as tk
from tkinter import ttk


class CustomLayoutWindow:
    def __init__(self, parent, config):
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("Проверка кастомного размещения")
        self.create_widgets()

    def create_widgets(self):
        """Создает интерфейс окна"""
        self.entries = []
        for i, comp in enumerate(self.config["components"]):
            frame = ttk.LabelFrame(self.window, text=f"Компонент {i + 1}")
            frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Label(frame, text="X:").grid(row=0, column=0)
            x_entry = ttk.Entry(frame)
            x_entry.grid(row=0, column=1)
            ttk.Label(frame, text="Y:").grid(row=0, column=2)
            y_entry = ttk.Entry(frame)
            y_entry.grid(row=0, column=3)
            ttk.Label(frame, text="Поворот:").grid(row=0, column=4)
            rot_entry = ttk.Entry(frame)
            rot_entry.grid(row=0, column=5)

            self.entries.append((x_entry, y_entry, rot_entry))

        ttk.Button(self.window, text="Проверить", command=self.evaluate).pack(pady=10)

    def evaluate(self):
        """Оценивает кастомное размещение"""
        placements = []
        for x_entry, y_entry, rot_entry in self.entries:
            x = int(x_entry.get())
            y = int(y_entry.get())
            rot = int(rot_entry.get())
            placements.extend([x, y, rot])

        # TODO: Здесь можно добавить вызов функции evaluate из GeneticAlgorithm
        print("Оценка размещения:", placements)
