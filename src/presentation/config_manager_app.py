import json
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.utils.config_manager_new import ConfigManager


class ConfigManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.current_config_name = None
        self.init_ui()
        self.load_config_names()

    def init_ui(self):
        self.setWindowTitle("JSON Config Manager")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel - config list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.config_list = QListWidget()
        self.config_list.itemClicked.connect(self.on_config_selected)
        left_layout.addWidget(QLabel("Available Configs:"))
        left_layout.addWidget(self.config_list)

        # Buttons for left panel
        btn_new = QPushButton("New Config")
        btn_new.clicked.connect(self.new_config)
        btn_delete = QPushButton("Delete Config")
        btn_delete.clicked.connect(self.delete_config)
        left_layout.addWidget(btn_new)
        left_layout.addWidget(btn_delete)

        # Right panel - config editor
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Config name editor
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Config Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter config name (without .json)")
        name_layout.addWidget(self.name_edit)
        right_layout.addLayout(name_layout)

        # JSON editor
        right_layout.addWidget(QLabel("Config Content (JSON):"))
        self.json_edit = QTextEdit()
        self.json_edit.setPlaceholderText("Enter valid JSON content")
        right_layout.addWidget(self.json_edit)

        # Save button
        btn_save = QPushButton("Save Changes")
        btn_save.clicked.connect(self.save_config)
        right_layout.addWidget(btn_save)

        # Import/Export buttons
        btn_layout = QHBoxLayout()
        btn_import = QPushButton("Import JSON")
        btn_import.clicked.connect(self.import_json)
        btn_export = QPushButton("Export JSON")
        btn_export.clicked.connect(self.export_json)
        btn_layout.addWidget(btn_import)
        btn_layout.addWidget(btn_export)
        right_layout.addLayout(btn_layout)

        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

    def load_config_names(self):
        self.config_list.clear()
        config_names = self.config_manager.read_all_names()
        if isinstance(config_names, list):
            for name in config_names:
                if name.endswith(".json"):
                    self.config_list.addItem(name)
        else:
            QMessageBox.warning(
                self, "Error", f"Failed to load config names: {config_names}"
            )

    def on_config_selected(self, item):
        self.current_config_name = item.text()
        self.name_edit.setText(self.current_config_name.replace(".json", ""))

        config_data = self.config_manager.read_dy_name(
            self.current_config_name.replace(".json", "")
        )
        if isinstance(config_data, dict):
            self.json_edit.setPlainText(json.dumps(config_data, indent=4))
        else:
            QMessageBox.warning(self, "Error", f"Failed to load config: {config_data}")
            self.json_edit.clear()

    def new_config(self):
        self.current_config_name = None
        self.name_edit.clear()
        self.json_edit.setPlainText(json.dumps({}, indent=4))
        self.name_edit.setFocus()

    def save_config(self):
        config_name = self.name_edit.text().strip()
        if not config_name:
            QMessageBox.warning(self, "Error", "Config name cannot be empty")
            return

        try:
            config_data = json.loads(self.json_edit.toPlainText())
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"JSON is invalid: {str(e)}")
            return

        if self.current_config_name:
            # Update existing config
            result = self.config_manager.update(
                self.current_config_name.replace(".json", ""), config_data
            )
            if result is not None:
                QMessageBox.warning(self, "Error", f"Failed to update config: {result}")
                return
        else:
            # Create new config
            self.config_manager.create(config_name, config_data)

        self.load_config_names()
        QMessageBox.information(self, "Success", "Config saved successfully")

    def delete_config(self):
        current_item = self.config_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "No config selected")
            return

        config_name = current_item.text()
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{config_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            result = self.config_manager.delete(config_name.replace(".json", ""))
            if result is not None:
                QMessageBox.warning(self, "Error", f"Failed to delete config: {result}")
            else:
                self.load_config_names()
                self.current_config_name = None
                self.name_edit.clear()
                self.json_edit.clear()

    def import_json(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import JSON", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                self.json_edit.setPlainText(json.dumps(data, indent=4))

                # Suggest the filename as config name
                suggested_name = file_path.split("/")[-1].replace(".json", "")
                if not self.name_edit.text():
                    self.name_edit.setText(suggested_name)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to import JSON: {str(e)}")

    def export_json(self):
        if not self.json_edit.toPlainText():
            QMessageBox.warning(self, "Error", "No JSON content to export")
            return

        try:
            json.loads(self.json_edit.toPlainText())  # Validate JSON
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"JSON is invalid: {str(e)}")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(self.json_edit.toPlainText())
                QMessageBox.information(self, "Success", "JSON exported successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export JSON: {str(e)}")
