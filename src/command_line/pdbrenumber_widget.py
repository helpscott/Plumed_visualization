# pdbrenumber_widget.py

from PyQt5 import QtWidgets, QtCore

class PdbRenumberWidget(QtWidgets.QWidget):
    """
    pdbrenumber 工具界面：
      - 用于修改PDB文件中的原子编号(atom serial numbers)，可能会用到 hybrid-36 编码
      - 强制必需参数：
          --ipdb (输入文件), --opdb (输出文件)
      - 可选参数：
          --help/-h, --firstatomnumber, --atomnumbers
      当输入发生变化时，发出 params_changed 信号，上层可更新命令行。
    """
    params_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # 顶部说明
        desc_label = QtWidgets.QLabel("一个用于修改PDB文件中原子编号的工具，可使用hybrid-36编码")
        desc_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(desc_label)

        # 强制必需参数：--ipdb, --opdb
        mandatory_form = QtWidgets.QFormLayout()

        self.ipdb_edit = QtWidgets.QLineEdit()
        self.ipdb_edit.setPlaceholderText("输入PDB文件名 (如 input.pdb)")
        mandatory_form.addRow("--ipdb:", self.ipdb_edit)

        self.opdb_edit = QtWidgets.QLineEdit()
        self.opdb_edit.setPlaceholderText("输出PDB文件名 (如 output.pdb)")
        mandatory_form.addRow("--opdb:", self.opdb_edit)

        layout.addLayout(mandatory_form)

        # 其它可选参数：--help/-h, --firstatomnumber, --atomnumbers
        optional_form = QtWidgets.QFormLayout()

        self.firstatomnumber_edit = QtWidgets.QLineEdit()
        self.firstatomnumber_edit.setPlaceholderText("指定输出文件中第一个原子的编号(默认=1)")
        optional_form.addRow("--firstatomnumber:", self.firstatomnumber_edit)

        self.atomnumbers_edit = QtWidgets.QLineEdit()
        self.atomnumbers_edit.setPlaceholderText("指定包含原子编号列表的文件(list.txt)，一行一个编号")
        optional_form.addRow("--atomnumbers:", self.atomnumbers_edit)

        layout.addLayout(optional_form)

        # --help/-h
        self.help_cb = QtWidgets.QCheckBox("--help/-h")
        self.help_cb.setToolTip("打印帮助信息(help)")
        layout.addWidget(self.help_cb)

        # 信号连接
        all_lineedits = [self.ipdb_edit, self.opdb_edit,
                         self.firstatomnumber_edit, self.atomnumbers_edit]
        for w in all_lineedits:
            w.textChanged.connect(self.params_changed.emit)

        self.help_cb.stateChanged.connect(self.params_changed.emit)

        self.setLayout(layout)

    def get_command_flags(self):
        """
        返回 pdbrenumber 的 list_of_flags, 不包含 "plumed pdbrenumber"
        """
        flags = []

        # --ipdb (必需)
        ipdb_val = self.ipdb_edit.text().strip()
        if ipdb_val:
            flags.append("--ipdb")
            flags.append(ipdb_val)

        # --opdb (必需)
        opdb_val = self.opdb_edit.text().strip()
        if opdb_val:
            flags.append("--opdb")
            flags.append(opdb_val)

        # --firstatomnumber
        fan_val = self.firstatomnumber_edit.text().strip()
        if fan_val:
            flags.append("--firstatomnumber")
            flags.append(fan_val)

        # --atomnumbers
        an_val = self.atomnumbers_edit.text().strip()
        if an_val:
            flags.append("--atomnumbers")
            flags.append(an_val)

        # --help/-h
        if self.help_cb.isChecked():
            flags.append("--help")

        return flags
