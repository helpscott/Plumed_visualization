# kt_widget.py

from PyQt5 import QtWidgets, QtCore

class KtWidget(QtWidgets.QWidget):
    """
    kt 工具界面：
      - 用于在给定温度下，打印 kBT 的数值
      - 必需参数:
         --temp (必填，用于指定温度)
         --units (默认=kj/mol，可为 kj/mol,kcal/mol,j/mol,eV 或转换因子)
      - 可选:
         --help/-h (打印帮助)
    当输入改变时，发出 params_changed 信号，以便上层刷新命令行。
    """
    params_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # 顶部说明
        desc_label = QtWidgets.QLabel("一个用于在特定温度下计算 kBT 值的工具")
        desc_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(desc_label)

        # 必需参数区域
        form_layout = QtWidgets.QFormLayout()

        self.temp_edit = QtWidgets.QLineEdit()
        self.temp_edit.setPlaceholderText("指定温度(必填)，例如 300")
        form_layout.addRow("--temp:", self.temp_edit)

        self.units_edit = QtWidgets.QLineEdit()
        self.units_edit.setPlaceholderText("能量单位,如 kj/mol,kcal/mol,j/mol,eV或转换因子(默认=kj/mol)")
        form_layout.addRow("--units:", self.units_edit)

        layout.addLayout(form_layout)

        # 可选布尔选项: --help/-h
        self.help_cb = QtWidgets.QCheckBox("--help")
        self.help_cb.setToolTip("打印此工具的帮助信息")
        layout.addWidget(self.help_cb)

        # 监听输入变化
        self.temp_edit.textChanged.connect(self.params_changed.emit)
        self.units_edit.textChanged.connect(self.params_changed.emit)
        self.help_cb.stateChanged.connect(self.params_changed.emit)

        self.setLayout(layout)

    def get_command_flags(self):
        """
        返回 kt 的 list_of_flags, 不包含 "plumed kt"
        """
        flags = []

        # --temp (必需)
        temp_val = self.temp_edit.text().strip()
        if temp_val:
            flags.append("--temp")
            flags.append(temp_val)

        # --units (默认=kj/mol)
        units_val = self.units_edit.text().strip()
        if units_val:
            flags.append("--units")
            flags.append(units_val)

        # --help
        if self.help_cb.isChecked():
            flags.append("--help")

        return flags
