from PyQt5 import QtWidgets, QtCore

class VolumePage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("计算模拟盒子的体积")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.prompt_label)

        self.adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        self.adv_box.setCheckable(True)
        self.adv_box.setChecked(False)
        self.adv_layout = QtWidgets.QFormLayout(self.adv_box)

        self.numerical_derivatives_checkbox = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 添加中文悬浮提示
        self.numerical_derivatives_checkbox.setToolTip("启用数值方式计算导数（默认关闭）")
        self.adv_layout.addRow(self.numerical_derivatives_checkbox)

        self.layout.addWidget(self.adv_box)

        # 对于VOLUME来说，输出属性同样是该cv的名称
        self.cv_output = []

    def get_definition_line(self):
        params = ""

        if self.adv_box.isChecked():
            if self.numerical_derivatives_checkbox.isChecked():
                params += " NUMERICAL_DERIVATIVES"

        return params.strip()

    def populate_data(self, group_data):
        # 从cv_data获取name用来设置cv_output
        name = group_data.get('name', '')
        if name:
            self.cv_output = [name]  # 输出属性为该cv的名字

        params = group_data.get('params', '')
        tokens = params.split()

        numerical_derivatives = False

        for token in tokens:
            if token == "NUMERICAL_DERIVATIVES":
                numerical_derivatives = True

        if numerical_derivatives:
            self.adv_box.setChecked(True)
            self.numerical_derivatives_checkbox.setChecked(True)
        else:
            self.adv_box.setChecked(False)
            self.numerical_derivatives_checkbox.setChecked(False)
