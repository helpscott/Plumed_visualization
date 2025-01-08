# command_line_widget.py

import os
import subprocess
from PyQt5 import QtWidgets, QtCore

from .sum_hills_widget import SumHillsWidget
from .driver_widget import DriverWidget
from .info_widget import InfoWidget
from .kt_widget import KtWidget
from .pathtools_widget import PathToolsWidget

# 新增
from .pdbrenumber_widget import PdbRenumberWidget

class CommandLineWidget(QtWidgets.QWidget):
    """
    命令行工具的主控件：
      - 下拉框：选择工具 (现支持 sum_hills, driver, info, kt, pathtools, pdbrenumber)
      - 一个按钮：点击后展开/收起 对应工具的参数设置页面
      - 命令行展示 (QLineEdit) + 用户可编辑
      - 运行命令按钮
      - 运行结果显示 (QTextEdit)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # 顶部：选择命令行工具 + 显示/隐藏参数设置
        top_hlayout = QtWidgets.QHBoxLayout()
        top_hlayout.addWidget(QtWidgets.QLabel("选择命令行工具:"))

        self.tool_combo = QtWidgets.QComboBox()
        # 在下拉里增加 "pdbrenumber"
        self.tool_combo.addItems([
            "(请选择工具)",
            "sum_hills",
            "driver",
            "info",
            "kt",
            "pathtools",
            "pdbrenumber",
        ])
        top_hlayout.addWidget(self.tool_combo)

        self.show_settings_btn = QtWidgets.QPushButton("显示/隐藏 参数设置")
        top_hlayout.addWidget(self.show_settings_btn)
        main_layout.addLayout(top_hlayout)

        # 中部：堆叠页面
        self.stack = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.stack)

        self.blank_widget = QtWidgets.QWidget()
        self.stack.addWidget(self.blank_widget)

        self.sumhills_page = SumHillsWidget()
        self.stack.addWidget(self.sumhills_page)
        self.sumhills_page.params_changed.connect(self.update_command_line)

        self.driver_page = DriverWidget()
        self.stack.addWidget(self.driver_page)
        self.driver_page.params_changed.connect(self.update_command_line)

        self.info_page = InfoWidget()
        self.stack.addWidget(self.info_page)
        self.info_page.params_changed.connect(self.update_command_line)

        self.kt_page = KtWidget()
        self.stack.addWidget(self.kt_page)
        self.kt_page.params_changed.connect(self.update_command_line)

        self.pathtools_page = PathToolsWidget()
        self.stack.addWidget(self.pathtools_page)
        self.pathtools_page.params_changed.connect(self.update_command_line)

        # 新增：pdbrenumber 页面
        self.pdbrenumber_page = PdbRenumberWidget()
        self.stack.addWidget(self.pdbrenumber_page)
        self.pdbrenumber_page.params_changed.connect(self.update_command_line)

        self.stack.setCurrentWidget(self.blank_widget)
        self.tool_combo.currentTextChanged.connect(self.on_tool_changed)
        self.show_settings_btn.clicked.connect(self.toggle_settings_visible)

        # 命令行展示 + 运行按钮
        cmd_hlayout = QtWidgets.QHBoxLayout()
        cmd_hlayout.addWidget(QtWidgets.QLabel("生成的命令:"))
        self.cmd_edit = QtWidgets.QLineEdit()
        self.cmd_edit.setPlaceholderText("plumed sum_hills ... / plumed driver ... / plumed info ... / plumed kt ... / pathtools ... / pdbrenumber ...")
        cmd_hlayout.addWidget(self.cmd_edit)
        main_layout.addLayout(cmd_hlayout)

        self.run_btn = QtWidgets.QPushButton("运行命令")
        main_layout.addWidget(self.run_btn)
        self.run_btn.clicked.connect(self.run_command)

        # 最下方：输出结果
        self.output_text = QtWidgets.QTextEdit()
        self.output_text.setReadOnly(True)
        main_layout.addWidget(self.output_text)

        # 初始化
        self.settings_visible = False
        self.stack.setVisible(self.settings_visible)
        self.setLayout(main_layout)

    def on_tool_changed(self, txt):
        """
        根据下拉框的选择，切换到对应的工具界面
        """
        if txt == "sum_hills":
            self.stack.setCurrentWidget(self.sumhills_page)
            self.update_command_line()
        elif txt == "driver":
            self.stack.setCurrentWidget(self.driver_page)
            self.update_command_line()
        elif txt == "info":
            self.stack.setCurrentWidget(self.info_page)
            self.update_command_line()
        elif txt == "kt":
            self.stack.setCurrentWidget(self.kt_page)
            self.update_command_line()
        elif txt == "pathtools":
            self.stack.setCurrentWidget(self.pathtools_page)
            self.update_command_line()
        elif txt == "pdbrenumber":
            self.stack.setCurrentWidget(self.pdbrenumber_page)
            self.update_command_line()
        else:
            self.stack.setCurrentWidget(self.blank_widget)
            self.cmd_edit.setText("")

    def toggle_settings_visible(self):
        """
        显示或隐藏参数设置区域
        """
        self.settings_visible = not self.settings_visible
        self.stack.setVisible(self.settings_visible)

    def update_command_line(self):
        """
        读取当前子页面的参数并拼出最终命令行
        """
        current_tool = self.tool_combo.currentText()

        if current_tool == "sum_hills":
            flags_list = self.sumhills_page.get_command_flags()
            cmd_str = "plumed sum_hills " + " ".join(flags_list)
            self.cmd_edit.setText(cmd_str)

        elif current_tool == "driver":
            flags_list = self.driver_page.get_command_flags()
            cmd_str = "plumed driver " + " ".join(flags_list)
            self.cmd_edit.setText(cmd_str)

        elif current_tool == "info":
            flags_list = self.info_page.get_command_flags()
            cmd_str = "plumed info " + " ".join(flags_list)
            self.cmd_edit.setText(cmd_str)

        elif current_tool == "kt":
            flags_list = self.kt_page.get_command_flags()
            cmd_str = "plumed kt " + " ".join(flags_list)
            self.cmd_edit.setText(cmd_str)

        elif current_tool == "pathtools":
            flags_list = self.pathtools_page.get_command_flags()
            cmd_str = "plumed pathtools " + " ".join(flags_list)
            self.cmd_edit.setText(cmd_str)

        elif current_tool == "pdbrenumber":
            flags_list = self.pdbrenumber_page.get_command_flags()
            cmd_str = "plumed pdbrenumber " + " ".join(flags_list)
            self.cmd_edit.setText(cmd_str)

        else:
            self.cmd_edit.setText("")

    def run_command(self):
        """
        在 data 目录下执行命令，并显示输出
        """
        cmd_line = self.cmd_edit.text().strip()
        if not cmd_line:
            QtWidgets.QMessageBox.warning(self, "提示", "当前命令行为空，请先选择并设置工具。")
            return

        self.output_text.clear()
        self.output_text.append(f"执行命令: {cmd_line}\n")

        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        data_dir = os.path.abspath(data_dir)

        process = subprocess.Popen(
            cmd_line,
            shell=True,
            cwd=data_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                self.output_text.append(line.rstrip("\n"))

        retcode = process.wait()
        self.output_text.append(f"\n[进程结束，返回码: {retcode}]")
