from PyQt5 import QtWidgets, QtCore
from ..mode_definitions.atom_selection import AtomSelectionWidget

class GhostPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("计算一个具有固定坐标的鬼原子在三个原子构成的局部参考系中的绝对位置。")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.prompt_label)

        self.atoms_group = QtWidgets.QGroupBox("ATOMS (选择三个参考原子)")
        atoms_layout = QtWidgets.QFormLayout(self.atoms_group)

        self.atom1_selection = AtomSelectionWidget([])
        atoms_layout.addRow("Atom 1:", self.atom1_selection)

        self.atom2_selection = AtomSelectionWidget([])
        atoms_layout.addRow("Atom 2:", self.atom2_selection)

        self.atom3_selection = AtomSelectionWidget([])
        atoms_layout.addRow("Atom 3:", self.atom3_selection)

        self.layout.addWidget(self.atoms_group)

        self.coordinates_group = QtWidgets.QGroupBox("COORDINATES")
        coord_layout = QtWidgets.QFormLayout(self.coordinates_group)

        self.coord_x = QtWidgets.QDoubleSpinBox()
        self.coord_x.setRange(-999999, 999999)
        self.coord_x.setDecimals(3)
        coord_layout.addRow("X:", self.coord_x)

        self.coord_y = QtWidgets.QDoubleSpinBox()
        self.coord_y.setRange(-999999, 999999)
        self.coord_y.setDecimals(3)
        coord_layout.addRow("Y:", self.coord_y)

        self.coord_z = QtWidgets.QDoubleSpinBox()
        self.coord_z.setRange(-999999, 999999)
        self.coord_z.setDecimals(3)
        coord_layout.addRow("Z:", self.coord_z)

        self.layout.addWidget(self.coordinates_group)

    def get_definition_line(self):
        atom1 = self.atom1_selection.get_selection()
        atom2 = self.atom2_selection.get_selection()
        atom3 = self.atom3_selection.get_selection()
        coord_x = self.coord_x.value()
        coord_y = self.coord_y.value()
        coord_z = self.coord_z.value()

        if not atom1 or not atom2 or not atom3:
            QtWidgets.QMessageBox.warning(self, "警告", "请选择三个参考原子！")
            return None

        atoms = f"{atom1},{atom2},{atom3}"
        coordinates = f"{coord_x},{coord_y},{coord_z}"
        params = f"ATOMS={atoms} COORDINATES={coordinates}"
        return params

    def populate_data(self, group_data):
        params = group_data.get('params', '')
        tokens = params.split()

        atoms = ""
        coordinates = ""

        for token in tokens:
            if token.startswith("ATOMS="):
                atoms = token[len("ATOMS="):]
            elif token.startswith("COORDINATES="):
                coordinates = token[len("COORDINATES="):]

        if atoms:
            try:
                atom1, atom2, atom3 = atoms.split(',')
                self.atom1_selection.set_selection(atom1)
                self.atom2_selection.set_selection(atom2)
                self.atom3_selection.set_selection(atom3)
            except:
                QtWidgets.QMessageBox.warning(self, "警告", "ATOMS 格式错误。")

        if coordinates:
            try:
                x, y, z = map(float, coordinates.split(','))
                self.coord_x.setValue(x)
                self.coord_y.setValue(y)
                self.coord_z.setValue(z)
            except:
                QtWidgets.QMessageBox.warning(self, "警告", "COORDINATES 格式错误。")
