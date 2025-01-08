"""
target_page.py
这是一个参考结构对比类型(dis_from_ref)的CV: TARGET

Compulsory:
    REFERENCE=file.pdb
    TYPE=EUCLIDEAN (目前仅此一种可选)

Options(关键字):
    NUMERICAL_DERIVATIVES

示例输出:
    name: TARGET REFERENCE=xxx TYPE=EUCLIDEAN [NUMERICAL_DERIVATIVES]

在reference.pdb中应包含描述CV label及其在参考结构下的数值等信息
(具体描述见文档)
"""

import os
from PyQt5 import QtWidgets, QtCore

class TargetPage(QtWidgets.QWidget):
    """
    计算目标参考点在CV空间的欧几里得距离(TARGET)
    可配置:
        - REFERENCE=xxx(pdb文件)
        - TYPE=EUCLIDEAN (仅此一种)
        - NUMERICAL_DERIVATIVES(关键字)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        prompt_label = QtWidgets.QLabel("计算TARGET (在已有CV空间与参考CV值的欧几里得距离)")
        prompt_label.setWordWrap(True)
        prompt_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(prompt_label)

        base_group = QtWidgets.QGroupBox("基础参数")
        base_form = QtWidgets.QFormLayout(base_group)

        # 1) REFERENCE
        self.ref_label = QtWidgets.QLabel("REFERENCE(pdb):")
        # 添加中文悬浮提示
        self.ref_label.setToolTip(
            "指定一个pdb格式文件作为参考结构。\n"
            "在此PDB文件中，原子坐标、BOX长度应以埃为单位(或自然单位)。\n"
            "若需要原子电荷或质量信息，请将其写入PDB的beta和occupancy列。"
        )
        self.ref_edit = QtWidgets.QLineEdit()
        self.ref_btn = QtWidgets.QPushButton("选择参考pdb文件")
        ref_h = QtWidgets.QHBoxLayout()
        ref_h.addWidget(self.ref_edit, stretch=1)
        ref_h.addWidget(self.ref_btn)
        base_form.addRow(self.ref_label, ref_h)

        # 2) TYPE (默认=EUCLIDEAN)
        self.type_label = QtWidgets.QLabel("TYPE:")
        # 添加中文悬浮提示
        self.type_label.setToolTip(
            "指定度量方式（默认=EUCLIDEAN），即CV值与参考值之间的欧几里得距离"
        )
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["EUCLIDEAN"])
        self.type_combo.setCurrentText("EUCLIDEAN")
        base_form.addRow(self.type_label, self.type_combo)

        layout.addWidget(base_group)

        # 高级参数按钮
        self.adv_btn = QtWidgets.QPushButton("高级参数")
        layout.addWidget(self.adv_btn)

        self.advanced_dialog = TargetAdvancedDialog(self)

        # 事件绑定
        self.ref_btn.clicked.connect(self.select_reference_file)
        self.adv_btn.clicked.connect(self.open_advanced_dialog)

        self.setLayout(layout)

    def select_reference_file(self):
        """选择pdb文件"""
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "选择参考pdb文件",
            os.getcwd(),
            "PDB Files (*.pdb);;All Files (*)"
        )
        if fname:
            if not fname.lower().endswith(".pdb"):
                QtWidgets.QMessageBox.warning(self, "警告", "只支持pdb文件！")
                return
            self.ref_edit.setText(fname)

    def open_advanced_dialog(self):
        """弹出高级参数对话框"""
        if self.advanced_dialog.exec_() == QtWidgets.QDialog.Accepted:
            pass  # 用户点了确定

    def get_definition_line(self):
        """
        返回形如:
            "REFERENCE=xxx TYPE=EUCLIDEAN [NUMERICAL_DERIVATIVES]"
        """
        ref_path = self.ref_edit.text().strip()
        if not ref_path:
            QtWidgets.QMessageBox.warning(self, "警告", "请指定REFERENCE(pdb文件)!")
            return None

        t = self.type_combo.currentText().strip()
        if not t:
            t = "EUCLIDEAN"  # fallback

        line = f"REFERENCE={ref_path} TYPE={t}"

        adv_data = self.advanced_dialog.get_data()
        if adv_data.get('NUMERICAL_DERIVATIVES'):
            line += " NUMERICAL_DERIVATIVES"

        return line

    def populate_data(self, cv_data):
        """
        例如:
          "REFERENCE=xxx TYPE=EUCLIDEAN NUMERICAL_DERIVATIVES"
        """
        params = cv_data.get('params', '')
        tokens = params.split()

        ref_file = ""
        type_val = "EUCLIDEAN"
        adv_data = {
            'NUMERICAL_DERIVATIVES': False,
        }

        for tk in tokens:
            if tk.startswith("REFERENCE="):
                ref_file = tk.split('=', 1)[1].strip()
            elif tk.startswith("TYPE="):
                type_val = tk.split('=', 1)[1].strip()
            elif tk == "NUMERICAL_DERIVATIVES":
                adv_data['NUMERICAL_DERIVATIVES'] = True

        if ref_file:
            self.ref_edit.setText(ref_file)
        if type_val:
            self.type_combo.setCurrentText(type_val.upper())

        # 填充到高级dialog
        self.advanced_dialog.populate_data(adv_data)

    def get_cv_output(self):
        """
        TARGET只有自己名字本身作为输出
        """
        if hasattr(self, 'cv_name'):
            return [self.cv_name]
        else:
            return []

    def set_cv_name(self, name):
        self.cv_name = name


class TargetAdvancedDialog(QtWidgets.QDialog):
    """
    高级参数(关键字):
      - NUMERICAL_DERIVATIVES
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TARGET 高级参数")
        layout = QtWidgets.QVBoxLayout(self)

        self.nd_check = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 添加中文悬浮提示
        self.nd_check.setToolTip("启用数值方式计算导数（默认关闭）")
        layout.addWidget(self.nd_check)

        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("确定")
        self.cancel_btn = QtWidgets.QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        self.setLayout(layout)

    def get_data(self):
        return {
            'NUMERICAL_DERIVATIVES': self.nd_check.isChecked()
        }

    def populate_data(self, data):
        self.nd_check.setChecked(data.get('NUMERICAL_DERIVATIVES', False))
