from PyQt5 import QtWidgets, QtCore
from ...mode_definitions.atom_selection import AtomSelectionWidget

class PositionPage(QtWidgets.QWidget):
    """
    计算一个原子的位置。
    输入只能选择一个原子：AtomSelectionWidget
    高级参数: NUMERICAL_DERIVATIVES、NOPBC、SCALED_COMPONENTS (关键字型)
    输出:
      - 默认输出: name.x, name.y, name.z
      - 若选择SCALED_COMPONENTS, 增加输出: name.a, name.b, name.c
    """
    def __init__(self, group_labels, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("计算一个原子的位置")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.prompt_label)

        # 选择一个原子的输入
        self.atom_group = QtWidgets.QGroupBox("ATOM (选择一个参考原子)")
        atom_layout = QtWidgets.QFormLayout(self.atom_group)

        self.atom_selection = AtomSelectionWidget(group_labels)
        atom_layout.addRow("Atom:", self.atom_selection)

        self.layout.addWidget(self.atom_group)

        # 高级参数
        self.adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        self.adv_box.setCheckable(True)
        self.adv_box.setChecked(False)
        self.adv_layout = QtWidgets.QFormLayout(self.adv_box)

        # 1. NUMERICAL_DERIVATIVES
        self.numerical_derivatives_checkbox = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        self.numerical_derivatives_checkbox.setToolTip(
            "启用数值方式计算导数（默认关闭）"
        )
        self.adv_layout.addRow(self.numerical_derivatives_checkbox)

        # 2. NOPBC
        self.nopbc_checkbox = QtWidgets.QCheckBox("NOPBC")
        self.nopbc_checkbox.setToolTip(
            "忽略周期性边界条件来计算距离（默认关闭）"
        )
        self.adv_layout.addRow(self.nopbc_checkbox)

        # 3. SCALED_COMPONENTS
        self.scaled_components_checkbox = QtWidgets.QCheckBox("SCALED_COMPONENTS")
        self.scaled_components_checkbox.setToolTip(
            "将坐标的 a, b, c 缩放分量分别存储为 label.a, label.b, label.c（默认关闭）"
        )
        self.adv_layout.addRow(self.scaled_components_checkbox)

        self.layout.addWidget(self.adv_box)

        # 在Position中，输出属性默认是 name.x, name.y, name.z
        # 若勾选SCALED_COMPONENTS，则额外有 name.a, name.b, name.c
        self.cv_name = ""  # 用于存储CV名

    def set_cv_name(self, name):
        # 由CVDefinitionDialog保存后显式调用
        self.cv_name = name.strip()

    def get_definition_line(self):
        # ATOM=xxx
        atom_val = self.atom_selection.get_selection()
        if not atom_val:
            QtWidgets.QMessageBox.warning(self, "警告", "请填写ATOM！")
            return None

        params = f"ATOM={atom_val}"

        if self.adv_box.isChecked():
            if self.numerical_derivatives_checkbox.isChecked():
                params += " NUMERICAL_DERIVATIVES"
            if self.nopbc_checkbox.isChecked():
                params += " NOPBC"
            if self.scaled_components_checkbox.isChecked():
                params += " SCALED_COMPONENTS"

        return params

    def populate_data(self, cv_data):
        """
        根据已有cv_data进行UI回填。
        """
        # 提取name
        name = cv_data.get('name', '')
        if name:
            self.cv_name = name

        params = cv_data.get('params', '')
        tokens = params.split()

        atom_val = ""
        numerical_derivatives = False
        nopbc = False
        scaled_components = False

        for tk in tokens:
            if tk.startswith("ATOM="):
                atom_val = tk[len("ATOM="):]
            elif tk == "NUMERICAL_DERIVATIVES":
                numerical_derivatives = True
            elif tk == "NOPBC":
                nopbc = True
            elif tk == "SCALED_COMPONENTS":
                scaled_components = True

        # 回填原子
        if atom_val:
            try:
                self.atom_selection.set_selection(atom_val)
            except:
                QtWidgets.QMessageBox.warning(self, "警告", "ATOM 格式错误。")

        # 回填高级选项
        if numerical_derivatives or nopbc or scaled_components:
            self.adv_box.setChecked(True)
            self.numerical_derivatives_checkbox.setChecked(numerical_derivatives)
            self.nopbc_checkbox.setChecked(nopbc)
            self.scaled_components_checkbox.setChecked(scaled_components)
        else:
            self.adv_box.setChecked(False)
            self.numerical_derivatives_checkbox.setChecked(False)
            self.nopbc_checkbox.setChecked(False)
            self.scaled_components_checkbox.setChecked(False)

    def get_cv_output(self):
        """
        返回此CV实际输出的字段列表。
        默认: name.x, name.y, name.z
        如果SCALED_COMPONENTS被勾选，则还要增加 name.a, name.b, name.c
        """
        if not self.cv_name:
            return []
        # 默认输出
        outputs = [
            f"{self.cv_name}.x",
            f"{self.cv_name}.y",
            f"{self.cv_name}.z"
        ]
        if self.adv_box.isChecked() and self.scaled_components_checkbox.isChecked():
            outputs.extend([
                f"{self.cv_name}.a",
                f"{self.cv_name}.b",
                f"{self.cv_name}.c"
            ])
        return outputs
