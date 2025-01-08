# src/basic_params/mode_definitions/atom_range.py

from PyQt5 import QtWidgets, QtCore

class AtomRangeWidget(QtWidgets.QWidget):
    def __init__(self, groups, parent=None):
        super().__init__(parent)
        self.groups = groups
        self.init_ui()

    def init_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)

        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["使用数字范围", "使用已定义的组"])
        self.layout.addWidget(self.mode_combo)

        self.range_widget = QtWidgets.QWidget()
        range_layout = QtWidgets.QFormLayout(self.range_widget)
        self.start_spin = QtWidgets.QSpinBox()
        self.start_spin.setRange(1, 999999)
        self.start_spin.setValue(1)
        self.end_spin = QtWidgets.QSpinBox()
        self.end_spin.setRange(1, 999999)
        self.end_spin.setValue(10)
        range_layout.addRow("起始原子:", self.start_spin)
        range_layout.addRow("终止原子:", self.end_spin)

        self.group_widget = QtWidgets.QWidget()
        group_layout = QtWidgets.QFormLayout(self.group_widget)
        self.group_combo = QtWidgets.QComboBox()
        if not self.groups:
            self.group_combo.addItem("(暂无已定义的组)")
            self.group_combo.setEnabled(False)
        else:
            self.group_combo.addItems(self.groups)
        group_layout.addRow("选择已有组:", self.group_combo)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.range_widget)
        self.stack.addWidget(self.group_widget)
        self.layout.addWidget(self.stack)

        self.mode_combo.currentIndexChanged.connect(self.stack.setCurrentIndex)
        self.stack.setCurrentIndex(0)

    def get_str(self):
        idx = self.mode_combo.currentIndex()
        if idx == 0:
            start = self.start_spin.value()
            end = self.end_spin.value()
            if end < start:
                QtWidgets.QMessageBox.warning(self, "警告", "终止原子编号必须大于或等于起始原子编号！")
                return None
            return f"{start}-{end}"
        else:
            if self.group_combo.isEnabled():
                selected_group = self.group_combo.currentText().strip()
                if not selected_group:
                    QtWidgets.QMessageBox.warning(self, "警告", "请选择一个已定义的组！")
                    return None
                return selected_group
            else:
                QtWidgets.QMessageBox.warning(self, "警告", "暂无可用的已定义组！")
                return None

    def set_definition(self, definition_str):
        if '-' in definition_str and ':' in definition_str:
            pass
        elif '-' in definition_str:
            try:
                start, end = map(int, definition_str.split('-'))
                self.mode_combo.setCurrentIndex(0)
                self.start_spin.setValue(start)
                self.end_spin.setValue(end)
            except ValueError:
                pass
                # QtWidgets.QMessageBox.warning(self, "警告", "ATOMS 格式错误。")
        else:
            group = definition_str
            if group in self.groups:
                self.mode_combo.setCurrentIndex(1)
                self.group_combo.setCurrentText(group)
            else:
                pass

    def clear_definition(self):
        self.mode_combo.setCurrentIndex(0)
        self.start_spin.setValue(1)
        self.end_spin.setValue(10)
        if self.groups:
            self.group_combo.setCurrentIndex(0)
