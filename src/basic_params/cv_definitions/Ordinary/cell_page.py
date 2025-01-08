"""
cell_page.py

CELL CV的界面。可选择 NUMERICAL_DERIVATIVES 高级参数。其余无输入。
输出属性：name.ax, name.ay, name.az,
           name.bx, name.by, name.bz,
           name.cx, name.cy, name.cz
"""

from PyQt5 import QtWidgets, QtCore


class CellAdvancedDialog(QtWidgets.QDialog):
    """
    用于编辑CELL的高级参数：
      - NUMERICAL_DERIVATIVES (关键字型)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CELL 高级参数")
        self.resize(280, 120)

        main_layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()
        self.num_deriv_cb = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 为 NUMERICAL_DERIVATIVES 添加中文鼠标悬浮说明
        self.num_deriv_cb.setToolTip("启用数值求导来计算这些量的导数（默认关闭）")
        form_layout.addRow(self.num_deriv_cb)
        main_layout.addLayout(form_layout)

        # 按钮行
        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("确定")
        self.cancel_btn = QtWidgets.QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def populate_data(self, data):
        """
        data形如: {'NUMERICAL_DERIVATIVES': bool}
        """
        self.num_deriv_cb.setChecked(data.get('NUMERICAL_DERIVATIVES', False))

    def get_data(self):
        """
        返回形如: {'NUMERICAL_DERIVATIVES': bool}
        """
        return {
            'NUMERICAL_DERIVATIVES': self.num_deriv_cb.isChecked()
        }


class CellPage(QtWidgets.QWidget):
    """
    CELL CV界面：
      - 无需输入任何atom/group
      - 仅可选高级参数: NUMERICAL_DERIVATIVES
      - 输出共9个：name.ax, name.ay, name.az, name.bx, name.by, name.bz, name.cx, name.cy, name.cz
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cv_name = ""
        self.adv_data = {
            'NUMERICAL_DERIVATIVES': False
        }

        layout = QtWidgets.QVBoxLayout(self)

        prompt_label = QtWidgets.QLabel("CELL: 计算模拟盒子的三个晶格向量(ax, ay, az, bx, by, bz, cx, cy, cz)。")
        prompt_label.setWordWrap(True)
        prompt_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(prompt_label)

        # 按钮：高级参数
        self.adv_btn = QtWidgets.QPushButton("高级参数")
        self.adv_btn.clicked.connect(self.open_advanced_dialog)
        layout.addWidget(self.adv_btn)

        layout.addStretch()

    def open_advanced_dialog(self):
        dlg = CellAdvancedDialog(self)
        dlg.populate_data(self.adv_data)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            new_adv = dlg.get_data()
            self.adv_data.update(new_adv)

    def set_cv_name(self, name):
        """
        由CV对话框在保存前调用，用于设置该CV名字
        """
        self.cv_name = name

    def get_cv_output(self):
        """
        返回输出属性列表:
          [ name.ax, name.ay, name.az, name.bx, name.by, name.bz, name.cx, name.cy, name.cz ]
        """
        if not self.cv_name:
            return []
        return [
            f"{self.cv_name}.ax",
            f"{self.cv_name}.ay",
            f"{self.cv_name}.az",
            f"{self.cv_name}.bx",
            f"{self.cv_name}.by",
            f"{self.cv_name}.bz",
            f"{self.cv_name}.cx",
            f"{self.cv_name}.cy",
            f"{self.cv_name}.cz"
        ]

    def get_definition_line(self):
        """
        生成CELL定义行:
          若 NUMERICAL_DERIVATIVES => "NUMERICAL_DERIVATIVES"
        """
        line = ""
        if self.adv_data.get('NUMERICAL_DERIVATIVES', False):
            line += "NUMERICAL_DERIVATIVES"

        return line.strip()  # 若为空则返回空字符串

    def populate_data(self, cv_data):
        """
        从cv_data['params']中解析是否有NUMERICAL_DERIVATIVES
        """
        params_str = cv_data.get('params', '').split()
        self.adv_data = {
            'NUMERICAL_DERIVATIVES': False
        }
        for token in params_str:
            if token == "NUMERICAL_DERIVATIVES":
                self.adv_data['NUMERICAL_DERIVATIVES'] = True
