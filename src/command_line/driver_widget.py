# driver_widget.py

from PyQt5 import QtWidgets, QtCore

class DriverWidget(QtWidgets.QWidget):
    """
    driver 命令行工具页面：
      - 一种允许人们使用 plumed 对现有轨迹进行后处理的工具。
      - 轨迹文件格式(只能选择一个)：
          --ixyz, --igro, --idlp4, --ixtc, --itrr
          --mf_dcd, --mf_crd, --mf_crdbox, --mf_gro, --mf_g96,
          --mf_trr, --mf_trj, --mf_xtc, --mf_pdb
      - 必需参数: --plumed, --timestep, --trajectory-stride, --multi
      - 其它可选参数：--length-units, --mass-units, --charge-units, --kt,
        --dump-forces, --dump-forces-fmt, --pdb, --mc, --box, --natoms,
        --initial-step, --debug-forces
      - 布尔/开关选项：--noatoms, --parse-only, --dump-full-virial
      - 新增：--help/-h, --help-debug
    当参数变化时，发射 params_changed 信号，上层可更新命令行。
    """
    params_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # 顶部说明
        desc_label = QtWidgets.QLabel("一种允许人们使用 plumed 对现有轨迹进行后处理的工具。")
        desc_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(desc_label)

        # --------------------------------------------------------------------
        # 轨迹格式 (只能选择一个) + 输入框
        # --------------------------------------------------------------------
        format_group = QtWidgets.QGroupBox("轨迹文件格式 (只能选择一种)")
        format_layout = QtWidgets.QHBoxLayout(format_group)

        self.format_combo = QtWidgets.QComboBox()
        # 用一个列表保存可供选择的轨迹格式对应的命令行参数
        self.format_options = [
            ("(不使用任何轨迹)", ""),  # 如果用户不想给轨迹
            ("--ixyz (xyz格式)", "--ixyz"),
            ("--igro (gro格式)", "--igro"),
            ("--idlp4 (DL_POLY_4格式)", "--idlp4"),
            ("--ixtc (xtc, xdrfile实现)", "--ixtc"),
            ("--itrr (trr, xdrfile实现)", "--itrr"),
            ("--mf_dcd (molfile: dcd格式)", "--mf_dcd"),
            ("--mf_crd (molfile: crd格式)", "--mf_crd"),
            ("--mf_crdbox (molfile: crdbox格式)", "--mf_crdbox"),
            ("--mf_gro (molfile: gro格式)", "--mf_gro"),
            ("--mf_g96 (molfile: g96格式)", "--mf_g96"),
            ("--mf_trr (molfile: trr格式)", "--mf_trr"),
            ("--mf_trj (molfile: trj格式)", "--mf_trj"),
            ("--mf_xtc (molfile: xtc格式)", "--mf_xtc"),
            ("--mf_pdb (molfile: pdb格式)", "--mf_pdb"),
        ]
        for label, _cmd in self.format_options:
            self.format_combo.addItem(label)
        format_layout.addWidget(self.format_combo)

        self.format_file_edit = QtWidgets.QLineEdit()
        self.format_file_edit.setPlaceholderText("在此输入轨迹文件名，例如 trajectory.xyz")
        format_layout.addWidget(self.format_file_edit)

        layout.addWidget(format_group)
        format_group.setLayout(format_layout)

        # --------------------------------------------------------------------
        # 必需参数: --plumed, --timestep, --trajectory-stride, --multi
        # --------------------------------------------------------------------
        essential_form = QtWidgets.QFormLayout()

        self.plumed_edit = QtWidgets.QLineEdit()
        self.plumed_edit.setPlaceholderText("plumed输入文件名称 (默认=plumed.dat)")
        essential_form.addRow("--plumed:", self.plumed_edit)

        self.timestep_edit = QtWidgets.QLineEdit()
        self.timestep_edit.setPlaceholderText("用于生成此轨迹的时间步长(单位ps)，默认=1.0")
        essential_form.addRow("--timestep:", self.timestep_edit)

        self.trajstride_edit = QtWidgets.QLineEdit()
        self.trajstride_edit.setPlaceholderText("输出频率(每隔多少步存一个帧)，默认=1")
        essential_form.addRow("--trajectory-stride:", self.trajstride_edit)

        self.multi_edit = QtWidgets.QLineEdit()
        self.multi_edit.setPlaceholderText("设置多副本环境的副本数(需要MPI)，默认=0")
        essential_form.addRow("--multi:", self.multi_edit)

        layout.addLayout(essential_form)

        # --------------------------------------------------------------------
        # 其它选项(文本输入)
        # --length-units, --mass-units, --charge-units, --kt,
        # --dump-forces, --dump-forces-fmt, --pdb, --mc, --box, --natoms,
        # --initial-step, --debug-forces
        # --------------------------------------------------------------------
        others_form = QtWidgets.QFormLayout()

        self.lengthunits_edit = QtWidgets.QLineEdit()
        self.lengthunits_edit.setPlaceholderText("指定长度单位(字符串或数值)，如 A")
        others_form.addRow("--length-units:", self.lengthunits_edit)

        self.massunits_edit = QtWidgets.QLineEdit()
        self.massunits_edit.setPlaceholderText("指定pdb/mc文件里的质量单位(字符串或数值)")
        others_form.addRow("--mass-units:", self.massunits_edit)

        self.chargeunits_edit = QtWidgets.QLineEdit()
        self.chargeunits_edit.setPlaceholderText("指定pdb/mc文件里的电荷单位(字符串或数值)")
        others_form.addRow("--charge-units:", self.chargeunits_edit)

        self.kt_edit = QtWidgets.QLineEdit()
        self.kt_edit.setPlaceholderText("指定kBT, 不用在输入文件中再指定温度")
        others_form.addRow("--kt:", self.kt_edit)

        self.dumpforces_edit = QtWidgets.QLineEdit()
        self.dumpforces_edit.setPlaceholderText("指定要将力写入哪个文件，留空则不启用")
        others_form.addRow("--dump-forces:", self.dumpforces_edit)

        self.dumpforcesfmt_edit = QtWidgets.QLineEdit()
        self.dumpforcesfmt_edit.setPlaceholderText("指定输出力的格式(默认=%f)")
        others_form.addRow("--dump-forces-fmt:", self.dumpforcesfmt_edit)

        self.pdb_edit = QtWidgets.QLineEdit()
        self.pdb_edit.setPlaceholderText("提供一个含质量和电荷的pdb文件")
        others_form.addRow("--pdb:", self.pdb_edit)

        self.mc_edit = QtWidgets.QLineEdit()
        self.mc_edit.setPlaceholderText("提供一个由DUMPMASSCHARGE生成的质量电荷文件")
        others_form.addRow("--mc:", self.mc_edit)

        self.box_edit = QtWidgets.QLineEdit()
        self.box_edit.setPlaceholderText("逗号分隔的box尺寸(3表示正交，9表示通用)")
        others_form.addRow("--box:", self.box_edit)

        self.natoms_edit = QtWidgets.QLineEdit()
        self.natoms_edit.setPlaceholderText("当轨迹格式不含原子数时在此指定原子数")
        others_form.addRow("--natoms:", self.natoms_edit)

        self.initialstep_edit = QtWidgets.QLineEdit()
        self.initialstep_edit.setPlaceholderText("指定初始步数(默认=0)")
        others_form.addRow("--initial-step:", self.initialstep_edit)

        self.debugforces_edit = QtWidgets.QLineEdit()
        self.debugforces_edit.setPlaceholderText("输出一个文件，内含数值导数和解析导数比较")
        others_form.addRow("--debug-forces:", self.debugforces_edit)

        layout.addLayout(others_form)

        # --------------------------------------------------------------------
        # 其它布尔选项: --noatoms, --parse-only, --dump-full-virial
        # --------------------------------------------------------------------
        bool_layout = QtWidgets.QHBoxLayout()

        self.noatoms_cb = QtWidgets.QCheckBox("--noatoms")
        self.noatoms_cb.setToolTip("不要读取轨迹，改用plumed.dat里指定的colvar文件")

        self.parseonly_cb = QtWidgets.QCheckBox("--parse-only")
        self.parseonly_cb.setToolTip("读取plumed输入文件后立即停止")

        self.dumpfullvirial_cb = QtWidgets.QCheckBox("--dump-full-virial")
        self.dumpfullvirial_cb.setToolTip("配合--dump-forces使用，输出9分量的应力张量")

        bool_layout.addWidget(self.noatoms_cb)
        bool_layout.addWidget(self.parseonly_cb)
        bool_layout.addWidget(self.dumpfullvirial_cb)
        layout.addLayout(bool_layout)

        # --------------------------------------------------------------------
        # 新增布尔选项: --help/-h, --help-debug
        # --------------------------------------------------------------------
        help_layout = QtWidgets.QHBoxLayout()
        self.help_cb = QtWidgets.QCheckBox("--help/-h")
        self.help_cb.setToolTip("打印此工具的帮助信息(help)")
        self.helpdebug_cb = QtWidgets.QCheckBox("--help-debug")
        self.helpdebug_cb.setToolTip("打印可用于生成测试(regtests)的特殊选项信息")

        help_layout.addWidget(self.help_cb)
        help_layout.addWidget(self.helpdebug_cb)
        layout.addLayout(help_layout)

        # --------------------------------------------------------------------
        # 信号连接: 当输入变化时发出 params_changed 信号
        # --------------------------------------------------------------------
        # 组合全部 lineEdit
        all_lineedits = [
            self.format_file_edit,     # 轨迹文件名
            self.plumed_edit, self.timestep_edit, self.trajstride_edit, self.multi_edit,
            self.lengthunits_edit, self.massunits_edit, self.chargeunits_edit,
            self.kt_edit, self.dumpforces_edit, self.dumpforcesfmt_edit,
            self.pdb_edit, self.mc_edit, self.box_edit, self.natoms_edit,
            self.initialstep_edit, self.debugforces_edit
        ]
        for w in all_lineedits:
            w.textChanged.connect(self.params_changed.emit)

        # comboBox 也要监听
        self.format_combo.currentIndexChanged.connect(self.params_changed.emit)

        # 布尔复选框 (原有 + 新增)
        cbs = [
            self.noatoms_cb, self.parseonly_cb, self.dumpfullvirial_cb,
            self.help_cb, self.helpdebug_cb
        ]
        for cb in cbs:
            cb.stateChanged.connect(self.params_changed.emit)

        self.setLayout(layout)

    def get_command_flags(self):
        """
        根据用户输入，返回 'plumed driver' 的后半部分 flags 列表
        例如：["--ixyz", "trajectory.xyz", "--plumed", "plumed.dat", ...]
        """
        flags = []

        # ------------------ 轨迹格式 (Combo + FileEdit) ------------------
        idx = self.format_combo.currentIndex()
        if idx > 0:  # 用户选择了非“(不使用任何轨迹)”
            arg_name = self.format_options[idx][1]  # e.g. "--ixyz"
            traj_file = self.format_file_edit.text().strip()
            if traj_file:
                flags.append(arg_name)
                flags.append(traj_file)

        # ------------------ 必需参数: --plumed, --timestep, etc. ------------------
        plumed_val = self.plumed_edit.text().strip()
        if plumed_val:
            flags.append("--plumed")
            flags.append(plumed_val)

        timestep_val = self.timestep_edit.text().strip()
        if timestep_val:
            flags.append("--timestep")
            flags.append(timestep_val)

        trajstride_val = self.trajstride_edit.text().strip()
        if trajstride_val:
            flags.append("--trajectory-stride")
            flags.append(trajstride_val)

        multi_val = self.multi_edit.text().strip()
        if multi_val:
            flags.append("--multi")
            flags.append(multi_val)

        # ------------------ 其它文本输入选项 ------------------
        lengthunits_val = self.lengthunits_edit.text().strip()
        if lengthunits_val:
            flags.append("--length-units")
            flags.append(lengthunits_val)

        massunits_val = self.massunits_edit.text().strip()
        if massunits_val:
            flags.append("--mass-units")
            flags.append(massunits_val)

        chargeunits_val = self.chargeunits_edit.text().strip()
        if chargeunits_val:
            flags.append("--charge-units")
            flags.append(chargeunits_val)

        kt_val = self.kt_edit.text().strip()
        if kt_val:
            flags.append("--kt")
            flags.append(kt_val)

        dumpforces_val = self.dumpforces_edit.text().strip()
        if dumpforces_val:
            flags.append("--dump-forces")
            flags.append(dumpforces_val)

        dumpforcesfmt_val = self.dumpforcesfmt_edit.text().strip()
        if dumpforcesfmt_val:
            flags.append("--dump-forces-fmt")
            flags.append(dumpforcesfmt_val)

        pdb_val = self.pdb_edit.text().strip()
        if pdb_val:
            flags.append("--pdb")
            flags.append(pdb_val)

        mc_val = self.mc_edit.text().strip()
        if mc_val:
            flags.append("--mc")
            flags.append(mc_val)

        box_val = self.box_edit.text().strip()
        if box_val:
            flags.append("--box")
            flags.append(box_val)

        natoms_val = self.natoms_edit.text().strip()
        if natoms_val:
            flags.append("--natoms")
            flags.append(natoms_val)

        initialstep_val = self.initialstep_edit.text().strip()
        if initialstep_val:
            flags.append("--initial-step")
            flags.append(initialstep_val)

        debugforces_val = self.debugforces_edit.text().strip()
        if debugforces_val:
            flags.append("--debug-forces")
            flags.append(debugforces_val)

        # ------------------ 布尔选项: --noatoms, --parse-only, --dump-full-virial ------------------
        if self.noatoms_cb.isChecked():
            flags.append("--noatoms")

        if self.parseonly_cb.isChecked():
            flags.append("--parse-only")

        if self.dumpfullvirial_cb.isChecked():
            flags.append("--dump-full-virial")

        # ------------------ 新增布尔选项: --help/-h, --help-debug ------------------
        if self.help_cb.isChecked():
            # 同样地，为简单，可只加 "--help"
            flags.append("--help")
        if self.helpdebug_cb.isChecked():
            flags.append("--help-debug")

        return flags
