"""
group_control.py
负责原子群组的控制逻辑
"""
from PyQt5 import QtWidgets
from .group_definitions.com_center import ComPage, CenterPage
from .group_definitions.fixed_atom import FixedAtomPage
from .group_definitions.ghost import GhostPage
from .group_definitions.group import GroupPage

class GroupDefinitionDialog(QtWidgets.QDialog):
    def __init__(self, existing_single_atoms, existing_groups, group_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("原子群组定义")
        self.existing_single_atoms = existing_single_atoms
        self.existing_groups = existing_groups
        self.group_data = group_data

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()
        self.name_edit = QtWidgets.QLineEdit()
        form_layout.addRow("名称:", self.name_edit)

        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["COM", "CENTER", "FIXEDATOM", "GHOST", "GROUP"])
        form_layout.addRow("类型:", self.type_combo)

        self.stack = QtWidgets.QStackedWidget()
        form_layout.addRow(self.stack)

        self.pages = {}
        for t in ["COM", "CENTER", "FIXEDATOM", "GHOST", "GROUP"]:
            pg = self.create_page_for_type(t)
            self.stack.addWidget(pg)
            self.pages[t] = pg

        self.type_combo.currentTextChanged.connect(lambda txt: self.stack.setCurrentWidget(self.pages[txt]))

        layout.addLayout(form_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("保存")
        self.cancel_btn = QtWidgets.QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        if self.group_data:
            self.populate_data()

        self.setLayout(layout)

    def populate_data(self):
        self.name_edit.setText(self.group_data['name'])
        self.type_combo.setCurrentText(self.group_data['type'])
        current_page = self.pages[self.group_data['type']]
        current_page.populate_data(self.group_data)

    def create_page_for_type(self, t):
        if t == "COM":
            return ComPage(self.existing_single_atoms, self.existing_groups)
        elif t == "CENTER":
            return CenterPage(self.existing_single_atoms, self.existing_groups)
        elif t == "FIXEDATOM":
            return FixedAtomPage()
        elif t == "GHOST":
            return GhostPage()
        elif t == "GROUP":
            return GroupPage(self.existing_single_atoms, self.existing_groups)
        else:
            return QtWidgets.QWidget()

    def get_group_data(self):
        name = self.name_edit.text().strip()
        cmd = self.type_combo.currentText()
        params = self.pages[cmd].get_definition_line()
        if not name or not cmd or (cmd != "VOLUME" and not params):
            QtWidgets.QMessageBox.warning(self, "警告", "群组定义不完整！")
            return None
        return {'name': name, 'type': cmd, 'params': params}

    def get_definition_line(self):
        group_data = self.get_group_data()
        if group_data:
            return f"{group_data['name']}: {group_data['type']} {group_data['params']}"
        else:
            return None
