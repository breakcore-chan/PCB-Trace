import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.application.config_manager.protocol import ConfigManagerProtocol
from src.application.genetic_algorithm.protocol import GAProcessorProtocol
from src.presentation.windows.component_editor import ComponentEditor
from src.presentation.windows.ga_processing import GAWindow
from src.presentation.windows.plot_window import PlotWindow
from src.utils.exceptions import WrongFileFormat
from src.utils.types import Config


class FrontApp:
    def __init__(
        self,
        root: tk.Tk,
        ga_processor: GAProcessorProtocol,
        config_manager: ConfigManagerProtocol,
    ) -> None:
        self._root = root
        self._root.title("Конфигурации для размещения элементов")
        self._config_manager = config_manager
        self._ga_processor = ga_processor
        # Создание интерфейса
        self._create_widgets()
        self._plot_window = PlotWindow(self._root)

    def _create_widgets(self) -> None:
        # Левая панель: список конфигураций и кнопки
        left_frame = ttk.LabelFrame(self._root, text="Конфигурации")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Список конфигураций
        self.__config_listbox = tk.Listbox(left_frame)
        self.__config_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.__config_listbox.bind("<<ListboxSelect>>", self._on_config_select)
        self.__config_listbox.bind(
            "<Button-3>", self._delete_config
        )  # ПКМ для удаления
        self.__config_listbox.bind("<BackSpace>", self._delete_config)
        self.__config_listbox.bind("<Delete>", self._delete_config)
        self._update_config_list()

        # Кнопка для создания новой конфигурации (под списком)
        new_config_button = tk.Button(
            left_frame, text="Добавить конфигурацию", command=self._create_new_config
        )
        new_config_button.pack(fill=tk.X, padx=5, pady=5)

        import_config_button = tk.Button(
            left_frame,
            text="Импортировать конфигурацию",
            command=self._import_config,
        )
        import_config_button.pack(fill=tk.X, padx=5, pady=5)

        # Кнопка для построения графиков (под списком)
        plot_button = tk.Button(
            left_frame, text="Построить графики", command=self._open_plot_window
        )
        plot_button.pack(fill=tk.X, padx=5, pady=5)

        # Правая панель: параметры конфигурации
        config_frame = ttk.LabelFrame(self._root, text="Параметры конфигурации")
        config_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Кнопки для запуска алгоритма и проверки размещения
        ga_button = tk.Button(
            config_frame, text="Запустить ГА", command=self._open_ga_console
        )
        ga_button.pack(side=tk.BOTTOM, pady=5)

        custom_layout_button = tk.Button(
            config_frame,
            text="Проверить размещение",
            command=self._check_custom_layout,
        )
        custom_layout_button.pack(side=tk.BOTTOM, pady=5)

        # Кнопка для открытия редактора компонентов
        component_editor_button = tk.Button(
            config_frame,
            text="Редактор компонентов",
            command=self._open_component_editor,
        )
        component_editor_button.pack(side=tk.BOTTOM, pady=5)

        # Отображение параметров конфигурации
        self.__config_params_frame = ttk.Frame(config_frame)
        self.__config_params_frame.pack(fill=tk.BOTH, expand=True)
        self._update_config_params()

    def _update_config_list(self) -> None:
        """Обновляет список конфигураций"""
        self.__config_listbox.delete(0, tk.END)
        for config_name in self._config_manager.get_config_list():
            self.__config_listbox.insert(tk.END, config_name)

    def _import_config(self) -> None:
        filepath = filedialog.askopenfilename(
            title="Выберите файл для импорта",
            filetypes=(("JSON файлы", "*.json"), ("Все файлы", "*.*")),
        )
        if filepath:
            try:
                self._config_manager.add_config_from_path(filepath)
            except WrongFileFormat:
                messagebox.showerror("Ошибка", "Файл должен быть нужного формата.")
            self._update_config_list()

    def _create_new_config(self) -> None:
        """Создает новую конфигурацию"""
        new_config_name = (
            f"Конфигурация {len(self._config_manager.get_config_list()) + 1}"
        )
        self._config_manager.add_config(new_config_name)
        self._update_config_list()
        self._update_config_params()

    def _on_config_select(self, event) -> None:
        """Обработчик выбора конфигурации"""
        self._update_config_params()

    def _delete_config(self, event) -> None:
        selected_config = self.__config_listbox.get(tk.ACTIVE)
        if selected_config:
            self._config_manager.delete_config(selected_config)  # Измененная строка
            self._update_config_list()
            self._update_config_params()

    def _update_config_params(self) -> None:
        """Обновляет отображение параметров конфигурации"""
        selected_config = self.__config_listbox.get(tk.ACTIVE)
        if selected_config:
            config = self._config_manager.get_config(selected_config)
            if not isinstance(config, dict):
                messagebox.showerror("Ошибка", "Конфигурация должна быть словарём.")
                return

            for widget in self.__config_params_frame.winfo_children():
                widget.destroy()

            row = 0
            for key, value in config.items():
                if key in ["components", "connections"]:
                    continue  # Пропускаем компоненты и соединения

                ttk.Label(self.__config_params_frame, text=f"{key}:").grid(
                    row=row, column=0, sticky=tk.W
                )

                # Поле для ввода значения
                entry = ttk.Entry(self.__config_params_frame)
                entry.insert(0, str(value))  # Вставляем значение по умолчанию
                entry.grid(row=row, column=1, sticky=tk.W)

                # Если значение по умолчанию, делаем текст серым
                entry.config(foreground="gray")
                entry.bind(
                    "<FocusIn>", lambda event, e=entry: self._on_entry_focus_in(e)
                )
                entry.bind(
                    "<FocusOut>",
                    lambda event, e=entry, k=key: self._on_entry_focus_out(
                        e, k, config
                    ),
                )

                row += 1

    def _on_entry_focus_in(self, entry) -> None:
        """Обработчик события фокуса на поле ввода"""
        if entry.get() == str(
            self._config_manager.get_config(self.__config_listbox.get(tk.ACTIVE)).get(
                entry.cget("text").rstrip(":")
            )
        ):
            entry.delete(0, tk.END)
            entry.config(foreground="black")

    def _on_entry_focus_out(self, entry, key, config) -> None:
        """Обработчик события потери фокуса на поле ввода"""
        if entry.get() == "":
            entry.insert(0, str(config[key]))
            entry.config(foreground="gray")
        else:
            # Обновляем значение в конфигурации
            try:
                if key in [
                    "board_width",
                    "board_height",
                    "population_size",
                    "generations",
                ]:
                    config[key] = int(entry.get())
                elif key in ["cxpb", "mutpb"]:
                    config[key] = float(entry.get())
                elif key in ["visualization_steps"]:
                    config[key] = list(map(int, entry.get().split(",")))
                else:
                    config[key] = entry.get()
            except ValueError:
                # Если ввод некорректен, восстанавливаем значение по умолчанию
                entry.delete(0, tk.END)
                entry.insert(0, str(config[key]))
                entry.config(foreground="gray")

    def __get_active_config(self) -> Config | None:
        selected_config = self.__config_listbox.get(tk.ACTIVE)
        if selected_config:
            return self._config_manager.get_config(selected_config)

    def _open_ga_console(self) -> None:
        """Открывает окно с консолью для запуска генетического алгоритма"""
        config = self.__get_active_config()
        if config:
            GAWindow(
                self._root,
                self._config_manager,
                self._ga_processor,
                config,
                self.__config_listbox.get(tk.ACTIVE),
            )
        else:
            messagebox.showwarning("Необходимо выбрать конфиг")

    def _check_custom_layout(self) -> None:
        """Проверяет кастомное размещение"""
        selected_config = self.__config_listbox.get(tk.ACTIVE)
        if selected_config:
            config = self._config_manager.get_config(selected_config)
            placements = []
            for _ in config["components"]:
                x = random.randint(0, config["board_width"] - 1)
                y = random.randint(0, config["board_height"] - 1)
                rot = random.randint(0, 1)
                placements.extend([x, y, rot])
            messagebox.showinfo("Кастомное размещение", f"Размещение: {placements}")

    def _open_plot_window(self) -> None:
        """Открывает окно для построения графиков"""
        config = self.__get_active_config()
        if config:
            self._plot_window.create_plot(config, self.__config_listbox.get(tk.ACTIVE))
        else:
            messagebox.showwarning("Необходимо выбрать конфиг")

    def _open_component_editor(self) -> None:
        """Открывает окно редактора компонентов"""
        config_name = self.__config_listbox.get(tk.ACTIVE)
        config = self.__get_active_config()
        if config:
            ComponentEditor(self._root, self._config_manager, config, config_name)
        else:
            messagebox.showwarning("Необходимо выбрать конфиг")

    def run(self) -> None:
        self._root.mainloop()
