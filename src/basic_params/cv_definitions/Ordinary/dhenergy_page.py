"""
dhenergy_page.py

一个文件中同时包含:
- DHENERGYAdvancedDialog : DHENERGY高级参数对话框
- DHENERGYPage : DHENERGY的主界面
"""

from PyQt5 import QtWidgets, QtCore
# 注意此处路径保持原状，不做额外更改
from ...mode_definitions.atom_range import AtomRangeWidget
from ...mode_definitions.single_atom_list import SingleAtomListWidget

class DHENERGYAdvancedDialog(QtWidgets.QDialog):
    """
    弹出对话框，用于编辑 DHENERGY 的高级可选关键字。
    包括：
    - NUMERICAL_DERIVATIVES
    - NOPBC
    - SERIAL
    - PAIR
    - NLIST (若选中NLIST，则必须输入NL_CUTOFF, NL_STRIDE)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DHENERGY 高级参数")
        self.resize(400, 200)

        layout = QtWidgets.QVBoxLayout(self)

        adv_form = QtWidgets.QFormLayout()

        self.numder_cb = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 悬浮提示
        self.numder_cb.setToolTip("启用数值方式计算导数（默认关闭）")

        self.nopbc_cb = QtWidgets.QCheckBox("NOPBC")
        self.nopbc_cb.setToolTip("忽略周期性边界条件进行距离计算（默认关闭）")

        self.serial_cb = QtWidgets.QCheckBox("SERIAL")
        self.serial_cb.setToolTip("串行模式运行，用于调试（默认关闭）")

        self.pair_cb = QtWidgets.QCheckBox("PAIR")
        self.pair_cb.setToolTip("只配对groupA与groupB中对应索引的原子（默认关闭）")

        self.nlist_cb = QtWidgets.QCheckBox("NLIST")
        self.nlist_cb.setToolTip("使用邻居列表以加速计算（默认关闭）")

        adv_form.addRow(self.numder_cb)
        adv_form.addRow(self.nopbc_cb)
        adv_form.addRow(self.serial_cb)
        adv_form.addRow(self.pair_cb)
        adv_form.addRow(self.nlist_cb)

        # 行: NL_CUTOFF / NL_STRIDE
        nlist_line = QtWidgets.QHBoxLayout()
        self.nl_cutoff_label = QtWidgets.QLabel("NL_CUTOFF:")
        self.nl_cutoff_label.setToolTip("邻居列表的截断半径")
        self.nl_cutoff_spin = QtWidgets.QDoubleSpinBox()
        self.nl_cutoff_spin.setRange(0.0,999999.0)
        self.nl_cutoff_spin.setDecimals(3)
        self.nl_cutoff_spin.setValue(1.0)

        self.nl_stride_label = QtWidgets.QLabel("NL_STRIDE:")
        self.nl_stride_label.setToolTip("邻居列表的更新频率（每隔多少步更新一次）")
        self.nl_stride_spin = QtWidgets.QSpinBox()
        self.nl_stride_spin.setRange(1,999999)
        self.nl_stride_spin.setValue(100)

        nlist_line.addWidget(self.nl_cutoff_label)
        nlist_line.addWidget(self.nl_cutoff_spin)
        nlist_line.addWidget(self.nl_stride_label)
        nlist_line.addWidget(self.nl_stride_spin)

        adv_form.addRow(nlist_line)

        layout.addLayout(adv_form)

        # 按钮行
        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("确定")
        self.cancel_btn = QtWidgets.QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        # 绑定nlist_cb来启用/禁用cutoff/stride
        self.nlist_cb.stateChanged.connect(self.toggle_nlist)

        # 初始化
        self.toggle_nlist(0)

    def toggle_nlist(self, state):
        enable_nl = (state == QtCore.Qt.Checked)
        self.nl_cutoff_label.setEnabled(enable_nl)
        self.nl_cutoff_spin.setEnabled(enable_nl)
        self.nl_stride_label.setEnabled(enable_nl)
        self.nl_stride_spin.setEnabled(enable_nl)

    def populate_data(self, data):
        """
        data中可能是:
        {
          'NUMDER': bool,
          'NOPBC': bool,
          'SERIAL': bool,
          'PAIR': bool,
          'NLIST': bool,
          'NL_CUTOFF': float,
          'NL_STRIDE': int
        }
        """
        self.numder_cb.setChecked(data.get('NUMDER', False))
        self.nopbc_cb.setChecked(data.get('NOPBC', False))
        self.serial_cb.setChecked(data.get('SERIAL', False))
        self.pair_cb.setChecked(data.get('PAIR', False))
        self.nlist_cb.setChecked(data.get('NLIST', False))

        self.nl_cutoff_spin.setValue(data.get('NL_CUTOFF', 1.0))
        self.nl_stride_spin.setValue(data.get('NL_STRIDE', 100))

        self.toggle_nlist(QtCore.Qt.Checked if data.get('NLIST', False) else 0)

    def get_data(self):
        """
        返回字典
        {
          'NUMDER': bool,
          'NOPBC': bool,
          'SERIAL': bool,
          'PAIR': bool,
          'NLIST': bool,
          'NL_CUTOFF': float,
          'NL_STRIDE': int
        }
        """
        out = {}
        out['NUMDER'] = self.numder_cb.isChecked()
        out['NOPBC'] = self.nopbc_cb.isChecked()
        out['SERIAL'] = self.serial_cb.isChecked()
        out['PAIR'] = self.pair_cb.isChecked()
        out['NLIST'] = self.nlist_cb.isChecked()
        out['NL_CUTOFF'] = self.nl_cutoff_spin.value()
        out['NL_STRIDE'] = self.nl_stride_spin.value()
        return out


class DHENERGYPage(QtWidgets.QWidget):
    """
    DHENERGY:
      - GROUPA=xxx (必填)
      - GROUPB=xxx (可选)
      - I=1.0, TEMP=300.0, EPSILON=80.0
      - 高级参数(通过DHENERGYAdvancedDialog):
         NUMDER, NOPBC, SERIAL, PAIR, NLIST(+ NL_CUTOFF, NL_STRIDE)
    """
    def __init__(self, group_labels, parent=None):
        super().__init__(parent)
        self.group_labels = group_labels
        self.cv_name = ""

        # 用于存储高级参数
        self.adv_data = {}

        layout = QtWidgets.QVBoxLayout(self)

        # 提示
        self.prompt_label = QtWidgets.QLabel("计算 Debye-Huckel interaction energy (DHENERGY)")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.prompt_label)

        # ========== GROUPA ==========

        groupA_box = QtWidgets.QGroupBox("GROUPA (必填)")
        groupA_layout = QtWidgets.QVBoxLayout(groupA_box)

        self.groupA_mode = QtWidgets.QComboBox()
        self.groupA_mode.addItems(["范围模式", "单原子列表模式"])
        groupA_layout.addWidget(self.groupA_mode)

        self.groupA_stack = QtWidgets.QStackedWidget()
        groupA_layout.addWidget(self.groupA_stack)

        # 注意：保持原有导入路径
        from ...mode_definitions.atom_range import AtomRangeWidget
        from ...mode_definitions.single_atom_list import SingleAtomListWidget

        self.groupA_range = AtomRangeWidget(self.group_labels)
        self.groupA_single = SingleAtomListWidget(self.group_labels)
        self.groupA_stack.addWidget(self.groupA_range)
        self.groupA_stack.addWidget(self.groupA_single)

        self.groupA_mode.currentIndexChanged.connect(self.groupA_stack.setCurrentIndex)

        layout.addWidget(groupA_box)

        # ========== GROUPB ==========
        groupB_box = QtWidgets.QGroupBox("GROUPB (可选，若为空则计算GROUPA内部)")
        groupB_layout = QtWidgets.QVBoxLayout(groupB_box)

        self.groupB_mode = QtWidgets.QComboBox()
        self.groupB_mode.addItems(["(不填)","范围模式", "单原子列表模式"])
        groupB_layout.addWidget(self.groupB_mode)

        self.groupB_stack = QtWidgets.QStackedWidget()
        groupB_layout.addWidget(self.groupB_stack)

        self.groupB_blank = QtWidgets.QWidget()
        self.groupB_range = AtomRangeWidget(self.group_labels)
        self.groupB_single = SingleAtomListWidget(self.group_labels)
        self.groupB_stack.addWidget(self.groupB_blank)
        self.groupB_stack.addWidget(self.groupB_range)
        self.groupB_stack.addWidget(self.groupB_single)

        self.groupB_mode.currentIndexChanged.connect(self.on_groupB_mode_changed)

        layout.addWidget(groupB_box)

        # ========== 基础参数 I, TEMP, EPSILON ==========
        base_box = QtWidgets.QGroupBox("基础参数")
        base_form = QtWidgets.QFormLayout(base_box)

        # -- I(ionic strength)
        self.i_label = QtWidgets.QLabel("I:")
        self.i_label.setToolTip("I（默认=1.0）：离子强度（单位 M）")
        self.i_spin = QtWidgets.QDoubleSpinBox()
        self.i_spin.setRange(0.0, 999999.0)
        self.i_spin.setDecimals(3)
        self.i_spin.setValue(1.0)
        base_form.addRow(self.i_label, self.i_spin)

        # -- TEMP
        self.temp_label = QtWidgets.QLabel("TEMP (K):")
        self.temp_label.setToolTip("TEMP（默认=300.0）：仿真温度(开尔文)")
        self.temp_spin = QtWidgets.QDoubleSpinBox()
        self.temp_spin.setRange(0.0,999999.0)
        self.temp_spin.setDecimals(1)
        self.temp_spin.setValue(300.0)
        base_form.addRow(self.temp_label, self.temp_spin)

        # -- EPSILON
        self.eps_label = QtWidgets.QLabel("EPSILON:")
        self.eps_label.setToolTip("EPSILON（默认=80.0）：溶剂介电常数")
        self.epsilon_spin = QtWidgets.QDoubleSpinBox()
        self.epsilon_spin.setRange(0.0,999999.0)
        self.epsilon_spin.setDecimals(1)
        self.epsilon_spin.setValue(80.0)
        base_form.addRow(self.eps_label, self.epsilon_spin)

        layout.addWidget(base_box)

        # ========== 高级参数按钮 ==========
        self.adv_btn = QtWidgets.QPushButton("高级参数")
        self.adv_btn.clicked.connect(self.open_advanced_dialog)
        layout.addWidget(self.adv_btn)

        layout.addStretch()

    def on_groupB_mode_changed(self, idx):
        self.groupB_stack.setCurrentIndex(idx)

    def open_advanced_dialog(self):
        dlg = DHENERGYAdvancedDialog(self)
        dlg.populate_data({
            'NUMDER': self.adv_data.get('NUMDER', False),
            'NOPBC': self.adv_data.get('NOPBC', False),
            'SERIAL': self.adv_data.get('SERIAL', False),
            'PAIR': self.adv_data.get('PAIR', False),
            'NLIST': self.adv_data.get('NLIST', False),
            'NL_CUTOFF': self.adv_data.get('NL_CUTOFF', 1.0),
            'NL_STRIDE': self.adv_data.get('NL_STRIDE', 100),
        })
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            new_data = dlg.get_data()
            self.adv_data.update(new_data)

    def set_cv_name(self, name):
        self.cv_name = name

    def get_cv_output(self):
        if not self.cv_name:
            return []
        return [self.cv_name]

    def get_definition_line(self):
        # groupA
        if self.groupA_stack.currentIndex()==0:
            gA_str = self.groupA_range.get_str()
        else:
            atoms = self.groupA_single.get_atoms()
            gA_str = ",".join(atoms)
        if not gA_str.strip():
            QtWidgets.QMessageBox.warning(self, "警告", "DHENERGY 需要指定GROUPA！")
            return None

        line = f"GROUPA={gA_str}"

        # groupB
        idxB = self.groupB_stack.currentIndex()
        if idxB==1:
            gB_str = self.groupB_range.get_str()
        elif idxB==2:
            atomsB = self.groupB_single.get_atoms()
            gB_str = ",".join(atomsB)
        else:
            gB_str = ""
        if gB_str.strip():
            line += f" GROUPB={gB_str}"

        # I, TEMP, EPSILON
        i_val = self.i_spin.value()
        t_val = self.temp_spin.value()
        eps_val = self.epsilon_spin.value()
        line += f" I={i_val} TEMP={t_val} EPSILON={eps_val}"

        # 读取 self.adv_data, 生成可选关键字
        if self.adv_data.get('NUMDER', False):
            line += " NUMERICAL_DERIVATIVES"
        if self.adv_data.get('NOPBC', False):
            line += " NOPBC"
        if self.adv_data.get('SERIAL', False):
            line += " SERIAL"
        if self.adv_data.get('PAIR', False):
            line += " PAIR"
        if self.adv_data.get('NLIST', False):
            line += " NLIST"
            cutoff_v = self.adv_data.get('NL_CUTOFF', 1.0)
            stride_v = self.adv_data.get('NL_STRIDE', 100)
            line += f" NL_CUTOFF={cutoff_v} NL_STRIDE={stride_v}"

        return line

    def populate_data(self, cv_data):
        params = cv_data.get('params', '')
        tokens = params.split()

        groupA_str = ""
        groupB_str = ""

        i_val = 1.0
        t_val = 300.0
        eps_val = 80.0

        self.adv_data = {
            'NUMDER': False,
            'NOPBC': False,
            'SERIAL': False,
            'PAIR': False,
            'NLIST': False,
            'NL_CUTOFF': 1.0,
            'NL_STRIDE': 100,
        }

        for token in tokens:
            if token.startswith("GROUPA="):
                groupA_str = token[len("GROUPA="):]
            elif token.startswith("GROUPB="):
                groupB_str = token[len("GROUPB="):]
            elif token.startswith("I="):
                try:
                    i_val = float(token[len("I="):])
                except:
                    pass
            elif token.startswith("TEMP="):
                try:
                    t_val = float(token[len("TEMP="):])
                except:
                    pass
            elif token.startswith("EPSILON="):
                try:
                    eps_val = float(token[len("EPSILON="):])
                except:
                    pass
            elif token=="NUMERICAL_DERIVATIVES":
                self.adv_data['NUMDER'] = True
            elif token=="NOPBC":
                self.adv_data['NOPBC'] = True
            elif token=="SERIAL":
                self.adv_data['SERIAL'] = True
            elif token=="PAIR":
                self.adv_data['PAIR'] = True
            elif token=="NLIST":
                self.adv_data['NLIST'] = True
            elif token.startswith("NL_CUTOFF="):
                try:
                    self.adv_data['NL_CUTOFF'] = float(token[len("NL_CUTOFF="):])
                except:
                    pass
            elif token.startswith("NL_STRIDE="):
                try:
                    self.adv_data['NL_STRIDE'] = int(token[len("NL_STRIDE="):])
                except:
                    pass

        # groupA
        if groupA_str:
            if '-' in groupA_str:
                self.groupA_mode.setCurrentIndex(0)
                self.groupA_range.set_definition(groupA_str)
            else:
                self.groupA_mode.setCurrentIndex(1)
                arrA = groupA_str.split(',')
                self.groupA_single.clear_all_atoms()
                for a in arrA:
                    if a.strip():
                        self.groupA_single.add_atom(a.strip())

        # groupB
        if not groupB_str.strip():
            self.groupB_mode.setCurrentIndex(0)
        else:
            if '-' in groupB_str:
                self.groupB_mode.setCurrentIndex(1)
                self.groupB_range.set_definition(groupB_str)
            else:
                self.groupB_mode.setCurrentIndex(2)
                arrB = groupB_str.split(',')
                self.groupB_single.clear_all_atoms()
                for b in arrB:
                    if b.strip():
                        self.groupB_single.add_atom(b.strip())

        self.i_spin.setValue(i_val)
        self.temp_spin.setValue(t_val)
        self.epsilon_spin.setValue(eps_val)

        if cv_data.get('name',''):
            self.cv_name = cv_data['name']

        # 构造对话框，但不显示
        dlg_data = {
            'NUMDER': self.adv_data['NUMDER'],
            'NOPBC': self.adv_data['NOPBC'],
            'SERIAL': self.adv_data['SERIAL'],
            'PAIR': self.adv_data['PAIR'],
            'NLIST': self.adv_data['NLIST'],
            'NL_CUTOFF': self.adv_data['NL_CUTOFF'],
            'NL_STRIDE': self.adv_data['NL_STRIDE'],
        }
        # 保证 self.adv_data 是最新的
        if not hasattr(self, 'adv_btn'):
            return
        # 仅在用户点击时再打开并查看
