from PyQt5 import QtWidgets, QtCore
from ..mode_definitions.single_atom_list import SingleAtomListWidget
from ..mode_definitions.atom_range import AtomRangeWidget
from ..mode_definitions.atom_range_stride import AtomRangeStrideWidget

class AdvancedSettingsDialog(QtWidgets.QDialog):
    """
    如果需要更多高级设置，可在此扩展，目前本例暂不使用。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("高级参数")
        layout = QtWidgets.QVBoxLayout(self)

        # 如果要加更多选项，可自己扩展
        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("确定")
        self.cancel_btn = QtWidgets.QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)


class GroupWidget(QtWidgets.QWidget):
    def __init__(self, single_atoms, groups, parent=None):
        super().__init__(parent)
        self.single_atoms = single_atoms
        self.groups = groups

        v = QtWidgets.QVBoxLayout(self)
        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["单原子列表模式", "范围模式", "范围+步长模式"])
        v.addWidget(self.mode_combo)

        self.single_widget = SingleAtomListWidget(self.single_atoms)
        self.range_widget = AtomRangeWidget(self.groups)
        self.rangest_widget = AtomRangeStrideWidget()

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.single_widget)   # idx=0
        self.stack.addWidget(self.range_widget)    # idx=1
        self.stack.addWidget(self.rangest_widget)  # idx=2
        v.addWidget(self.stack)

        self.mode_combo.currentIndexChanged.connect(self.stack.setCurrentIndex)
        # 缺省设为index=1(范围模式)
        self.mode_combo.setCurrentIndex(1)

    def get_definition_line(self):
        """
        返回ATOMS=xxx的右侧那部分定义
        """
        idx = self.mode_combo.currentIndex()
        if idx == 0:
            # 单原子列表
            atoms = self.single_widget.get_atoms()
            return ",".join(atoms) if atoms else ""
        elif idx == 1:
            # 范围模式
            return self.range_widget.get_str()
        else:
            # 范围+步长
            return self.rangest_widget.get_range_str()

    def set_definition(self, atoms_str):
        """
        将已有的ATOMS定义还原
        """
        if '-' in atoms_str and ':' in atoms_str:
            # 说明是范围+步长
            try:
                range_part, stride = atoms_str.split(':')
                start, end = range_part.split('-')
                self.mode_combo.setCurrentIndex(2)
                self.stack.setCurrentIndex(2)
                self.rangest_widget.start_spin.setValue(int(start))
                self.rangest_widget.end_spin.setValue(int(end))
                self.rangest_widget.stride_spin.setValue(int(stride))
            except ValueError:
                pass
        elif '-' in atoms_str:
            # 说明是范围模式
            self.mode_combo.setCurrentIndex(1)
            self.stack.setCurrentIndex(1)
            self.range_widget.set_definition(atoms_str)
        else:
            # 说明是单原子列表
            self.mode_combo.setCurrentIndex(0)
            self.stack.setCurrentIndex(0)
            self.single_widget.clear_all_atoms()
            for atom in atoms_str.split(','):
                self.single_widget.add_atom(atom.strip())

    def populate_data(self, group_data):
        """
        用于GroupPage调用，传入 {'type':..., 'params':...}
        解析出 ATOMS=xxx 并还原
        """
        params = group_data.get('params', '')
        tokens = params.split()
        # 例如 "ATOMS=1,2,3 REMOVE=4,5 SORT UNIQUE"
        # 只解析出ATOMS=xxx
        at_expr = ""
        for t in tokens:
            if t.startswith("ATOMS="):
                at_expr = t[len("ATOMS="):]
        if at_expr:
            self.set_definition(at_expr)


class GroupPage(QtWidgets.QWidget):
    """
    定义一组原子。
    """
    def __init__(self, single_atoms, groups, parent=None):
        super().__init__(parent)
        self.single_atoms = single_atoms
        self.groups = groups

        layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("定义一组原子。")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.prompt_label)

        # 基本的原子定义widget
        self.group_widget = GroupWidget(self.single_atoms, self.groups)
        layout.addWidget(self.group_widget)

        # 高级参数(可选)
        self.adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        self.adv_box.setCheckable(True)
        self.adv_box.setChecked(False)
        self.adv_layout = QtWidgets.QVBoxLayout(self.adv_box)

        # REMOVE
        self.remove_checkbox = QtWidgets.QCheckBox("REMOVE")
        # 添加中文鼠标悬浮提示
        self.remove_checkbox.setToolTip(
            "从列表中移除这些原子。可使用和ATOMS类似的语法指定原子范围或列表。"
        )
        self.remove_widget = GroupWidget(self.single_atoms, self.groups)
        self.remove_widget.setEnabled(False)
        self.adv_layout.addWidget(self.remove_checkbox)
        self.adv_layout.addWidget(self.remove_widget)

        # NDX_FILE
        self.ndx_file_checkbox = QtWidgets.QCheckBox("NDX_FILE")
        self.ndx_file_widget = QtWidgets.QWidget()
        ndx_file_layout = QtWidgets.QHBoxLayout(self.ndx_file_widget)
        self.ndx_file_line = QtWidgets.QLineEdit()
        # 中文placeholder说明
        self.ndx_file_line.setPlaceholderText("指定gromacs索引文件(.ndx)的路径")
        self.ndx_file_btn = QtWidgets.QPushButton("选择文件")
        ndx_file_layout.addWidget(self.ndx_file_line)
        ndx_file_layout.addWidget(self.ndx_file_btn)
        self.ndx_file_widget.setEnabled(False)
        self.adv_layout.addWidget(self.ndx_file_checkbox)
        self.adv_layout.addWidget(self.ndx_file_widget)

        # NDX_GROUP
        self.ndx_group_checkbox = QtWidgets.QCheckBox("NDX_GROUP")
        self.ndx_group_line = QtWidgets.QLineEdit()
        self.ndx_group_line.setPlaceholderText("指定索引文件中的组名(不指定则使用第一组)")
        self.ndx_group_line.setEnabled(False)
        self.adv_layout.addWidget(self.ndx_group_checkbox)
        self.adv_layout.addWidget(self.ndx_group_line)

        # SORT
        self.sort_checkbox = QtWidgets.QCheckBox("SORT")
        # 添加中文鼠标悬浮提示
        self.sort_checkbox.setToolTip(
            "对结果列表进行排序 (默认关闭)"
        )
        self.sort_checkbox.setEnabled(True)
        self.adv_layout.addWidget(self.sort_checkbox)

        # UNIQUE
        self.unique_checkbox = QtWidgets.QCheckBox("UNIQUE")
        # 添加中文鼠标悬浮提示
        self.unique_checkbox.setToolTip(
            "对结果列表进行去重并排序 (默认关闭)"
        )
        self.unique_checkbox.setEnabled(True)
        self.adv_layout.addWidget(self.unique_checkbox)

        layout.addWidget(self.adv_box)

        self.remove_checkbox.stateChanged.connect(self.toggle_remove)
        self.ndx_file_checkbox.stateChanged.connect(self.toggle_ndx_file)
        self.ndx_group_checkbox.stateChanged.connect(self.toggle_ndx_group)
        self.sort_checkbox.stateChanged.connect(self.toggle_sort)
        self.unique_checkbox.stateChanged.connect(self.toggle_unique)
        self.ndx_file_btn.clicked.connect(self.choose_ndx_file)

        layout.addStretch()

    def toggle_remove(self, state):
        if state == QtCore.Qt.Checked:
            self.remove_widget.setEnabled(True)
        else:
            self.remove_widget.setEnabled(False)
            self.remove_widget.set_definition("")

    def toggle_ndx_file(self, state):
        if state == QtCore.Qt.Checked:
            self.ndx_file_widget.setEnabled(True)
        else:
            self.ndx_file_widget.setEnabled(False)
            self.ndx_file_line.clear()

    def toggle_ndx_group(self, state):
        if state == QtCore.Qt.Checked:
            self.ndx_group_line.setEnabled(True)
        else:
            self.ndx_group_line.setEnabled(False)
            self.ndx_group_line.clear()

    def toggle_sort(self, state):
        pass

    def toggle_unique(self, state):
        pass

    def choose_ndx_file(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "选择NDX文件", "",
            "NDX Files (*.ndx);;All Files (*)"
        )
        if fname:
            self.ndx_file_line.setText(fname)

    def get_definition_line(self):
        """
        生成最终 params，如：
        ATOMS=1-10 REMOVE=2,3 NDX_FILE=xxx.ndx NDX_GROUP=xxx SORT UNIQUE
        """
        group_atoms = self.group_widget.get_definition_line()
        if not group_atoms:
            QtWidgets.QMessageBox.warning(self, "警告", "请定义ATOMS参数！")
            return None
        params = f"ATOMS={group_atoms}"

        if self.remove_checkbox.isChecked():
            remove_atoms = self.remove_widget.get_definition_line()
            if not remove_atoms:
                QtWidgets.QMessageBox.warning(self, "警告", "请定义REMOVE参数！")
                return None
            params += f" REMOVE={remove_atoms}"

        if self.ndx_file_checkbox.isChecked():
            ndx_file = self.ndx_file_line.text().strip()
            if not ndx_file:
                QtWidgets.QMessageBox.warning(self, "警告", "请指定NDX_FILE文件！")
                return None
            params += f" NDX_FILE={ndx_file}"

        if self.ndx_group_checkbox.isChecked():
            ndx_group = self.ndx_group_line.text().strip()
            if not ndx_group:
                QtWidgets.QMessageBox.warning(self, "警告", "请指定NDX_GROUP名称！")
                return None
            params += f" NDX_GROUP={ndx_group}"

        if self.sort_checkbox.isChecked():
            params += " SORT"
        if self.unique_checkbox.isChecked():
            params += " UNIQUE"

        return params

    def populate_data(self, group_data):
        """
        回显已有的Group定义
        """
        # 先让 group_widget 解析 ATOMS=xxx
        self.group_widget.populate_data(group_data)

        # 然后解析 REMOVE=xxx / NDX_FILE=xxx / NDX_GROUP=xxx / SORT / UNIQUE
        params = group_data.get('params', '')
        tokens = params.split()

        self.remove_checkbox.setChecked(False)
        self.ndx_file_checkbox.setChecked(False)
        self.ndx_group_checkbox.setChecked(False)
        self.sort_checkbox.setChecked(False)
        self.unique_checkbox.setChecked(False)

        self.remove_widget.set_definition("")
        self.ndx_file_line.clear()
        self.ndx_group_line.clear()

        for token in tokens:
            if token.startswith("REMOVE="):
                remove_atoms = token[len("REMOVE="):]
                self.remove_checkbox.setChecked(True)
                self.remove_widget.set_definition(remove_atoms)
            elif token.startswith("NDX_FILE="):
                ndx_file = token[len("NDX_FILE="):]
                self.ndx_file_checkbox.setChecked(True)
                self.ndx_file_widget.setEnabled(True)
                self.ndx_file_line.setText(ndx_file)
            elif token.startswith("NDX_GROUP="):
                ndx_group = token[len("NDX_GROUP="):]
                self.ndx_group_checkbox.setChecked(True)
                self.ndx_group_line.setEnabled(True)
                self.ndx_group_line.setText(ndx_group)
            elif token == "SORT":
                self.sort_checkbox.setChecked(True)
            elif token == "UNIQUE":
                self.unique_checkbox.setChecked(True)
