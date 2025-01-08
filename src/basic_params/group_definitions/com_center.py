from PyQt5 import QtWidgets, QtCore
from ..mode_definitions.atom_range import AtomRangeWidget
from ..mode_definitions.single_atom_list import SingleAtomListWidget

class ComCenterBasePage(QtWidgets.QWidget):
    def __init__(self, single_atoms, groups, parent=None):
        super().__init__(parent)
        self.single_atoms = single_atoms
        self.groups = groups
        self.layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel()
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.prompt_label)

        # 切换按钮，用于在“范围模式(AtomRangeWidget)”和“单原子列表模式(SingleAtomListWidget)”之间切换
        self.mode_btn = QtWidgets.QPushButton("切换到单原子列表模式")
        self.layout.addWidget(self.mode_btn)

        self.range_widget = AtomRangeWidget(self.groups)
        self.single_widget = SingleAtomListWidget(self.single_atoms)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.range_widget)    # index = 0
        self.stack.addWidget(self.single_widget)   # index = 1
        self.layout.addWidget(self.stack)

        # 当前模式，可为 "range" 或 "single"
        self.current_mode = "range"
        self.mode_btn.clicked.connect(self.toggle_mode)

        # 高级参数区域
        self.adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        self.adv_box.setCheckable(True)
        self.adv_box.setChecked(False)
        self.adv_layout = QtWidgets.QFormLayout(self.adv_box)

        self.nopbc_checkbox = QtWidgets.QCheckBox("NOPBC")
        self.mass_checkbox = QtWidgets.QCheckBox("MASS")
        self.phases_checkbox = QtWidgets.QCheckBox("PHASES")
        self.weights_checkbox = QtWidgets.QCheckBox("WEIGHTS")

        # ---------------- 这里添加中文鼠标悬浮提示 ----------------
        self.nopbc_checkbox.setToolTip("在计算距离时忽略周期性边界条件 (NOPBC)")
        self.mass_checkbox.setToolTip("若勾选，则使用质量加权来计算中心 (MASS)")
        self.phases_checkbox.setToolTip("使用三角函数相位来计算中心 (PHASES)")
        self.weights_checkbox.setToolTip("以加权平均方式计算中心 (WEIGHTS)")
        # -------------------------------------------------------

        self.adv_layout.addRow(self.nopbc_checkbox)
        self.adv_layout.addRow(self.mass_checkbox)
        self.adv_layout.addRow(self.phases_checkbox)
        self.adv_layout.addRow(self.weights_checkbox)

        self.weights_input = QtWidgets.QLineEdit()
        self.weights_input.setPlaceholderText("输入权重，以逗号分隔（例如: 2,1）")
        self.weights_input.setEnabled(False)
        self.adv_layout.addRow("Weights:", self.weights_input)

        self.weights_checkbox.stateChanged.connect(self.toggle_weights_input)

        self.layout.addWidget(self.adv_box)
        self.layout.addStretch()

    def toggle_mode(self):
        """
        在 range 和 single 两种模式之间切换
        """
        if self.current_mode == "range":
            self.stack.setCurrentIndex(1)  # 切到 single_widget
            self.current_mode = "single"
            self.mode_btn.setText("切换到范围模式")
        else:
            self.stack.setCurrentIndex(0)  # 切到 range_widget
            self.current_mode = "range"
            self.mode_btn.setText("切换到单原子列表模式")

    def toggle_weights_input(self, state):
        """
        当“WEIGHTS”被选中时，启用 weights_input；否则禁用并清空
        """
        if state == QtCore.Qt.Checked:
            self.weights_input.setEnabled(True)
        else:
            self.weights_input.setEnabled(False)
            self.weights_input.clear()

    def get_definition_line(self):
        """
        根据当前界面状态拼接定义行
        """
        if self.current_mode == "range":
            group_selection = self.range_widget.get_str()
            if not group_selection:
                return None
            params = f"ATOMS={group_selection}"
        else:
            atoms = self.single_widget.get_atoms()
            if not atoms:
                QtWidgets.QMessageBox.warning(self, "警告", "请选择至少一个原子！")
                return None
            params = f"ATOMS={','.join(atoms)}"

        if self.adv_box.isChecked():
            if self.nopbc_checkbox.isChecked():
                params += " NOPBC"
            if self.mass_checkbox.isChecked():
                params += " MASS"
            if self.phases_checkbox.isChecked():
                params += " PHASES"
            if self.weights_checkbox.isChecked():
                weights_text = self.weights_input.text().strip()
                if not weights_text:
                    QtWidgets.QMessageBox.warning(self, "警告", "请为 WEIGHTS 输入权重值！")
                    return None
                params += f" WEIGHTS={weights_text}"

        return params

    def populate_data(self, group_data):
        """
        将已保存的参数回显到UI
        """
        params = group_data.get('params', '')
        tokens = params.split()

        # 默认是 range 模式
        self.current_mode = "range"
        self.stack.setCurrentIndex(0)
        self.mode_btn.setText("切换到单原子列表模式")

        # 解析 ATOMS=xxx
        group_selection = ""
        advanced_flags = []
        weights_str = ""

        for t in tokens:
            if t.startswith("ATOMS="):
                group_selection = t[len("ATOMS="):]
            elif t.startswith("WEIGHTS="):
                weights_str = t[len("WEIGHTS="):]
            elif t in ["NOPBC", "MASS", "PHASES", "WEIGHTS"]:
                advanced_flags.append(t)

        # 回显到 range/single widget
        if group_selection:
            # 简化逻辑：只要包含'-'就认为是range模式，否则单原子列表
            if '-' in group_selection:
                # range模式
                self.current_mode = "range"
                self.stack.setCurrentIndex(0)
                self.mode_btn.setText("切换到单原子列表模式")
                self.range_widget.set_definition(group_selection)
            else:
                # single模式
                self.current_mode = "single"
                self.stack.setCurrentIndex(1)
                self.mode_btn.setText("切换到范围模式")
                self.single_widget.clear_all_atoms()
                for atom in group_selection.split(','):
                    self.single_widget.add_atom(atom.strip())

        # 回显高级参数
        if advanced_flags or weights_str:
            self.adv_box.setChecked(True)
            self.nopbc_checkbox.setChecked("NOPBC" in advanced_flags)
            self.mass_checkbox.setChecked("MASS" in advanced_flags)
            self.phases_checkbox.setChecked("PHASES" in advanced_flags)

            if "WEIGHTS" in advanced_flags or weights_str:
                self.weights_checkbox.setChecked(True)
                self.weights_input.setEnabled(True)
                self.weights_input.setText(weights_str)
            else:
                self.weights_checkbox.setChecked(False)
                self.weights_input.setEnabled(False)
                self.weights_input.clear()
        else:
            self.adv_box.setChecked(False)
            self.nopbc_checkbox.setChecked(False)
            self.mass_checkbox.setChecked(False)
            self.phases_checkbox.setChecked(False)
            self.weights_checkbox.setChecked(False)
            self.weights_input.setEnabled(False)
            self.weights_input.clear()


class ComPage(ComCenterBasePage):
    def __init__(self, single_atoms, groups, parent=None):
        super().__init__(single_atoms, groups, parent=parent)
        self.prompt_label.setText("计算一组原子的质心。")

class CenterPage(ComCenterBasePage):
    def __init__(self, single_atoms, groups, parent=None):
        super().__init__(single_atoms, groups, parent=parent)
        self.prompt_label.setText("计算一组原子的几何中心。")
