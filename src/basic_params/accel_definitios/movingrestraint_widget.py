# src/acceleration/methods/movingrestraint_widget.py

from PyQt5 import QtWidgets

class MovingRestraintWidget(QtWidgets.QWidget):
    """
    MOVINGRESTRAINT加速采样方法的参数页面。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        # 基本参数
        basic_box = QtWidgets.QGroupBox("基本参数")
        bf = QtWidgets.QFormLayout(basic_box)

        # 输入的CV名称
        self.mr_cv_combo = QtWidgets.QComboBox()
        self.mr_cv_combo.setEditable(True)  # 允许手动输入
        bf.addRow("选择CV名称 (必填):", self.mr_cv_combo)

        self.mr_speed_spin = QtWidgets.QDoubleSpinBox()
        self.mr_speed_spin.setRange(0.0, 1000.0)
        self.mr_speed_spin.setValue(0.1)
        bf.addRow("移动速度 (必填):", self.mr_speed_spin)

        layout.addWidget(basic_box)

        # 高级参数
        adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        adv_box.setCheckable(True)
        adv_box.setChecked(False)
        af = QtWidgets.QFormLayout(adv_box)

        self.mr_numerical = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        self.mr_nopbc = QtWidgets.QCheckBox("NOPBC")
        af.addRow(self.mr_numerical)
        af.addRow(self.mr_nopbc)

        layout.addWidget(adv_box)
        layout.addStretch()

    def populate_data(self, method_data):
        """
        根据传入的数据填充页面。
        method_data: dict, 包含 'params' 键的字典
        """
        params = method_data.get('params', '')
        tokens = params.split()

        for token in tokens:
            if token.startswith("CV="):
                cv_name = token[len("CV="):]
                index = self.mr_cv_combo.findText(cv_name)
                if index != -1:
                    self.mr_cv_combo.setCurrentIndex(index)
                else:
                    self.mr_cv_combo.addItem(cv_name)
                    self.mr_cv_combo.setCurrentText(cv_name)
            elif token.startswith("SPEED="):
                speed = token[len("SPEED="):]
                try:
                    self.mr_speed_spin.setValue(float(speed))
                except ValueError:
                    pass
            elif token == "NUMERICAL_DERIVATIVES":
                self.mr_numerical.setChecked(True)
            elif token == "NOPBC":
                self.mr_nopbc.setChecked(True)

    def get_definition_line(self):
        """
        获取MOVINGRESTRAINT加速采样方法的定义行。
        """
        cv_name = self.mr_cv_combo.currentText().strip()
        speed = self.mr_speed_spin.value()

        if not cv_name:
            QtWidgets.QMessageBox.warning(self, "警告", "请填写CV名称！")
            return None

        params = f"CV={cv_name} SPEED={speed}"
        if self.mr_numerical.isChecked():
            params += " NUMERICAL_DERIVATIVES"
        if self.mr_nopbc.isChecked():
            params += " NOPBC"
        return params

    def update_cv_list(self, cv_list):
        """
        更新CV选择列表。
        cv_list: list of CV names
        """
        current_cv = self.mr_cv_combo.currentText()
        self.mr_cv_combo.clear()
        self.mr_cv_combo.addItems(cv_list)
        if current_cv in cv_list:
            index = self.mr_cv_combo.findText(current_cv)
            self.mr_cv_combo.setCurrentIndex(index)
        else:
            self.mr_cv_combo.setCurrentText("")
