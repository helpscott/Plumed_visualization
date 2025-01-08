# src/acceleration/methods/extended_lagrangian_widget.py

from PyQt5 import QtWidgets

class ExtendedLagrangianWidget(QtWidgets.QWidget):
    """
    EXTENDED_LAGRANGIAN加速采样方法的参数页面。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        # 基本参数
        basic_box = QtWidgets.QGroupBox("基本参数")
        bf = QtWidgets.QFormLayout(basic_box)

        # 输入的CV名称
        self.el_cv_combo = QtWidgets.QComboBox()
        self.el_cv_combo.setEditable(True)  # 允许手动输入
        bf.addRow("选择CV名称 (必填):", self.el_cv_combo)

        self.alpha_spin = QtWidgets.QDoubleSpinBox()
        self.alpha_spin.setRange(0.0, 1000.0)
        self.alpha_spin.setValue(0.5)
        bf.addRow("Alpha (必填):", self.alpha_spin)

        self.beta_spin = QtWidgets.QDoubleSpinBox()
        self.beta_spin.setRange(0.0, 1000.0)
        self.beta_spin.setValue(1.0)
        bf.addRow("Beta (必填):", self.beta_spin)

        layout.addWidget(basic_box)

        # 高级参数
        adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        adv_box.setCheckable(True)
        adv_box.setChecked(False)
        af = QtWidgets.QFormLayout(adv_box)

        self.el_enable_checkbox = QtWidgets.QCheckBox("ENABLE_LAGRANGIAN")
        af.addRow(self.el_enable_checkbox)

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
                index = self.el_cv_combo.findText(cv_name)
                if index != -1:
                    self.el_cv_combo.setCurrentIndex(index)
                else:
                    self.el_cv_combo.addItem(cv_name)
                    self.el_cv_combo.setCurrentText(cv_name)
            elif token.startswith("ALPHA="):
                alpha = token[len("ALPHA="):]
                try:
                    self.alpha_spin.setValue(float(alpha))
                except ValueError:
                    pass
            elif token.startswith("BETA="):
                beta = token[len("BETA="):]
                try:
                    self.beta_spin.setValue(float(beta))
                except ValueError:
                    pass
            elif token == "ENABLE_LAGRANGIAN":
                self.el_enable_checkbox.setChecked(True)

    def get_definition_line(self):
        """
        获取EXTENDED_LAGRANGIAN加速采样方法的定义行。
        """
        cv_name = self.el_cv_combo.currentText().strip()
        alpha = self.alpha_spin.value()
        beta = self.beta_spin.value()

        if not cv_name:
            QtWidgets.QMessageBox.warning(self, "警告", "请填写CV名称！")
            return None

        params = f"CV={cv_name} ALPHA={alpha} BETA={beta}"
        if self.el_enable_checkbox.isChecked():
            params += " ENABLE_LAGRANGIAN"
        return params

    def update_cv_list(self, cv_list):
        """
        更新CV选择列表。
        cv_list: list of CV names
        """
        current_cv = self.el_cv_combo.currentText()
        self.el_cv_combo.clear()
        self.el_cv_combo.addItems(cv_list)
        if current_cv in cv_list:
            index = self.el_cv_combo.findText(current_cv)
            self.el_cv_combo.setCurrentIndex(index)
        else:
            self.el_cv_combo.setCurrentText("")
