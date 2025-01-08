from PyQt5 import QtWidgets, QtCore
from ...mode_definitions.atom_selection import AtomSelectionWidget

class TorsionPage(QtWidgets.QWidget):
    def __init__(self, group_labels, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("计算一个二面角")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.prompt_label)

        self.atoms_group = QtWidgets.QGroupBox("ATOMS (选择六个参考原子)")
        atoms_layout = QtWidgets.QFormLayout(self.atoms_group)

        self.vector1_atom1 = AtomSelectionWidget(group_labels)
        atoms_layout.addRow("VECTOR1 - Atom 1:", self.vector1_atom1)

        self.vector1_atom2 = AtomSelectionWidget(group_labels)
        atoms_layout.addRow("VECTOR1 - Atom 2:", self.vector1_atom2)

        self.axis_atom1 = AtomSelectionWidget(group_labels)
        atoms_layout.addRow("AXIS - Atom 1:", self.axis_atom1)

        self.axis_atom2 = AtomSelectionWidget(group_labels)
        atoms_layout.addRow("AXIS - Atom 2:", self.axis_atom2)

        self.vector2_atom1 = AtomSelectionWidget(group_labels)
        atoms_layout.addRow("VECTOR2 - Atom 1:", self.vector2_atom1)

        self.vector2_atom2 = AtomSelectionWidget(group_labels)
        atoms_layout.addRow("VECTOR2 - Atom 2:", self.vector2_atom2)

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

        # 3. COSINE
        self.cosine_checkbox = QtWidgets.QCheckBox("COSINE")
        self.cosine_checkbox.setToolTip(
            "计算cos(二面角)而不是二面角值（默认关闭）"
        )
        self.adv_layout.addRow(self.cosine_checkbox)

        self.layout.addWidget(self.adv_box)

        # 新增的属性，用于存储cv的输出属性
        # 对于TORSION来说，输出属性同样是该cv的名称
        self.cv_output = []

    def get_definition_line(self):
        v1_a1 = self.vector1_atom1.get_selection()
        v1_a2 = self.vector1_atom2.get_selection()
        axis_a1 = self.axis_atom1.get_selection()
        axis_a2 = self.axis_atom2.get_selection()
        v2_a1 = self.vector2_atom1.get_selection()
        v2_a2 = self.vector2_atom2.get_selection()

        atoms = [v1_a1, v1_a2, axis_a1, axis_a2, v2_a1, v2_a2]

        if not all(atoms):
            QtWidgets.QMessageBox.warning(self, "警告", "请填写所有六个参考原子！")
            return None

        params = f"VECTOR1={v1_a1},{v1_a2} AXIS={axis_a1},{axis_a2} VECTOR2={v2_a1},{v2_a2}"

        if self.adv_box.isChecked():
            if self.numerical_derivatives_checkbox.isChecked():
                params += " NUMERICAL_DERIVATIVES"
            if self.nopbc_checkbox.isChecked():
                params += " NOPBC"
            if self.cosine_checkbox.isChecked():
                params += " COSINE"

        return params

    def populate_data(self, cv_data):
        # 从cv_data获取name用来设置cv_output
        name = cv_data.get('name', '')
        if name:
            self.cv_output = [name]  # 输出属性为该cv的名字

        params = cv_data.get('params', '')
        tokens = params.split()

        vector1 = []
        axis = []
        vector2 = []
        numerical_derivatives = False
        nopbc = False
        cosine = False

        for token in tokens:
            if token.startswith("VECTOR1="):
                vector1 = token[len("VECTOR1="):].split(',')
            elif token.startswith("AXIS="):
                axis = token[len("AXIS="):].split(',')
            elif token.startswith("VECTOR2="):
                vector2 = token[len("VECTOR2="):].split(',')
            elif token == "NUMERICAL_DERIVATIVES":
                numerical_derivatives = True
            elif token == "NOPBC":
                nopbc = True
            elif token == "COSINE":
                cosine = True

        if vector1 and axis and vector2:
            try:
                self.vector1_atom1.set_selection(vector1[0])
                self.vector1_atom2.set_selection(vector1[1])
                self.axis_atom1.set_selection(axis[0])
                self.axis_atom2.set_selection(axis[1])
                self.vector2_atom1.set_selection(vector2[0])
                self.vector2_atom2.set_selection(vector2[1])
            except:
                QtWidgets.QMessageBox.warning(self, "警告", "ATOMS 格式错误。")

        if numerical_derivatives or nopbc or cosine:
            self.adv_box.setChecked(True)
            self.numerical_derivatives_checkbox.setChecked(numerical_derivatives)
            self.nopbc_checkbox.setChecked(nopbc)
            self.cosine_checkbox.setChecked(cosine)
        else:
            self.adv_box.setChecked(False)
            self.numerical_derivatives_checkbox.setChecked(False)
            self.nopbc_checkbox.setChecked(False)
            self.cosine_checkbox.setChecked(False)
