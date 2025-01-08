from PyQt5 import QtWidgets, QtCore
from ...mode_definitions.atom_range import AtomRangeWidget
from ...mode_definitions.single_atom_list import SingleAtomListWidget
from ...mode_definitions.atom_range_stride import AtomRangeStrideWidget

class AdvancedSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("高级参数")
        layout = QtWidgets.QVBoxLayout(self)

        class_params_group = QtWidgets.QGroupBox("类参数")
        class_params_layout = QtWidgets.QFormLayout(class_params_group)

        # --- NN ---
        self.nn_label = QtWidgets.QLabel("NN:")
        # 为NN标签添加中文悬浮说明
        self.nn_label.setToolTip("NN（默认=6）：切换函数的 n 参数")

        self.nn_input = QtWidgets.QSpinBox()
        self.nn_input.setRange(1, 100)
        self.nn_input.setValue(6)
        class_params_layout.addRow(self.nn_label, self.nn_input)

        # --- MM ---
        self.mm_label = QtWidgets.QLabel("MM:")
        # 为MM标签添加中文悬浮说明
        self.mm_label.setToolTip("MM（默认=0）：切换函数的 m 参数；为0表示 2×NN")

        self.mm_input = QtWidgets.QSpinBox()
        self.mm_input.setRange(0, 100)
        self.mm_input.setValue(0)
        class_params_layout.addRow(self.mm_label, self.mm_input)

        # --- D_0 ---
        self.d0_label = QtWidgets.QLabel("D_0:")
        # 为D_0标签添加中文悬浮说明
        self.d0_label.setToolTip("D_0（默认=0.0）：切换函数的 d_0 参数")

        self.d0_input = QtWidgets.QDoubleSpinBox()
        self.d0_input.setRange(0.0, 10.0)
        self.d0_input.setDecimals(3)
        self.d0_input.setValue(0.0)
        class_params_layout.addRow(self.d0_label, self.d0_input)

        layout.addWidget(class_params_group)

        keyword_params_group = QtWidgets.QGroupBox("关键字参数")
        keyword_params_layout = QtWidgets.QFormLayout(keyword_params_group)

        # --- NUMERICAL_DERIVATIVES ---
        self.numerical_derivatives_checkbox = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        self.numerical_derivatives_checkbox.setToolTip("启用数值方式计算导数（默认关闭）")
        keyword_params_layout.addRow(self.numerical_derivatives_checkbox)

        # --- NOPBC ---
        self.nopbc_checkbox = QtWidgets.QCheckBox("NOPBC")
        self.nopbc_checkbox.setToolTip("忽略周期性边界条件来计算距离（默认关闭）")
        keyword_params_layout.addRow(self.nopbc_checkbox)

        # --- SERIAL ---
        self.serial_checkbox = QtWidgets.QCheckBox("SERIAL")
        self.serial_checkbox.setToolTip("串行模式下进行计算，用于调试（默认关闭）")
        keyword_params_layout.addRow(self.serial_checkbox)

        # --- PAIR ---
        self.pair_checkbox = QtWidgets.QCheckBox("PAIR")
        self.pair_checkbox.setToolTip("仅配对groupA与groupB的第i个原子（默认关闭）")
        keyword_params_layout.addRow(self.pair_checkbox)

        # --- NLIST ---
        self.nl_list_checkbox = QtWidgets.QCheckBox("NLIST")
        self.nl_list_checkbox.setToolTip("使用邻居列表加速计算（默认关闭）")
        self.nl_list_checkbox.stateChanged.connect(self.toggle_nlist)
        keyword_params_layout.addRow(self.nl_list_checkbox)

        layout.addWidget(keyword_params_group)

        self.nl_list_group = QtWidgets.QGroupBox("NLIST 参数")
        self.nl_list_group.setEnabled(False)
        nl_list_layout = QtWidgets.QFormLayout(self.nl_list_group)

        # --- NL_CUTOFF ---
        self.nl_cutoff_label = QtWidgets.QLabel("NL_CUTOFF:")
        self.nl_cutoff_label.setToolTip("邻居列表的截断距离")
        self.nl_cutoff_input = QtWidgets.QDoubleSpinBox()
        self.nl_cutoff_input.setRange(0.0, 10.0)
        self.nl_cutoff_input.setDecimals(3)
        self.nl_cutoff_input.setValue(0.5)
        nl_list_layout.addRow(self.nl_cutoff_label, self.nl_cutoff_input)

        # --- NL_STRIDE ---
        self.nl_stride_label = QtWidgets.QLabel("NL_STRIDE:")
        self.nl_stride_label.setToolTip("邻居列表的更新频率(每多少步更新一次)")
        self.nl_stride_input = QtWidgets.QSpinBox()
        self.nl_stride_input.setRange(1, 10000)
        self.nl_stride_input.setValue(100)
        nl_list_layout.addRow(self.nl_stride_label, self.nl_stride_input)

        layout.addWidget(self.nl_list_group)

        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("确定")
        self.cancel_btn = QtWidgets.QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def toggle_nlist(self, state):
        self.nl_list_group.setEnabled(state == QtCore.Qt.Checked)

    def get_data(self):
        """
        将高级参数中的所有选项打包成字典返回
        """
        data = {}
        data['NN'] = self.nn_input.value()
        data['MM'] = self.mm_input.value()
        data['D_0'] = self.d0_input.value()
        data['NUMERICAL_DERIVATIVES'] = self.numerical_derivatives_checkbox.isChecked()
        data['NOPBC'] = self.nopbc_checkbox.isChecked()
        data['SERIAL'] = self.serial_checkbox.isChecked()
        data['PAIR'] = self.pair_checkbox.isChecked()
        nlist_checked = self.nl_list_checkbox.isChecked()
        data['NLIST'] = nlist_checked
        if nlist_checked:
            data['NL_CUTOFF'] = self.nl_cutoff_input.value()
            data['NL_STRIDE'] = self.nl_stride_input.value()
        return data

    def populate_data(self, data):
        """
        根据传入的数据字典，设置高级参数对话框中的值和勾选状态
        """
        self.nn_input.setValue(data.get('NN', 6))
        self.mm_input.setValue(data.get('MM', 0))
        self.d0_input.setValue(data.get('D_0', 0.0))
        self.numerical_derivatives_checkbox.setChecked(data.get('NUMERICAL_DERIVATIVES', False))
        self.nopbc_checkbox.setChecked(data.get('NOPBC', False))
        self.serial_checkbox.setChecked(data.get('SERIAL', False))
        self.pair_checkbox.setChecked(data.get('PAIR', False))
        nlist = data.get('NLIST', False)
        self.nl_list_checkbox.setChecked(nlist)
        if nlist:
            self.nl_cutoff_input.setValue(data.get('NL_CUTOFF', 0.5))
            self.nl_stride_input.setValue(data.get('NL_STRIDE', 100))

class CoordinationPage(QtWidgets.QWidget):
    def __init__(self, group_labels, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        prompt = QtWidgets.QLabel("计算配位数")
        prompt.setWordWrap(True)
        prompt.setStyleSheet("font-weight: bold;")
        layout.addWidget(prompt)

        # ---- GROUPA ----
        groupA_group = QtWidgets.QGroupBox("GROUPA (选择第一组原子)")
        groupA_layout = QtWidgets.QVBoxLayout(groupA_group)

        self.groupA_mode = QtWidgets.QComboBox()
        self.groupA_mode.addItems(["范围模式", "单原子列表模式"])
        groupA_layout.addWidget(self.groupA_mode)

        self.groupA_stack = QtWidgets.QStackedWidget()
        self.groupA_range = AtomRangeWidget(group_labels)
        self.groupA_single = SingleAtomListWidget(group_labels)
        self.groupA_stack.addWidget(self.groupA_range)
        self.groupA_stack.addWidget(self.groupA_single)
        groupA_layout.addWidget(self.groupA_stack)
        layout.addWidget(groupA_group)

        # ---- GROUPB ----
        groupB_group = QtWidgets.QGroupBox("GROUPB (选择第二组原子)")
        groupB_layout = QtWidgets.QVBoxLayout(groupB_group)

        self.groupB_mode = QtWidgets.QComboBox()
        self.groupB_mode.addItems(["范围模式", "单原子列表模式"])
        groupB_layout.addWidget(self.groupB_mode)

        self.groupB_stack = QtWidgets.QStackedWidget()
        self.groupB_range = AtomRangeWidget(group_labels)
        self.groupB_single = SingleAtomListWidget(group_labels)
        self.groupB_stack.addWidget(self.groupB_range)
        self.groupB_stack.addWidget(self.groupB_single)
        groupB_layout.addWidget(self.groupB_stack)
        layout.addWidget(groupB_group)

        self.groupA_mode.currentIndexChanged.connect(self.groupA_stack.setCurrentIndex)
        self.groupB_mode.currentIndexChanged.connect(self.groupB_stack.setCurrentIndex)

        # ---- R_0 ----
        r0_layout = QtWidgets.QFormLayout()
        self.r0_label = QtWidgets.QLabel("R_0:")
        # 为 R_0 标签添加中文悬浮说明
        self.r0_label.setToolTip("R_0：切换函数的 r_0 参数(默认=0.3)")
        self.r0_input = QtWidgets.QDoubleSpinBox()
        self.r0_input.setRange(0.0, 10.0)
        self.r0_input.setDecimals(3)
        self.r0_input.setValue(0.3)
        r0_layout.addRow(self.r0_label, self.r0_input)

        r0_group = QtWidgets.QGroupBox("基本参数")
        r0_group.setLayout(r0_layout)
        layout.addWidget(r0_group)

        # ---- 高级设置按钮 ----
        self.adv_btn = QtWidgets.QPushButton("高级设置")
        layout.addWidget(self.adv_btn)
        self.adv_btn.clicked.connect(self.open_advanced_settings)

        # ---- 数据存储 ----
        self.cv_output = []
        self.advanced_settings = None  # 用于保存已打开的高级设置对话框

        self.setLayout(layout)

    def open_advanced_settings(self):
        if not self.advanced_settings:
            self.advanced_settings = AdvancedSettingsDialog(self)
        self.advanced_settings.show()
        self.advanced_settings.raise_()
        self.advanced_settings.activateWindow()

    def get_definition_line(self):
        # ---- 读取GROUPA ----
        if self.groupA_stack.currentIndex() == 0:  # 范围模式
            groupA = self.groupA_range.get_str()
        else:  # 单原子模式
            atoms = self.groupA_single.get_atoms()
            groupA = ','.join(atoms)

        # ---- 读取GROUPB ----
        if self.groupB_stack.currentIndex() == 0:  # 范围模式
            groupB = self.groupB_range.get_str()
        else:  # 单原子模式
            atoms = self.groupB_single.get_atoms()
            groupB = ','.join(atoms)

        r0 = self.r0_input.value()

        if not groupA:
            QtWidgets.QMessageBox.warning(self, "警告", "请填写GROUPA！")
            return None
        if not groupB:
            QtWidgets.QMessageBox.warning(self, "警告", "请填写GROUPB！")
            return None

        params = f"GROUPA={groupA} GROUPB={groupB} R_0={r0}"

        if self.advanced_settings:
            adv_data = self.advanced_settings.get_data()
            if adv_data['NUMERICAL_DERIVATIVES']:
                params += " NUMERICAL_DERIVATIVES"
            if adv_data['NOPBC']:
                params += " NOPBC"
            if adv_data['SERIAL']:
                params += " SERIAL"
            if adv_data['PAIR']:
                params += " PAIR"
            if adv_data['NLIST']:
                params += (
                    f" NLIST NL_CUTOFF={adv_data['NL_CUTOFF']} "
                    f"NL_STRIDE={adv_data['NL_STRIDE']}"
                )

            params += (
                f" NN={adv_data['NN']}"
                f" MM={adv_data['MM']}"
                f" D_0={adv_data['D_0']}"
            )

        return params

    def populate_data(self, cv_data):
        name = cv_data.get('name', '')
        if name:
            self.cv_output = [name]

        params = cv_data.get('params', '')
        tokens = params.split()

        groupA = ""
        groupB = ""
        r0 = 0.0

        adv_data = {
            'NN': 6,
            'MM': 0,
            'D_0': 0.0,
            'NUMERICAL_DERIVATIVES': False,
            'NOPBC': False,
            'SERIAL': False,
            'PAIR': False,
            'NLIST': False,
            'NL_CUTOFF': 0.5,
            'NL_STRIDE': 100,
        }

        for token in tokens:
            if token.startswith("GROUPA="):
                groupA = token[len("GROUPA="):]
            elif token.startswith("GROUPB="):
                groupB = token[len("GROUPB="):]
            elif token.startswith("R_0="):
                r0 = float(token[len("R_0="):])
            elif token.startswith("NN="):
                adv_data['NN'] = int(token[len("NN="):])
            elif token.startswith("MM="):
                adv_data['MM'] = int(token[len("MM="):])
            elif token.startswith("D_0="):
                adv_data['D_0'] = float(token[len("D_0="):])
            elif token == "NUMERICAL_DERIVATIVES":
                adv_data['NUMERICAL_DERIVATIVES'] = True
            elif token == "NOPBC":
                adv_data['NOPBC'] = True
            elif token == "SERIAL":
                adv_data['SERIAL'] = True
            elif token == "PAIR":
                adv_data['PAIR'] = True
            elif token == "NLIST":
                adv_data['NLIST'] = True
            elif token.startswith("NL_CUTOFF="):
                adv_data['NL_CUTOFF'] = float(token[len("NL_CUTOFF="):])
            elif token.startswith("NL_STRIDE="):
                adv_data['NL_STRIDE'] = int(token[len("NL_STRIDE="):])

        self.r0_input.setValue(r0)

        if groupA:
            if '-' in groupA:
                self.groupA_mode.setCurrentIndex(0)
                self.groupA_range.set_definition(groupA)
            else:
                self.groupA_mode.setCurrentIndex(1)
                self.groupA_single.populate_data(groupA)

        if groupB:
            if '-' in groupB:
                self.groupB_mode.setCurrentIndex(0)
                self.groupB_range.set_definition(groupB)
            else:
                self.groupB_mode.setCurrentIndex(1)
                self.groupB_single.populate_data(groupB)

        if not self.advanced_settings:
            self.advanced_settings = AdvancedSettingsDialog(self)
        self.advanced_settings.populate_data(adv_data)
