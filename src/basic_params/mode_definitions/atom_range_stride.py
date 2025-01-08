# src/basic_params/mode_definitions/atom_range_stride.py

from PyQt5 import QtWidgets

class AtomRangeStrideWidget(QtWidgets.QWidget):
    """
    范围+步长模式（模式3）仅用于GROUP
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        form = QtWidgets.QFormLayout(self)
        self.start_spin = QtWidgets.QSpinBox()
        self.start_spin.setRange(1, 999999)
        self.start_spin.setValue(1)
        self.end_spin = QtWidgets.QSpinBox()
        self.end_spin.setRange(1, 999999)
        self.end_spin.setValue(100)
        self.stride_spin = QtWidgets.QSpinBox()
        self.stride_spin.setRange(1, 999999)
        self.stride_spin.setValue(36)
        form.addRow("起始原子:", self.start_spin)
        form.addRow("终止原子:", self.end_spin)
        form.addRow("步长:", self.stride_spin)

    def get_range_str(self):
        return f"{self.start_spin.value()}-{self.end_spin.value()}:{self.stride_spin.value()}"
