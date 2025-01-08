"""
rmsd_page.py
这是一个参考结构对比类型(dis_from_ref)的CV: RMSD
"""

import os
from PyQt5 import QtWidgets, QtCore

class RMSDPage(QtWidgets.QWidget):
    """
    计算与参考结构的RMSD距离
    可配置:
      - REFERENCE (pdb文件, 通过文件选择对话框)
      - TYPE=OPTIMAL/SIMPLE (下拉框，默认SIMPLE)
      - 高级参数(关键字选项): NUMERICAL_DERIVATIVES, NOPBC, SQUARED
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)

        # 标题提示
        prompt_label = QtWidgets.QLabel("计算与参考结构的RMSD距离")
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
            "参考结构的pdb文件，包含此CV所需的原子。\n"
            "例如：REFERENCE=ref.pdb"
        )
        self.reference_edit = QtWidgets.QLineEdit()
        self.reference_btn = QtWidgets.QPushButton("选择参考pdb文件")
        ref_h = QtWidgets.QHBoxLayout()
        ref_h.addWidget(self.reference_edit, stretch=1)
        ref_h.addWidget(self.reference_btn)
        basic_form.addRow(self.reference_label, ref_h)

        # 2) TYPE
        self.type_label = QtWidgets.QLabel("TYPE:")
        # 添加中文悬浮提示
        self.type_label.setToolTip(
            "RMSD对齐方式（默认=SIMPLE），可选：\n"
            "  - SIMPLE\n"
            "  - OPTIMAL"
        )
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["SIMPLE", "OPTIMAL"])
        self.type_combo.setCurrentText("SIMPLE")  # 默认
        basic_form.addRow(self.type_label, self.type_combo)

        layout.addWidget(basic_group)

        # 高级参数按钮
        self.adv_btn = QtWidgets.QPushButton("高级参数")
        layout.addWidget(self.adv_btn)

        # 高级参数区域(对话框)
        self.advanced_dialog = RMSDAdvancedDialog(self)

        # 绑定事件
        self.reference_btn.clicked.connect(self.select_reference_file)
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
            # 简单校验一下后缀
            if not fname.lower().endswith(".pdb"):
                QtWidgets.QMessageBox.warning(self, "警告", "只支持pdb文件！")
                return
            self.reference_edit.setText(fname)

    def open_advanced_dialog(self):
        """
        弹出高级参数对话框
        """
        # 如果已有设置, 就传递给对话框
        if self.advanced_dialog.exec_() == QtWidgets.QDialog.Accepted:
            pass  # 用户点击了 确定

    def get_definition_line(self):
        """
        生成RMSD定义行, 形如:
         name: RMSD REFERENCE=xxx TYPE=OPTIMAL [NUMERICAL_DERIVATIVES] ...
        """
        ref_path = self.reference_edit.text().strip()
        if not ref_path:
            QtWidgets.QMessageBox.warning(self, "警告", "请指定REFERENCE(pdb文件)!")
            return None

        t = self.type_combo.currentText().strip()
        if not t:
            t = "SIMPLE"  # fallback

        line = f"REFERENCE={ref_path} TYPE={t}"

        # 拼上高级参数
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
        从cv_data['params']解析
        例如: "REFERENCE=file.pdb TYPE=OPTIMAL NUMERICAL_DERIVATIVES SQUARED"
        """
        params = cv_data.get('params', '')
        tokens = params.split()

        ref_file = ""
        type_val = "SIMPLE"

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
            self.reference_edit.setText(ref_file)
        self.type_combo.setCurrentText(type_val.upper())

        # 填充到高级dialog
        self.advanced_dialog.populate_data(adv_data)

    def get_cv_output(self):
        """
        RMSD只有自己名字本身作为输出
        """
        # 假设外部CV name是xxx, 这里只返回 [xxx]
        # 由外部在保存后传 set_cv_name
        if hasattr(self, 'cv_name'):
            return [self.cv_name]
        else:
            return []

    def set_cv_name(self, name):
        self.cv_name = name


class RMSDAdvancedDialog(QtWidgets.QDialog):
    """
    高级参数: NUMERICAL_DERIVATIVES, NOPBC, SQUARED
    都是关键字型
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RMSD 高级参数")
        layout = QtWidgets.QVBoxLayout(self)

        self.nd_check = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 添加中文悬浮提示
        self.nd_check.setToolTip("启用数值方式计算导数（默认关闭）")

        self.nopbc_check = QtWidgets.QCheckBox("NOPBC")
        # 添加中文悬浮提示
        self.nopbc_check.setToolTip("忽略周期性边界条件来计算距离（默认关闭）")

        self.squared_check = QtWidgets.QCheckBox("SQUARED")
        # 添加中文悬浮提示
        self.squared_check.setToolTip("若勾选，返回均方位移而不是RMSD（默认关闭）")

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
        """
        data形如: {'NUMERICAL_DERIVATIVES': True/False,
                   'NOPBC': True/False,
                   'SQUARED': True/False}
        """
        self.nd_check.setChecked(data.get('NUMERICAL_DERIVATIVES', False))
        self.nopbc_check.setChecked(data.get('NOPBC', False))
        self.squared_check.setChecked(data.get('SQUARED', False))
