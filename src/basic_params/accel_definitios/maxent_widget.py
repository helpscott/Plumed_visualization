# src/acceleration/methods/maxent_widget.py

from PyQt5 import QtWidgets

class MaxentWidget(QtWidgets.QWidget):
    """
    MAXENT加速采样方法的参数页面。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        # 基本参数
        basic_box = QtWidgets.QGroupBox("基本参数")
        bf = QtWidgets.QFormLayout(basic_box)

        # 输入的CV名称
        self.maxent_cv_combo = QtWidgets.QComboBox()
        self.maxent_cv_combo.setEditable(True)  # 允许手动输入
        bf.addRow("选择CV名称 (必填):", self.maxent_cv_combo)

        self.maxent_value_spin = QtWidgets.QDoubleSpinBox()
        self.maxent_value_spin.setRange(-1000.0, 1000.0)
        self.maxent_value_spin.setValue(0.0)
        bf.addRow("目标值 (必填):", self.maxent_value_spin)

        layout.addWidget(basic_box)

        # 高级参数
        adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        adv_box.setCheckable(True)
        adv_box.setChecked(False)
        af = QtWidgets.QFormLayout(adv_box)

        self.maxent_numerical = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        self.maxent_nopbc = QtWidgets.QCheckBox("NOPBC")
        af.addRow(self.maxent_numerical)
        af.addRow(self.maxent_nopbc)

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
                index = self.maxent_cv_combo.findText(cv_name)
                if index != -1:
                    self.maxent_cv_combo.setCurrentIndex(index)
                else:
                    self.maxent_cv_combo.addItem(cv_name)
                    self.maxent_cv_combo.setCurrentText(cv_name)
            elif token.startswith("VALUE="):
                value = token[len("VALUE="):]
                try:
                    self.maxent_value_spin.setValue(float(value))
                except ValueError:
                    pass
            elif token == "NUMERICAL_DERIVATIVES":
                self.maxent_numerical.setChecked(True)
            elif token == "NOPBC":
                self.maxent_nopbc.setChecked(True)

    def get_definition_line(self):
        """
        获取MAXENT加速采样方法的定义行。
        """
        cv_name = self.maxent_cv_combo.currentText().strip()
        value = self.maxent_value_spin.value()

        if not cv_name:
            QtWidgets.QMessageBox.warning(self, "警告", "请填写CV名称！")
            return None

        params = f"CV={cv_name} VALUE={value}"
        if self.maxent_numerical.isChecked():
            params += " NUMERICAL_DERIVATIVES"
        if self.maxent_nopbc.isChecked():
            params += " NOPBC"
        return params

    def update_cv_list(self, cv_list):
        """
        更新CV选择列表。
        cv_list: list of CV names
        """
        current_cv = self.maxent_cv_combo.currentText()
        self.maxent_cv_combo.clear()
        self.maxent_cv_combo.addItems(cv_list)
        if current_cv in cv_list:
            index = self.maxent_cv_combo.findText(current_cv)
            self.maxent_cv_combo.setCurrentIndex(index)
        else:
            self.maxent_cv_combo.setCurrentText("")
