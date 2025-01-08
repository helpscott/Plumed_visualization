# src/main.py

import sys
import os
from PyQt5 import QtWidgets


from .basic_params.basic_params import BasicParamsWidget
from .command_line.command_line_widget import CommandLineWidget
from .basic_params.config_manager import ConfigManager

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plumed Visualization and Setup Tool")
        self.resize(1200, 800)

        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        self.basic_widget = BasicParamsWidget(self)
        self.tabs.addTab(self.basic_widget, "基本参数")

        self.commandline_widget = CommandLineWidget(self)
        self.tabs.addTab(self.commandline_widget, "命令行工具")

        self.create_style_menu()
        self.apply_style("style/style_fusion.qss")

    def create_style_menu(self):
        menubar = self.menuBar()
        style_menu = menubar.addMenu("风格")

        self.style_dict = {
            "Pure White":       "style/style_pure_white.qss",
            "Pure Black":       "style/style_pure_black.qss",
            "Fusion (Default)": "style/style_fusion.qss",
            "Blue Theme":       "style/style_blue.qss",
            "Dark Fusion":      "style/style_darkfusion.qss",
        }

        for style_name, qss_file in self.style_dict.items():
            action = QtWidgets.QAction(style_name, self)
            # lambda 改动：将 file=qss_file 传入 apply_style
            action.triggered.connect(lambda checked, file=qss_file: self.apply_style(file))
            style_menu.addAction(action)

    def apply_style(self, qss_filename):
        """
        根据选择的 qss 文件，切换全局样式。
        如果没找到文件，就弹出警告并使用默认Fusion。
        """
        app = QtWidgets.QApplication.instance()
        if not app:
            return

        app.setStyle("Fusion")

        full_path = os.path.join(os.path.dirname(__file__), qss_filename)
        if os.path.isfile(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                qss_content = f.read()
            app.setStyleSheet(qss_content)
        else:
            QtWidgets.QMessageBox.warning(self, "提示", f"未找到样式文件: {full_path}")
            app.setStyleSheet("")

    def load_config(self, config_path):
        """
        加载指定路径的配置文件并恢复配置。
        """
        if os.path.isfile(config_path):
            try:
                ConfigManager.load_config(config_path, self.basic_widget)
                QtWidgets.QMessageBox.information(self, "加载成功", f"已加载配置文件: {config_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "加载失败", f"加载配置文件失败: {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "警告", f"配置文件不存在: {config_path}")

def run():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    w = MainWindow()

    # 检查是否有命令行参数来加载配置
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        w.load_config(config_path)

    w.show()
    sys.exit(app.exec())

    
if __name__ == "__main__":
    run()