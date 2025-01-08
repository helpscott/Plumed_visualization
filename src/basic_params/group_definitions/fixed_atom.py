from PyQt5 import QtWidgets, QtCore

class FixedAtomPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("在固定位置添加虚拟原子")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.prompt_label)

        self.basic_group = QtWidgets.QGroupBox("基本参数")
        self.basic_layout = QtWidgets.QFormLayout(self.basic_group)
        self.at_x = QtWidgets.QDoubleSpinBox()
        self.at_x.setRange(-999999, 999999)
        self.at_x.setDecimals(3)
        self.at_y = QtWidgets.QDoubleSpinBox()
        self.at_y.setRange(-999999, 999999)
        self.at_y.setDecimals(3)
        self.at_z = QtWidgets.QDoubleSpinBox()
        self.at_z.setRange(-999999, 999999)
        self.at_z.setDecimals(3)
        self.basic_layout.addRow("AT X:", self.at_x)
        self.basic_layout.addRow("AT Y:", self.at_y)
        self.basic_layout.addRow("AT Z:", self.at_z)
        self.layout.addWidget(self.basic_group)

        self.adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        self.adv_box.setCheckable(True)
        self.adv_box.setChecked(False)
        self.adv_layout = QtWidgets.QFormLayout(self.adv_box)

        # SET_MASS checkbox + input
        self.set_mass_checkbox = QtWidgets.QCheckBox("SET_MASS=")
        self.set_mass_input = QtWidgets.QLineEdit()
        self.set_mass_input.setEnabled(False)
        # 中文说明 (placeholder) 对应 "虚拟原子的质量(默认=1)"
        self.set_mass_input.setPlaceholderText("设置虚拟原子的质量（默认=1）")

        self.adv_layout.addRow(self.set_mass_checkbox, self.set_mass_input)

        # SET_CHARGE checkbox + input
        self.set_charge_checkbox = QtWidgets.QCheckBox("SET_CHARGE=")
        self.set_charge_input = QtWidgets.QLineEdit()
        self.set_charge_input.setEnabled(False)
        # 中文说明 (placeholder) 对应 "虚拟原子的电荷(默认=0)"
        self.set_charge_input.setPlaceholderText("设置虚拟原子的电荷（默认=0）")

        self.adv_layout.addRow(self.set_charge_checkbox, self.set_charge_input)

        # SCALED_COMPONENTS
        self.scaled_components_checkbox = QtWidgets.QCheckBox("SCALED_COMPONENTS")
        # 中文说明 (鼠标悬浮 tooltip) 对应 "使用缩放分量 (默认=off)"
        self.scaled_components_checkbox.setToolTip("使用缩放分量（默认关闭）")

        self.adv_layout.addRow(self.scaled_components_checkbox)

        self.layout.addWidget(self.adv_box)

        # stateChanged
        self.set_mass_checkbox.stateChanged.connect(self.toggle_set_mass)
        self.set_charge_checkbox.stateChanged.connect(self.toggle_set_charge)
        self.scaled_components_checkbox.stateChanged.connect(self.toggle_scaled_components)

    def toggle_set_mass(self, state):
        if state == QtCore.Qt.Checked:
            self.set_mass_input.setEnabled(True)
        else:
            self.set_mass_input.setEnabled(False)
            self.set_mass_input.clear()

    def toggle_set_charge(self, state):
        if state == QtCore.Qt.Checked:
            self.set_charge_input.setEnabled(True)
        else:
            self.set_charge_input.setEnabled(False)
            self.set_charge_input.clear()

    def toggle_scaled_components(self, state):
        pass

    def get_definition_line(self):
        at_x = self.at_x.value()
        at_y = self.at_y.value()
        at_z = self.at_z.value()
        params = f"AT={at_x},{at_y},{at_z}"

        if self.adv_box.isChecked():
            if self.set_mass_checkbox.isChecked() and self.set_mass_input.text().strip():
                params += f" SET_MASS={self.set_mass_input.text().strip()}"
            if self.set_charge_checkbox.isChecked() and self.set_charge_input.text().strip():
                params += f" SET_CHARGE={self.set_charge_input.text().strip()}"
            if self.scaled_components_checkbox.isChecked():
                params += " SCALED_COMPONENTS"

        return params

    def populate_data(self, group_data):
        params = group_data.get('params', '')
        tokens = params.split()

        at_values = ""
        set_mass = ""
        set_charge = ""
        scaled_components = False

        for token in tokens:
            if token.startswith("AT="):
                at_values = token[len("AT="):]
            elif token.startswith("SET_MASS="):
                set_mass = token[len("SET_MASS="):]
            elif token.startswith("SET_CHARGE="):
                set_charge = token[len("SET_CHARGE="):]
            elif token == "SCALED_COMPONENTS":
                scaled_components = True

        # 回显坐标
        if at_values:
            try:
                x, y, z = map(float, at_values.split(','))
                self.at_x.setValue(x)
                self.at_y.setValue(y)
                self.at_z.setValue(z)
            except:
                QtWidgets.QMessageBox.warning(self, "警告", "AT 格式错误。")

        # 回显高级参数
        if set_mass or set_charge or scaled_components:
            self.adv_box.setChecked(True)

            if set_mass:
                self.set_mass_checkbox.setChecked(True)
                self.set_mass_input.setEnabled(True)
                self.set_mass_input.setText(set_mass)
            else:
                self.set_mass_checkbox.setChecked(False)
                self.set_mass_input.setEnabled(False)
                self.set_mass_input.clear()

            if set_charge:
                self.set_charge_checkbox.setChecked(True)
                self.set_charge_input.setEnabled(True)
                self.set_charge_input.setText(set_charge)
            else:
                self.set_charge_checkbox.setChecked(False)
                self.set_charge_input.setEnabled(False)
                self.set_charge_input.clear()

            self.scaled_components_checkbox.setChecked(scaled_components)
        else:
            self.adv_box.setChecked(False)
            self.set_mass_checkbox.setChecked(False)
            self.set_mass_input.clear()
            self.set_charge_checkbox.setChecked(False)
            self.set_charge_input.clear()
            self.scaled_components_checkbox.setChecked(False)
