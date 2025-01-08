"""
time_page.py
This is part of the generic module
Retrieve the current simulation time to be used as a CV

Example usage:
  t1: TIME
  PRINT ARG=t1

Options (keyword):
  NUMERICAL_DERIVATIVES (default=off)

Usage in code:
  - No basic parameter needed
  - One advanced param (NUMERICAL_DERIVATIVES) if desired
"""

from PyQt5 import QtWidgets

class TimePage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        prompt_label = QtWidgets.QLabel("计算当前模拟时间 (TIME)")
        prompt_label.setWordWrap(True)
        prompt_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(prompt_label)

        # 基础参数组 - 此CV无需任何基础参数
        self.base_group = QtWidgets.QGroupBox("此CV无需额外基础参数")
        base_layout = QtWidgets.QVBoxLayout(self.base_group)
        base_layout.addWidget(QtWidgets.QLabel("TIME: retrieves the simulation time"))
        layout.addWidget(self.base_group)

        # 高级按钮
        self.adv_btn = QtWidgets.QPushButton("高级参数")
        layout.addWidget(self.adv_btn)

        self.advanced_dialog = TimeAdvancedDialog(self)
        self.adv_btn.clicked.connect(self.open_advanced_dialog)

        self.setLayout(layout)

    def open_advanced_dialog(self):
        if self.advanced_dialog.exec_() == QtWidgets.QDialog.Accepted:
            pass  # 不做额外处理

    def get_definition_line(self):
        """
        返回形如:
          "NUMERICAL_DERIVATIVES"
        或 空字符串
        """
        adv_data = self.advanced_dialog.get_data()
        line = ""
        if adv_data.get('NUMERICAL_DERIVATIVES', False):
            line = "NUMERICAL_DERIVATIVES"
        return line.strip()

    def populate_data(self, cv_data):
        """
        如果params里包含NUMERICAL_DERIVATIVES就设定
        """
        params = cv_data.get('params', '')
        adv_dict = {
            'NUMERICAL_DERIVATIVES': False
        }
        tokens = params.split()
        for tk in tokens:
            if tk == "NUMERICAL_DERIVATIVES":
                adv_dict['NUMERICAL_DERIVATIVES'] = True
        # 用对话框进行回填
        self.advanced_dialog.populate_data(adv_dict)

    def get_cv_output(self):
        """
        TIME只有自己名称本身作为输出
        """
        if hasattr(self, 'cv_name'):
            return [self.cv_name]
        else:
            return []

    def set_cv_name(self, name):
        self.cv_name = name


class TimeAdvancedDialog(QtWidgets.QDialog):
    """
    高级设置:
      - NUMERICAL_DERIVATIVES
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TIME 高级参数")
        layout = QtWidgets.QVBoxLayout(self)

        self.nd_check = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 添加中文悬浮提示
        self.nd_check.setToolTip("启用数值方式计算导数（默认关闭）")
        layout.addWidget(self.nd_check)

        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("确定")
        self.cancel_btn = QtWidgets.QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.setLayout(layout)

    def get_data(self):
        return {
            'NUMERICAL_DERIVATIVES': self.nd_check.isChecked()
        }

    def populate_data(self, data):
        self.nd_check.setChecked(data.get('NUMERICAL_DERIVATIVES', False))
