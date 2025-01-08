from PyQt5 import QtWidgets, QtCore
from ...mode_definitions.atom_selection import AtomSelectionWidget

class AnglePage(QtWidgets.QWidget):
    def __init__(self, group_labels, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("计算一个角度")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.prompt_label)

        self.atoms_group = QtWidgets.QGroupBox("ATOMS (选择三个或四个参考原子)")
        atoms_layout = QtWidgets.QFormLayout(self.atoms_group)

        self.atom1_selection = AtomSelectionWidget(group_labels)
        atoms_layout.addRow("Vector 1 - Atom 1:", self.atom1_selection)

        self.atom2_selection = AtomSelectionWidget(group_labels)
        atoms_layout.addRow("Vector 1 - Atom 2:", self.atom2_selection)

        self.atom3_selection = AtomSelectionWidget(group_labels)
        atoms_layout.addRow("Vector 2 - Atom 1:", self.atom3_selection)

        self.atom4_selection = AtomSelectionWidget(group_labels)
        atoms_layout.addRow("Vector 2 - Atom 2 (可选):", self.atom4_selection)

        self.layout.addWidget(self.atoms_group)

        self.adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        self.adv_box.setCheckable(True)
        self.adv_box.setChecked(False)
        self.adv_layout = QtWidgets.QFormLayout(self.adv_box)

        self.numerical_derivatives_checkbox = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 为NUMERICAL_DERIVATIVES添加中文鼠标悬浮提示
        self.numerical_derivatives_checkbox.setToolTip(
            "启用数值求导来计算这些量的导数（默认关闭）"
        )

        self.adv_layout.addRow(self.numerical_derivatives_checkbox)

        self.nopbc_checkbox = QtWidgets.QCheckBox("NOPBC")
        # 为NOPBC添加中文鼠标悬浮提示
        self.nopbc_checkbox.setToolTip(
            "在计算距离时忽略周期性边界条件（默认关闭）"
        )

        self.adv_layout.addRow(self.nopbc_checkbox)

        self.layout.addWidget(self.adv_box)

        # 新增的属性，用于存储cv的输出属性
        self.cv_output = []

    def get_definition_line(self):
        atom1 = self.atom1_selection.get_selection()
        atom2 = self.atom2_selection.get_selection()
        atom3 = self.atom3_selection.get_selection()
        atom4 = self.atom4_selection.get_selection()

        atoms = [atom1, atom2, atom3]
        if atom4:
            atoms.append(atom4)

        if len(atoms) not in [3, 4]:
            QtWidgets.QMessageBox.warning(self, "警告", "请至少选择三个或四个参考原子！")
            return None

        atoms_str = ",".join(atoms)
        params = f"ATOMS={atoms_str}"

        if self.adv_box.isChecked():
            if self.numerical_derivatives_checkbox.isChecked():
                params += " NUMERICAL_DERIVATIVES"
            if self.nopbc_checkbox.isChecked():
                params += " NOPBC"

        return params

    def populate_data(self, cv_data):
        # cv_data中应该包含 'name' 字段，用于设置cv_output
        name = cv_data.get('name', '')
        if name:
            self.cv_output = [name]  # 输出属性为该cv的名字

        params = cv_data.get('params', '')
        tokens = params.split()

        atoms = []
        numerical_derivatives = False
        nopbc = False

        for token in tokens:
            if token.startswith("ATOMS="):
                atoms = token[len("ATOMS="):].split(',')
            elif token == "NUMERICAL_DERIVATIVES":
                numerical_derivatives = True
            elif token == "NOPBC":
                nopbc = True

        if atoms:
            try:
                self.atom1_selection.set_selection(atoms[0])
                self.atom2_selection.set_selection(atoms[1])
                self.atom3_selection.set_selection(atoms[2])
                if len(atoms) == 4:
                    self.atom4_selection.set_selection(atoms[3])
                else:
                    self.atom4_selection.set_selection("")
            except:
                QtWidgets.QMessageBox.warning(self, "警告", "ATOMS 格式错误。")

        if numerical_derivatives or nopbc:
            self.adv_box.setChecked(True)
            self.numerical_derivatives_checkbox.setChecked(numerical_derivatives)
            self.nopbc_checkbox.setChecked(nopbc)
        else:
            self.adv_box.setChecked(False)
            self.numerical_derivatives_checkbox.setChecked(False)
            self.nopbc_checkbox.setChecked(False)
