from PyQt5 import QtWidgets, QtCore
from ...mode_definitions.atom_selection import AtomSelectionWidget

class DistancePage(QtWidgets.QWidget):
    def __init__(self, group_labels, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("计算两个原子间的距离")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.prompt_label)

        self.atoms_group = QtWidgets.QGroupBox("ATOMS (选择两个参考原子)")
        atoms_layout = QtWidgets.QFormLayout(self.atoms_group)

        self.atom1_selection = AtomSelectionWidget(group_labels)
        atoms_layout.addRow("Atom 1:", self.atom1_selection)

        self.atom2_selection = AtomSelectionWidget(group_labels)
        atoms_layout.addRow("Atom 2:", self.atom2_selection)

        self.layout.addWidget(self.atoms_group)

        self.adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        self.adv_box.setCheckable(True)
        self.adv_box.setChecked(False)
        self.adv_layout = QtWidgets.QFormLayout(self.adv_box)

        # 1. NUMERICAL_DERIVATIVES
        self.numerical_derivatives_checkbox = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        self.numerical_derivatives_checkbox.setToolTip(
            "启用数值方式计算导数（默认关闭）"
        )
        self.adv_layout.addRow(self.numerical_derivatives_checkbox)

        # 2. NOPBC
        self.nopbc_checkbox = QtWidgets.QCheckBox("NOPBC")
        self.nopbc_checkbox.setToolTip(
            "忽略周期性边界条件来计算距离（默认关闭）"
        )
        self.adv_layout.addRow(self.nopbc_checkbox)

        # 3. COMPONENTS
        self.components_checkbox = QtWidgets.QCheckBox("COMPONENTS")
        self.components_checkbox.setToolTip(
            "将距离的x, y, z分量分别存储为 label.x, label.y, label.z（默认关闭）"
        )
        self.adv_layout.addRow(self.components_checkbox)

        # 4. SCALED_COMPONENTS
        self.scaled_components_checkbox = QtWidgets.QCheckBox("SCALED_COMPONENTS")
        self.scaled_components_checkbox.setToolTip(
            "将距离的a, b, c缩放分量分别存储为 label.a, label.b, label.c（默认关闭）"
        )
        self.adv_layout.addRow(self.scaled_components_checkbox)

        self.layout.addWidget(self.adv_box)

        self.cv_name = ""  # 初始化为空

    def set_cv_name(self, name):
        # 在CVDefinitionDialog中保存后显式调用此方法
        self.cv_name = name

    def get_definition_line(self):
        atom1 = self.atom1_selection.get_selection()
        atom2 = self.atom2_selection.get_selection()

        if not atom1 or not atom2:
            QtWidgets.QMessageBox.warning(self, "警告", "请填写两个参考原子！")
            return None

        params = f"ATOMS={atom1},{atom2}"

        if self.adv_box.isChecked():
            if self.numerical_derivatives_checkbox.isChecked():
                params += " NUMERICAL_DERIVATIVES"
            if self.nopbc_checkbox.isChecked():
                params += " NOPBC"
            if self.components_checkbox.isChecked():
                params += " COMPONENTS"
            if self.scaled_components_checkbox.isChecked():
                params += " SCALED_COMPONENTS"

        return params

    def populate_data(self, cv_data):
        # 尽管populate_data可能不调用，但如果编辑已有CV则会调用
        name = cv_data.get('name', '')
        if name:
            self.cv_name = name

        params = cv_data.get('params', '')
        tokens = params.split()

        atom_list = []
        numerical_derivatives = False
        nopbc = False
        components = False
        scaled_components = False

        for token in tokens:
            if token.startswith("ATOMS="):
                atom_list = token[len("ATOMS="):].split(',')
            elif token == "NUMERICAL_DERIVATIVES":
                numerical_derivatives = True
            elif token == "NOPBC":
                nopbc = True
            elif token == "COMPONENTS":
                components = True
            elif token == "SCALED_COMPONENTS":
                scaled_components = True

        if atom_list and len(atom_list) == 2:
            try:
                self.atom1_selection.set_selection(atom_list[0])
                self.atom2_selection.set_selection(atom_list[1])
            except:
                QtWidgets.QMessageBox.warning(self, "警告", "ATOMS 格式错误。")

        if numerical_derivatives or nopbc or components or scaled_components:
            self.adv_box.setChecked(True)
            self.numerical_derivatives_checkbox.setChecked(numerical_derivatives)
            self.nopbc_checkbox.setChecked(nopbc)
            self.components_checkbox.setChecked(components)
            self.scaled_components_checkbox.setChecked(scaled_components)
        else:
            self.adv_box.setChecked(False)
            self.numerical_derivatives_checkbox.setChecked(False)
            self.nopbc_checkbox.setChecked(False)
            self.components_checkbox.setChecked(False)
            self.scaled_components_checkbox.setChecked(False)

    def get_cv_output(self):
        # 根据当前UI状态和cv_name动态返回输出属性
        # 若cv_name为空，说明在CVDefinitionDialog保存后应调用set_cv_name
        if not self.cv_name:
            return []
        outputs = [self.cv_name]
        if self.adv_box.isChecked():
            if self.components_checkbox.isChecked():
                outputs.extend([f"{self.cv_name}.x", f"{self.cv_name}.y", f"{self.cv_name}.z"])
            if self.scaled_components_checkbox.isChecked():
                outputs.extend([f"{self.cv_name}.a", f"{self.cv_name}.b", f"{self.cv_name}.c"])
        return outputs
