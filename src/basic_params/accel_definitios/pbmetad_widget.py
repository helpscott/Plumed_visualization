# src/acceleration/methods/pbmetad_widget.py

from PyQt5 import QtWidgets

class PbmetadWidget(QtWidgets.QWidget):
    """
    PBMETAD加速采样方法的参数页面。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        # 基本参数
        basic_box = QtWidgets.QGroupBox("基本参数")
        bf = QtWidgets.QFormLayout(basic_box)

        # 选择CV的下拉框
        self.pbmetad_cv_combo = QtWidgets.QComboBox()
        bf.addRow("选择CV (必填):", self.pbmetad_cv_combo)

        # Kappa参数
        self.pbmetad_kappa_spin = QtWidgets.QDoubleSpinBox()
        self.pbmetad_kappa_spin.setRange(0.0, 1000.0)
        self.pbmetad_kappa_spin.setValue(1.0)
        bf.addRow("Kappa (必填):", self.pbmetad_kappa_spin)

        layout.addWidget(basic_box)

        # 高级参数
        adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        adv_box.setCheckable(True)
        adv_box.setChecked(False)
        af = QtWidgets.QFormLayout(adv_box)

        self.pbmetad_numerical = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        self.pbmetad_nopbc = QtWidgets.QCheckBox("NOPBC")
        af.addRow(self.pbmetad_numerical)
        af.addRow(self.pbmetad_nopbc)

        layout.addWidget(adv_box)
        layout.addStretch()

    def set_cv_list(self, cv_list):
        """
        设置CV列表到下拉框中。
        cv_list: list of str
        """
        self.pbmetad_cv_combo.clear()
        self.pbmetad_cv_combo.addItems(cv_list)

    def populate_data(self, method_data):
        """
        根据传入的方法数据填充页面。
        method_data: dict, 包含 'params' 键的字典
        """
        params = method_data.get('params', '')
        tokens = params.split()

        for token in tokens:
            if token.startswith("CV="):
                cv_name = token[len("CV="):]
                idx = self.pbmetad_cv_combo.findText(cv_name)
                if idx != -1:
                    self.pbmetad_cv_combo.setCurrentIndex(idx)
                else:
                    self.pbmetad_cv_combo.addItem(cv_name)
                    self.pbmetad_cv_combo.setCurrentText(cv_name)
            elif token.startswith("KAPPA="):
                kappa = token[len("KAPPA="):]
                try:
                    self.pbmetad_kappa_spin.setValue(float(kappa))
                except ValueError:
                    pass
            elif token == "NUMERICAL_DERIVATIVES":
                self.pbmetad_numerical.setChecked(True)
            elif token == "NOPBC":
                self.pbmetad_nopbc.setChecked(True)

    def get_definition_line(self):
        """
        获取PBMETAD加速采样方法的定义行。
        """
        cv_name = self.pbmetad_cv_combo.currentText().strip()
        kappa = self.pbmetad_kappa_spin.value()

        if not cv_name:
            QtWidgets.QMessageBox.warning(self, "警告", "请选择CV！")
            return None

        params = f"CV={cv_name} KAPPA={kappa}"
        if self.pbmetad_numerical.isChecked():
            params += " NUMERICAL_DERIVATIVES"
        if self.pbmetad_nopbc.isChecked():
            params += " NOPBC"
        return params
