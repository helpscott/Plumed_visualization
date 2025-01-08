# sum_hills_widget.py

from PyQt5 import QtWidgets, QtCore

class SumHillsWidget(QtWidgets.QWidget):
    """
    sum_hills 参数设置页面:
      - 必须至少指定: --hills 或者 --histo (可多选)
      - 可指定: --stride, --outfile
      - 可指定: --bin, --min, --max
      - 可指定: --spacing, --idw, --outhisto, --kt, --sigma, --fmt
      - 复选框: --negbias, --nohistory, --mintozero, 以及新增的 --help/-h, --help-debug
    当参数变化时, 发出 params_changed 信号, 由上层同步更新命令行.
    """
    params_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # 在最上面增加一条说明
        desc_label = QtWidgets.QLabel("一个允许使用 plumed 对现有 hills/colvar 文件进行后期处理的工具")
        desc_label.setStyleSheet("font-weight: bold;")  # 可选，加个粗体
        layout.addWidget(desc_label)

        # -------- 第1排: --hills, --histo --------
        hills_layout = QtWidgets.QHBoxLayout()
        self.hills_edit = QtWidgets.QLineEdit()
        self.hills_edit.setPlaceholderText("指定 hills 文件的名称")
        hills_layout.addWidget(QtWidgets.QLabel("hills:"))
        hills_layout.addWidget(self.hills_edit)
        layout.addLayout(hills_layout)

        histo_layout = QtWidgets.QHBoxLayout()
        self.histo_edit = QtWidgets.QLineEdit()
        self.histo_edit.setPlaceholderText("指定直方图文件的名称，colvar/hills 文件比较好")
        histo_layout.addWidget(QtWidgets.QLabel("histo:"))
        histo_layout.addWidget(self.histo_edit)
        layout.addLayout(histo_layout)

        # -------- 第2排: --stride, --outfile --------
        row2_layout = QtWidgets.QHBoxLayout()
        self.stride_edit = QtWidgets.QLineEdit()
        self.stride_edit.setPlaceholderText("指定整合 hills 文件的步幅,默认0=never")
        row2_layout.addWidget(QtWidgets.QLabel("stride:"))
        row2_layout.addWidget(self.stride_edit)

        self.outfile_edit = QtWidgets.QLineEdit()
        self.outfile_edit.setPlaceholderText("指定 sumhills 的输出文件")
        row2_layout.addWidget(QtWidgets.QLabel("outfile:"))
        row2_layout.addWidget(self.outfile_edit)
        layout.addLayout(row2_layout)

        # -------- 第3排: --bin, --min, --max --------
        grid_form = QtWidgets.QFormLayout()
        self.bin_edit = QtWidgets.QLineEdit()
        self.bin_edit.setPlaceholderText("网格的箱数，如99,99")
        grid_form.addRow("bin:", self.bin_edit)

        self.min_edit = QtWidgets.QLineEdit()
        self.min_edit.setPlaceholderText("网格的下限，如-pi,-pi")
        grid_form.addRow("min:", self.min_edit)

        self.max_edit = QtWidgets.QLineEdit()
        self.max_edit.setPlaceholderText("网格的上限，如pi,pi")
        grid_form.addRow("max:", self.max_edit)
        layout.addLayout(grid_form)

        # -------- 第4排: 额外参数 --spacing, --idw, --outhisto, --kt, --sigma, --fmt --------
        extra_form = QtWidgets.QFormLayout()

        self.spacing_edit = QtWidgets.QLineEdit()
        self.spacing_edit.setPlaceholderText("网格间距,如 0.01,0.01 ")
        extra_form.addRow("spacing:", self.spacing_edit)

        self.idw_edit = QtWidgets.QLineEdit()
        self.idw_edit.setPlaceholderText("要处理的变量名，如t1,t2")
        extra_form.addRow("idw:", self.idw_edit)

        self.outhisto_edit = QtWidgets.QLineEdit()
        self.outhisto_edit.setPlaceholderText("指定直方图的输出文件")
        extra_form.addRow("outhisto:", self.outhisto_edit)

        self.kt_edit = QtWidgets.QLineEdit()
        self.kt_edit.setPlaceholderText("以能量单位指定温度以整合变量，如 0.6 (能量单位)")
        extra_form.addRow("kt:", self.kt_edit)

        self.sigma_edit = QtWidgets.QLineEdit()
        self.sigma_edit.setPlaceholderText("指定分箱的 sigma 的向量（仅在进行直方图分析时需要）")
        extra_form.addRow("sigma:", self.sigma_edit)

        self.fmt_edit = QtWidgets.QLineEdit()
        self.fmt_edit.setPlaceholderText("指定输出格式，如 %8.3f")
        extra_form.addRow("fmt:", self.fmt_edit)

        layout.addLayout(extra_form)

        # -------- 第5排: 三个复选框 --negbias, --nohistory, --mintozero --------
        cb_layout = QtWidgets.QHBoxLayout()

        # --negbias
        self.negbias_cb = QtWidgets.QCheckBox("--negbias")
        self.negbias_cb.setToolTip(
            "打印负偏压而不是自由能（仅在 well-tempered 和 flexible hills 下需要）"
        )

        # --nohistory
        self.nohistory_cb = QtWidgets.QCheckBox("--nohistory")
        self.nohistory_cb.setToolTip(
            "将偏压/直方图数据分块处理（不带历史），需配合 --stride 分块查看"
        )

        # --mintozero
        self.mintozero_cb = QtWidgets.QCheckBox("--mintozero")
        self.mintozero_cb.setToolTip(
            "将偏压/直方图的最小值整体平移到0，便于对比结果"
        )

        cb_layout.addWidget(self.negbias_cb)
        cb_layout.addWidget(self.nohistory_cb)
        cb_layout.addWidget(self.mintozero_cb)
        layout.addLayout(cb_layout)

        # -------- 第6排: 新增的复选框 --help/-h, --help-debug --------
        help_layout = QtWidgets.QHBoxLayout()
        self.help_cb = QtWidgets.QCheckBox("--help/-h")
        self.help_cb.setToolTip("打印帮助信息(help)")
        self.helpdebug_cb = QtWidgets.QCheckBox("--help-debug")
        self.helpdebug_cb.setToolTip("打印可用于生成测试(regtests)的特殊选项信息")

        help_layout.addWidget(self.help_cb)
        help_layout.addWidget(self.helpdebug_cb)
        layout.addLayout(help_layout)

        # 监听参数变化，发射 params_changed
        all_lineedits = [
            self.hills_edit, self.histo_edit, self.stride_edit, self.outfile_edit,
            self.bin_edit, self.min_edit, self.max_edit, self.spacing_edit,
            self.idw_edit, self.outhisto_edit, self.kt_edit, self.sigma_edit, self.fmt_edit
        ]
        for w in all_lineedits:
            w.textChanged.connect(self.params_changed.emit)

        all_checkboxes = [
            self.negbias_cb, self.nohistory_cb, self.mintozero_cb,
            self.help_cb, self.helpdebug_cb
        ]
        for cb in all_checkboxes:
            cb.stateChanged.connect(self.params_changed.emit)

        self.setLayout(layout)

    def get_command_flags(self):
        """
        返回 sum_hills 的 list_of_flags, 不包含 "plumed sum_hills"
        """
        flags = []

        # --hills
        hills_val = self.hills_edit.text().strip()
        if hills_val:
            flags.append("--hills")
            flags.append(hills_val)

        # --histo
        histo_val = self.histo_edit.text().strip()
        if histo_val:
            flags.append("--histo")
            flags.append(histo_val)

        # --stride
        stride_val = self.stride_edit.text().strip()
        if stride_val:
            flags.append("--stride")
            flags.append(stride_val)

        # --outfile
        outfile_val = self.outfile_edit.text().strip()
        if outfile_val:
            flags.append("--outfile")
            flags.append(outfile_val)

        # --bin
        bin_val = self.bin_edit.text().strip()
        if bin_val:
            flags.append("--bin")
            flags.append(bin_val)

        # --min
        min_val = self.min_edit.text().strip()
        if min_val:
            flags.append("--min")
            flags.append(min_val)

        # --max
        max_val = self.max_edit.text().strip()
        if max_val:
            flags.append("--max")
            flags.append(max_val)

        # --spacing
        spacing_val = self.spacing_edit.text().strip()
        if spacing_val:
            flags.append("--spacing")
            flags.append(spacing_val)

        # --idw
        idw_val = self.idw_edit.text().strip()
        if idw_val:
            flags.append("--idw")
            flags.append(idw_val)

        # --outhisto
        outhisto_val = self.outhisto_edit.text().strip()
        if outhisto_val:
            flags.append("--outhisto")
            flags.append(outhisto_val)

        # --kt
        kt_val = self.kt_edit.text().strip()
        if kt_val:
            flags.append("--kt")
            flags.append(kt_val)

        # --sigma
        sigma_val = self.sigma_edit.text().strip()
        if sigma_val:
            flags.append("--sigma")
            flags.append(sigma_val)

        # --fmt
        fmt_val = self.fmt_edit.text().strip()
        if fmt_val:
            flags.append("--fmt")
            flags.append(fmt_val)

        # 复选框: --negbias, --nohistory, --mintozero
        if self.negbias_cb.isChecked():
            flags.append("--negbias")
        if self.nohistory_cb.isChecked():
            flags.append("--nohistory")
        if self.mintozero_cb.isChecked():
            flags.append("--mintozero")

        # 新增复选框: --help/-h, --help-debug
        if self.help_cb.isChecked():
            # 这里为了简化处理，将 "--help/-h" 写成 "--help"
            # 或者你想直接加这两种写法也可
            flags.append("--help")
        if self.helpdebug_cb.isChecked():
            flags.append("--help-debug")

        return flags
