# src/acceleration/methods/abmd_widget.py

from PyQt5 import QtWidgets

class AbmdWidget(QtWidgets.QWidget):
    """
    ABMD加速采样方法的参数页面。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        # 基本参数
        basic_box = QtWidgets.QGroupBox("基本参数")
        bf = QtWidgets.QFormLayout(basic_box)

        # 输入Bias的CV名称
        self.abmd_cv_combo = QtWidgets.QComboBox()
        self.abmd_cv_combo.setEditable(True)  # 允许手动输入
        bf.addRow("选择CV名称 (必填):", self.abmd_cv_combo)

        self.param1_line = QtWidgets.QLineEdit()
        bf.addRow("参数1 (必填):", self.param1_line)

        self.param2_line = QtWidgets.QLineEdit()
        bf.addRow("参数2 (必填):", self.param2_line)

        layout.addWidget(basic_box)

        # 高级参数
        adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        adv_box.setCheckable(True)
        adv_box.setChecked(False)
        af = QtWidgets.QFormLayout(adv_box)

        self.abmd_numerical = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        self.abmd_nopbc = QtWidgets.QCheckBox("NOPBC")
        af.addRow(self.abmd_numerical)
        af.addRow(self.abmd_nopbc)

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
                index = self.abmd_cv_combo.findText(cv_name)
                if index != -1:
                    self.abmd_cv_combo.setCurrentIndex(index)
                else:
                    self.abmd_cv_combo.addItem(cv_name)
                    self.abmd_cv_combo.setCurrentText(cv_name)
            elif token.startswith("PARAM1="):
                param1 = token[len("PARAM1="):]
                self.param1_line.setText(param1)
            elif token.startswith("PARAM2="):
                param2 = token[len("PARAM2="):]
                self.param2_line.setText(param2)
            elif token == "NUMERICAL_DERIVATIVES":
                self.abmd_numerical.setChecked(True)
            elif token == "NOPBC":
                self.abmd_nopbc.setChecked(True)

    def get_definition_line(self):
        """
        获取ABMD加速采样方法的定义行。
        """
        cv_name = self.abmd_cv_combo.currentText().strip()
        param1 = self.param1_line.text().strip()
        param2 = self.param2_line.text().strip()

        if not cv_name or not param1 or not param2:
            QtWidgets.QMessageBox.warning(self, "警告", "请填写所有必填参数！")
            return None

        params = f"CV={cv_name} PARAM1={param1} PARAM2={param2}"
        if self.abmd_numerical.isChecked():
            params += " NUMERICAL_DERIVATIVES"
        if self.abmd_nopbc.isChecked():
            params += " NOPBC"
        return params

    def update_cv_list(self, cv_list):
        """
        更新CV选择列表。
        cv_list: list of CV names
        """
        current_cv = self.abmd_cv_combo.currentText()
        self.abmd_cv_combo.clear()
        self.abmd_cv_combo.addItems(cv_list)
        if current_cv in cv_list:
            index = self.abmd_cv_combo.findText(current_cv)
            self.abmd_cv_combo.setCurrentIndex(index)
        else:
            self.abmd_cv_combo.setCurrentText("")
