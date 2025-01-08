"""
multi_rmsd_page.py
这是一个参考结构对比类型(dis_from_ref)的CV: MULTI_RMSD

Compulsory:
    REFERENCE=file.pdb
    TYPE=MULTI-SIMPLE / MULTI-OPTIMAL / MULTI-OPTIMAL-FAST / MULTI-DRMSD (默认 MULTI-SIMPLE)

Options(关键字型):
    NUMERICAL_DERIVATIVES
    NOPBC
    SQUARED
示例输出：
    name: MULTI_RMSD REFERENCE=xxx TYPE=xxx [NUMERICAL_DERIVATIVES] [NOPBC] [SQUARED]
"""

import os
from PyQt5 import QtWidgets, QtCore

class MultiRMSDPage(QtWidgets.QWidget):
    """
    计算多域RMSD (dis_from_ref类型)
    可配置:
        - REFERENCE (pdb文件, 通过文件选择对话框)
        - TYPE=MULTI-SIMPLE / MULTI-OPTIMAL / MULTI-OPTIMAL-FAST / MULTI-DRMSD (下拉框)
        - 高级参数(关键字): NUMERICAL_DERIVATIVES, NOPBC, SQUARED
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        # 标题提示
        prompt_label = QtWidgets.QLabel("计算多域RMSD(MULTI_RMSD) - 用于大分子多域参考对齐")
        prompt_label.setWordWrap(True)
        prompt_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(prompt_label)

        # 基础参数区域
        basic_group = QtWidgets.QGroupBox("基础参数")
        basic_form = QtWidgets.QFormLayout(basic_group)

        # 1) REFERENCE
        self.reference_label = QtWidgets.QLabel("REFERENCE(pdb):")
        # 添加中文悬浮提示
        self.reference_label.setToolTip(
            "参考结构的pdb文件，包含此CV所需原子。\n"
            "例如：REFERENCE=ref.pdb"
        )
        self.ref_edit = QtWidgets.QLineEdit()
        self.ref_btn = QtWidgets.QPushButton("选择参考pdb文件")
        ref_h = QtWidgets.QHBoxLayout()
        ref_h.addWidget(self.ref_edit, stretch=1)
        ref_h.addWidget(self.ref_btn)
        basic_form.addRow(self.reference_label, ref_h)

        # 2) TYPE
        self.type_label = QtWidgets.QLabel("TYPE:")
        # 添加中文悬浮提示
        self.type_label.setToolTip(
            "MULTI-RMSD的对齐方式（默认=MULTI-SIMPLE），可选：\n"
            "  - MULTI-SIMPLE\n"
            "  - MULTI-OPTIMAL\n"
            "  - MULTI-OPTIMAL-FAST\n"
            "  - MULTI-DRMSD"
        )
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["MULTI-SIMPLE", "MULTI-OPTIMAL", "MULTI-OPTIMAL-FAST", "MULTI-DRMSD"])
        self.type_combo.setCurrentText("MULTI-SIMPLE")
        basic_form.addRow(self.type_label, self.type_combo)

        layout.addWidget(basic_group)

        # 高级参数按钮
        self.adv_btn = QtWidgets.QPushButton("高级参数")
        layout.addWidget(self.adv_btn)

        self.advanced_dialog = MultiRMSDAdvancedDialog(self)

        # 绑定事件
        self.ref_btn.clicked.connect(self.select_reference_file)
        self.adv_btn.clicked.connect(self.open_advanced_dialog)

        self.setLayout(layout)

    def select_reference_file(self):
        """
        只选择pdb文件
        """
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
        """
        弹出高级参数对话框
        """
        if self.advanced_dialog.exec_() == QtWidgets.QDialog.Accepted:
            pass  # 用户点击了确定

    def get_definition_line(self):
        """
        返回形如:
            REFERENCE=xxx TYPE=xxx [NUMERICAL_DERIVATIVES] [NOPBC] [SQUARED]
        """
        ref_path = self.ref_edit.text().strip()
        if not ref_path:
            QtWidgets.QMessageBox.warning(self, "警告", "请指定REFERENCE(pdb文件)!")
            return None

        t = self.type_combo.currentText().strip()
        if not t:
            t = "MULTI-SIMPLE"  # fallback

        line = f"REFERENCE={ref_path} TYPE={t}"

        adv_data = self.advanced_dialog.get_data()
        if adv_data.get('NUMERICAL_DERIVATIVES'):
            line += " NUMERICAL_DERIVATIVES"
        if adv_data.get('NOPBC'):
            line += " NOPBC"
        if adv_data.get('SQUARED'):
            line += " SQUARED"

        return line

    def populate_data(self, cv_data):
        """
        例如:
          "REFERENCE=xxx TYPE=MULTI-OPTIMAL NOPBC SQUARED"
        """
        params = cv_data.get('params', '')
        tokens = params.split()

        ref_file = ""
        type_val = "MULTI-SIMPLE"
        adv_data = {
            'NUMERICAL_DERIVATIVES': False,
            'NOPBC': False,
            'SQUARED': False
        }

        for tk in tokens:
            if tk.startswith("REFERENCE="):
                ref_file = tk.split('=',1)[1].strip()
            elif tk.startswith("TYPE="):
                type_val = tk.split('=',1)[1].strip()
            elif tk == "NUMERICAL_DERIVATIVES":
                adv_data['NUMERICAL_DERIVATIVES'] = True
            elif tk == "NOPBC":
                adv_data['NOPBC'] = True
            elif tk == "SQUARED":
                adv_data['SQUARED'] = True

        if ref_file:
            self.ref_edit.setText(ref_file)
        self.type_combo.setCurrentText(type_val.upper())

        # 填充到高级dialog
        self.advanced_dialog.populate_data(adv_data)

    def get_cv_output(self):
        """
        MULTI_RMSD只有自己名字本身作为输出
        """
        if hasattr(self, 'cv_name'):
            return [self.cv_name]
        else:
            return []

    def set_cv_name(self, name):
        self.cv_name = name


class MultiRMSDAdvancedDialog(QtWidgets.QDialog):
    """
    高级参数(关键字):
      - NUMERICAL_DERIVATIVES
      - NOPBC
      - SQUARED
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MULTI_RMSD 高级参数")
        layout = QtWidgets.QVBoxLayout(self)

        self.nd_check = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 添加中文悬浮提示
        self.nd_check.setToolTip("启用数值方式计算导数（默认关闭）")

        self.nopbc_check = QtWidgets.QCheckBox("NOPBC")
        # 添加中文悬浮提示
        self.nopbc_check.setToolTip("忽略周期性边界条件来计算距离（默认关闭）")

        self.squared_check = QtWidgets.QCheckBox("SQUARED")
        # 添加中文悬浮提示
        self.squared_check.setToolTip("如果勾选，将输出平均平方位移而不是RMSD（默认关闭）")

        layout.addWidget(self.nd_check)
        layout.addWidget(self.nopbc_check)
        layout.addWidget(self.squared_check)

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
            'NUMERICAL_DERIVATIVES': self.nd_check.isChecked(),
            'NOPBC': self.nopbc_check.isChecked(),
            'SQUARED': self.squared_check.isChecked()
        }

    def populate_data(self, data):
        self.nd_check.setChecked(data.get('NUMERICAL_DERIVATIVES', False))
        self.nopbc_check.setChecked(data.get('NOPBC', False))
        self.squared_check.setChecked(data.get('SQUARED', False))
