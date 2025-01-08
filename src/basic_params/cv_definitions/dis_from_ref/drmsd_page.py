"""
drmsd_page.py
这是一个参考结构对比类型(dis_from_ref)的CV: DRMSD

Compulsory:
REFERENCE=file.pdb
LOWER_CUTOFF=0.1
UPPER_CUTOFF=0.8
TYPE=DRMSD / INTER-DRMSD / INTRA-DRMSD (默认 DRMSD)

高级参数(关键字类型):
  NUMERICAL_DERIVATIVES
  NOPBC
"""

import os
from PyQt5 import QtWidgets, QtCore

class DRMSDPage(QtWidgets.QWidget):
    """
    计算基于对间距的DRMSD距离
    可配置:
      - REFERENCE (pdb文件, 通过文件选择对话框)
      - LOWER_CUTOFF, UPPER_CUTOFF (默认0.1, 0.8)
      - TYPE=DRMSD / INTER-DRMSD / INTRA-DRMSD (下拉框, 默认DRMSD)
    高级参数(关键字选项): NUMERICAL_DERIVATIVES, NOPBC
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)

        # 标题提示
        prompt_label = QtWidgets.QLabel("计算基于对间距的DRMSD距离")
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
            "参考结构的pdb文件，用于CV中包含的原子。"
        )
        self.reference_edit = QtWidgets.QLineEdit()
        self.reference_btn = QtWidgets.QPushButton("选择参考pdb文件")
        ref_h = QtWidgets.QHBoxLayout()
        ref_h.addWidget(self.reference_edit, stretch=1)
        ref_h.addWidget(self.reference_btn)
        basic_form.addRow(self.reference_label, ref_h)

        # 2) LOWER_CUTOFF
        self.lower_cutoff_label = QtWidgets.QLabel("LOWER_CUTOFF:")
        self.lower_cutoff_label.setToolTip(
            "仅对距离大于 LOWER_CUTOFF 的原子对进行计算（默认=0.1）"
        )
        self.lower_cutoff_spin = QtWidgets.QDoubleSpinBox()
        self.lower_cutoff_spin.setRange(0.0, 999.0)
        self.lower_cutoff_spin.setDecimals(3)
        self.lower_cutoff_spin.setValue(0.1)
        basic_form.addRow(self.lower_cutoff_label, self.lower_cutoff_spin)

        # 3) UPPER_CUTOFF
        self.upper_cutoff_label = QtWidgets.QLabel("UPPER_CUTOFF:")
        self.upper_cutoff_label.setToolTip(
            "仅对距离小于 UPPER_CUTOFF 的原子对进行计算（默认=0.8）"
        )
        self.upper_cutoff_spin = QtWidgets.QDoubleSpinBox()
        self.upper_cutoff_spin.setRange(0.0, 999.0)
        self.upper_cutoff_spin.setDecimals(3)
        self.upper_cutoff_spin.setValue(0.8)
        basic_form.addRow(self.upper_cutoff_label, self.upper_cutoff_spin)

        # 4) TYPE
        self.type_label = QtWidgets.QLabel("TYPE:")
        self.type_label.setToolTip(
            "选择DRMSD类型（默认=DRMSD）。\n"
            "可选：\n"
            "  - DRMSD: 普通的DRMSD\n"
            "  - INTER-DRMSD: 仅针对不同分子间的距离\n"
            "  - INTRA-DRMSD: 仅针对同一分子内的距离"
        )
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["DRMSD", "INTER-DRMSD", "INTRA-DRMSD"])
        self.type_combo.setCurrentText("DRMSD")  # 默认
        basic_form.addRow(self.type_label, self.type_combo)

        layout.addWidget(basic_group)

        # 高级参数按钮
        self.adv_btn = QtWidgets.QPushButton("高级参数")
        layout.addWidget(self.adv_btn)

        # 高级参数区域(对话框)
        self.advanced_dialog = DRMSDAdvancedDialog(self)

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
            if not fname.lower().endswith(".pdb"):
                QtWidgets.QMessageBox.warning(self, "警告", "只支持pdb文件！")
                return
            self.reference_edit.setText(fname)

    def open_advanced_dialog(self):
        """
        弹出高级参数对话框
        """
        if self.advanced_dialog.exec_() == QtWidgets.QDialog.Accepted:
            pass  # 用户点击了 确定

    def get_definition_line(self):
        """
        生成DRMSD定义行, 形如:
         name: DRMSD REFERENCE=xxx LOWER_CUTOFF=xx UPPER_CUTOFF=xx TYPE=xx ...
        """
        ref_path = self.reference_edit.text().strip()
        if not ref_path:
            QtWidgets.QMessageBox.warning(self, "警告", "请指定REFERENCE(pdb文件)!")
            return None

        lower_cut = self.lower_cutoff_spin.value()
        upper_cut = self.upper_cutoff_spin.value()
        t = self.type_combo.currentText().strip()
        if not t:
            t = "DRMSD"  # fallback

        line = f"REFERENCE={ref_path} LOWER_CUTOFF={lower_cut} UPPER_CUTOFF={upper_cut} TYPE={t}"

        # 拼上高级参数
        adv_data = self.advanced_dialog.get_data()
        if adv_data.get('NUMERICAL_DERIVATIVES'):
            line += " NUMERICAL_DERIVATIVES"
        if adv_data.get('NOPBC'):
            line += " NOPBC"

        return line

    def populate_data(self, cv_data):
        """
        从cv_data['params']解析
        例如: "REFERENCE=file.pdb LOWER_CUTOFF=0.1 UPPER_CUTOFF=0.8 TYPE=INTER-DRMSD NOPBC ..."
        """
        params = cv_data.get('params', '')
        tokens = params.split()

        ref_file = ""
        lower_cut = 0.1
        upper_cut = 0.8
        type_val = "DRMSD"

        adv_data = {
            'NUMERICAL_DERIVATIVES': False,
            'NOPBC': False
        }

        for tk in tokens:
            if tk.startswith("REFERENCE="):
                ref_file = tk.split('=',1)[1].strip()
            elif tk.startswith("LOWER_CUTOFF="):
                try:
                    lower_cut = float(tk.split('=',1)[1].strip())
                except:
                    pass
            elif tk.startswith("UPPER_CUTOFF="):
                try:
                    upper_cut = float(tk.split('=',1)[1].strip())
                except:
                    pass
            elif tk.startswith("TYPE="):
                type_val = tk.split('=',1)[1].strip()
            elif tk == "NUMERICAL_DERIVATIVES":
                adv_data['NUMERICAL_DERIVATIVES'] = True
            elif tk == "NOPBC":
                adv_data['NOPBC'] = True

        if ref_file:
            self.reference_edit.setText(ref_file)
        self.lower_cutoff_spin.setValue(lower_cut)
        self.upper_cutoff_spin.setValue(upper_cut)
        self.type_combo.setCurrentText(type_val.upper())

        # 填充到高级dialog
        self.advanced_dialog.populate_data(adv_data)

    def get_cv_output(self):
        """
        DRMSD只有自己名字本身作为输出
        """
        if hasattr(self, 'cv_name'):
            return [self.cv_name]
        else:
            return []

    def set_cv_name(self, name):
        self.cv_name = name


class DRMSDAdvancedDialog(QtWidgets.QDialog):
    """
    高级参数: NUMERICAL_DERIVATIVES, NOPBC
    都是关键字型
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DRMSD 高级参数")
        layout = QtWidgets.QVBoxLayout(self)

        self.nd_check = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 给NUMERICAL_DERIVATIVES添加中文悬浮说明
        self.nd_check.setToolTip(
            "启用数值方式计算导数（默认关闭）"
        )

        self.nopbc_check = QtWidgets.QCheckBox("NOPBC")
        # 给NOPBC添加中文悬浮说明
        self.nopbc_check.setToolTip(
            "忽略周期性边界条件来计算距离（默认关闭）"
        )

        layout.addWidget(self.nd_check)
        layout.addWidget(self.nopbc_check)

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
            'NOPBC': self.nopbc_check.isChecked()
        }

    def populate_data(self, data):
        self.nd_check.setChecked(data.get('NUMERICAL_DERIVATIVES', False))
        self.nopbc_check.setChecked(data.get('NOPBC', False))
