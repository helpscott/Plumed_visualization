# src/basic_params/mode_definitions/single_atom_list.py

from PyQt5 import QtWidgets

class SingleAtomListWidget(QtWidgets.QWidget):
    """
    单原子列表模式：可添加原子编号或已定义的单原子虚拟原子label。
    不允许添加组label。
    """
    def __init__(self, single_atoms, parent=None):
        super().__init__(parent)
        self.single_atoms = single_atoms  # 已定义的单原子虚拟原子label列表
        v_layout = QtWidgets.QVBoxLayout(self)

        self.list_widget = QtWidgets.QListWidget()
        v_layout.addWidget(self.list_widget)

        btn_layout = QtWidgets.QHBoxLayout()
        self.add_atom_btn = QtWidgets.QPushButton("增加原子/单原子虚拟原子")
        self.remove_atom_btn = QtWidgets.QPushButton("删除选中项")
        btn_layout.addWidget(self.add_atom_btn)
        btn_layout.addWidget(self.remove_atom_btn)
        v_layout.addLayout(btn_layout)

        self.add_atom_btn.clicked.connect(self.add_item)
        self.remove_atom_btn.clicked.connect(self.remove_item)

    def add_item(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("选择添加类型")
        layout = QtWidgets.QVBoxLayout(dialog)

        btn_atom = QtWidgets.QPushButton("添加原子编号")
        btn_single = QtWidgets.QPushButton("添加单原子虚拟原子(label)")
        layout.addWidget(btn_atom)
        layout.addWidget(btn_single)

        def atom_clicked():
            dialog.accept()
            val, ok = QtWidgets.QInputDialog.getInt(self, "添加原子", "输入原子编号:", 1, 1, 999999, 1)
            if ok:
                # 检查是否已存在
                items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
                if str(val) in items:
                    QtWidgets.QMessageBox.warning(self, "警告", f"原子编号 {val} 已存在。")
                else:
                    self.list_widget.addItem(str(val))

        def single_clicked():
            dialog.accept()
            if not self.single_atoms:
                QtWidgets.QMessageBox.warning(self, "警告", "暂无已定义的单原子虚拟原子可选。")
                return
            s_item, ok = QtWidgets.QInputDialog.getItem(self, "添加单原子虚拟原子", "选择label:", self.single_atoms, 0, False)
            if ok and s_item:
                # 检查是否已存在
                items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
                if s_item in items:
                    QtWidgets.QMessageBox.warning(self, "警告", f"单原子虚拟原子 '{s_item}' 已存在。")
                else:
                    self.list_widget.addItem(s_item)

        btn_atom.clicked.connect(atom_clicked)
        btn_single.clicked.connect(single_clicked)

        dialog.exec_()

    def remove_item(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, "警告", "请选择要删除的项。")
            return
        for item in selected_items:
            self.list_widget.takeItem(self.list_widget.row(item))

    def get_atoms(self):
        atoms = []
        for i in range(self.list_widget.count()):
            atoms.append(self.list_widget.item(i).text())
        return atoms

    def clear_all_atoms(self):
        self.list_widget.clear()

    def add_atom(self, atom):
        self.list_widget.addItem(atom)

    def populate_data(self, params):
        """
        根据传入的参数填充列表。
        params: str, 例如 "1,2,3"
        """
        self.clear_all_atoms()
        atoms = params.split(',')
        for atom in atoms:
            atom = atom.strip()
            if atom:
                self.list_widget.addItem(atom)
