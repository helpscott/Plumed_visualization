"""
dipole_page.py
计算一组原子的偶极矩 (DIPOLE)
"""

from PyQt5 import QtWidgets, QtCore
from ...mode_definitions.atom_range import AtomRangeWidget
from ...mode_definitions.single_atom_list import SingleAtomListWidget

class DipolePage(QtWidgets.QWidget):
    """
    DIPOLE:
      - GROUP=xxx
      - 关键字选项: NUMERICAL_DERIVATIVES, NOPBC, COMPONENTS
    """

    def __init__(self, group_labels, parent=None):
        super().__init__(parent)
        self.group_labels = group_labels
        self.cv_name = ""

        layout = QtWidgets.QVBoxLayout(self)

        # 提示
        self.prompt_label = QtWidgets.QLabel("计算偶极矩 (DIPOLE)")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.prompt_label)

        # GROUP(选择模式=范围 or 单原子列表)
        groupbox = QtWidgets.QGroupBox("GROUP (选择原子)")
        groupbox_layout = QtWidgets.QVBoxLayout(groupbox)

        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["范围模式", "单原子列表模式"])
        groupbox_layout.addWidget(self.mode_combo)

        self.stack = QtWidgets.QStackedWidget()
        groupbox_layout.addWidget(self.stack)

        # 两种模式Widget
        self.range_widget = AtomRangeWidget(self.group_labels)
        self.single_widget = SingleAtomListWidget(self.group_labels)

        self.stack.addWidget(self.range_widget)
        self.stack.addWidget(self.single_widget)

        # 切换
        self.mode_combo.currentIndexChanged.connect(self.stack.setCurrentIndex)

        layout.addWidget(groupbox)

        # 高级参数(可选)
        self.adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        self.adv_box.setCheckable(True)
        self.adv_box.setChecked(False)
        self.adv_layout = QtWidgets.QFormLayout(self.adv_box)

        self.numerical_cb = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 增加中文悬浮说明
        self.numerical_cb.setToolTip("启用数值方式计算导数（默认关闭）")
        self.adv_layout.addRow(self.numerical_cb)

        self.nopbc_cb = QtWidgets.QCheckBox("NOPBC")
        # 增加中文悬浮说明
        self.nopbc_cb.setToolTip("忽略周期性边界条件来计算距离（默认关闭）")
        self.adv_layout.addRow(self.nopbc_cb)

        self.components_cb = QtWidgets.QCheckBox("COMPONENTS (输出 x,y,z)")
        # 增加中文悬浮说明
        self.components_cb.setToolTip("将偶极矩的 x, y, z 分量分别存储为 label.x, label.y, label.z（默认关闭）")
        self.adv_layout.addRow(self.components_cb)

        layout.addWidget(self.adv_box)
        layout.addStretch()

    def set_cv_name(self, name):
        self.cv_name = name

    def get_cv_output(self):
        """
        默认输出属性 = [cv_name]
        如果COMPONENTS勾选, 输出属性再增加 [cv_name+".x", cv_name+".y", cv_name+".z"]
        """
        if not self.cv_name:
            return []

        outs = [self.cv_name]
        if self.adv_box.isChecked() and self.components_cb.isChecked():
            outs.append(f"{self.cv_name}.x")
            outs.append(f"{self.cv_name}.y")
            outs.append(f"{self.cv_name}.z")
        return outs

    def get_definition_line(self):
        """
        生成 "GROUP=xxx NUMERICAL_DERIVATIVES NOPBC COMPONENTS" ...
        """
        # 读取 GROUP
        if self.stack.currentIndex() == 0:
            # 范围模式
            group_str = self.range_widget.get_str()
        else:
            # 单原子列表
            atoms = self.single_widget.get_atoms()
            group_str = ",".join(atoms)

        if not group_str:
            QtWidgets.QMessageBox.warning(self, "警告", "请指定DIPOLE的 GROUP！")
            return None

        line = f"GROUP={group_str}"

        if self.adv_box.isChecked():
            if self.numerical_cb.isChecked():
                line += " NUMERICAL_DERIVATIVES"
            if self.nopbc_cb.isChecked():
                line += " NOPBC"
            if self.components_cb.isChecked():
                line += " COMPONENTS"

        return line

    def populate_data(self, cv_data):
        """
        从 cv_data['params'] 中解析
        GROUP=xxx ...
        """
        params = cv_data.get('params', '')
        tokens = params.split()

        group_val = ""
        numerical_flag = False
        nopbc_flag = False
        comp_flag = False

        for token in tokens:
            if token.startswith("GROUP="):
                group_val = token[len("GROUP="):]
            elif token == "NUMERICAL_DERIVATIVES":
                numerical_flag = True
            elif token == "NOPBC":
                nopbc_flag = True
            elif token == "COMPONENTS":
                comp_flag = True

        # 回填高级
        if numerical_flag or nopbc_flag or comp_flag:
            self.adv_box.setChecked(True)
            self.numerical_cb.setChecked(numerical_flag)
            self.nopbc_cb.setChecked(nopbc_flag)
            self.components_cb.setChecked(comp_flag)
        else:
            self.adv_box.setChecked(False)
            self.numerical_cb.setChecked(False)
            self.nopbc_cb.setChecked(False)
            self.components_cb.setChecked(False)

        # 解析 group_val
        if '-' in group_val or (group_val.isdigit() and len(group_val) > 0):
            self.mode_combo.setCurrentIndex(0)  # 范围模式
            self.range_widget.set_definition(group_val)
        else:
            self.mode_combo.setCurrentIndex(1)  # 单原子列表
            atoms = group_val.split(',')
            self.single_widget.clear_all_atoms()
            for a in atoms:
                if a.strip():
                    self.single_widget.add_atom(a.strip())
