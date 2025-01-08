# pathtools_widget.py

from PyQt5 import QtWidgets, QtCore

class PathToolsWidget(QtWidgets.QWidget):
    """
    pathtools 工具界面：
      - 用户可在“使用 --start + --end”或“使用 --path”之间二选一
      - 必需参数：
          --fixed, --metric, --out, --arg-fmt, --tolerance,
          --nframes-before-start, --nframes, --nframes-after-end
      - 其余可选参数：--help/-h
      当输入发生变化时，发出 params_changed 信号，上层页面可更新命令行。
    """
    params_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # 顶部说明
        desc_label = QtWidgets.QLabel("一个可用于从 pdb 数据中构建路径 (path) 的工具，或将原路径重新均匀化。")
        desc_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(desc_label)

        # --------------------------------------------------------------------
        # 二选一： (start+end)  OR  (path)
        # --------------------------------------------------------------------
        group = QtWidgets.QGroupBox("选择路径来源：")
        group_layout = QtWidgets.QFormLayout(group)

        self.mode_combo = QtWidgets.QComboBox()
        # 两种模式：1) 使用 --start + --end   2) 使用 --path
        self.mode_combo.addItems(["使用 --start + --end", "使用 --path"])
        group_layout.addRow("模式:", self.mode_combo)

        # 用两个不同的Widget分别放置
        self.startend_widget = QtWidgets.QWidget()
        se_layout = QtWidgets.QFormLayout(self.startend_widget)

        # --start
        self.start_edit = QtWidgets.QLineEdit()
        self.start_edit.setPlaceholderText(
            "指定 start.pdb：这是用于路径起始帧的pdb文件（详见 Group 的原子列表说明）"
        )
        se_layout.addRow("--start:", self.start_edit)

        # --end
        self.end_edit = QtWidgets.QLineEdit()
        self.end_edit.setPlaceholderText(
            "指定 end.pdb：这是用于路径终止帧的pdb文件（详见 Group 的原子列表说明）"
        )
        se_layout.addRow("--end:", self.end_edit)

        self.path_widget = QtWidgets.QWidget()
        p_layout = QtWidgets.QFormLayout(self.path_widget)

        # --path
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setPlaceholderText(
            "指定含不等间隔帧的pdb文件 (in_path.pdb)：用于重新均匀化路径"
        )
        p_layout.addRow("--path:", self.path_edit)

        # 默认显示 start+end widget
        self.stacked_mode = QtWidgets.QStackedWidget()
        self.stacked_mode.addWidget(self.startend_widget)  # index=0
        self.stacked_mode.addWidget(self.path_widget)      # index=1
        group_layout.addRow(self.stacked_mode)

        layout.addWidget(group)
        group.setLayout(group_layout)

        # 监听下拉改变
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)

        # --------------------------------------------------------------------
        # 必需参数
        # --------------------------------------------------------------------
        essential_form = QtWidgets.QFormLayout()

        self.fixed_edit = QtWidgets.QLineEdit()
        self.fixed_edit.setPlaceholderText("指定要固定的帧序号(如 2,12)")
        essential_form.addRow("--fixed:", self.fixed_edit)

        self.metric_edit = QtWidgets.QLineEdit()
        self.metric_edit.setPlaceholderText("选择距离度量方式 (如 EUCLIDEAN, OPTIMAL)")
        essential_form.addRow("--metric:", self.metric_edit)

        self.out_edit = QtWidgets.QLineEdit()
        self.out_edit.setPlaceholderText("输出路径文件名 (如 final_path.pdb)")
        essential_form.addRow("--out:", self.out_edit)

        self.argfmt_edit = QtWidgets.QLineEdit()
        self.argfmt_edit.setPlaceholderText("指定帧中坐标值的格式 (默认=f)")
        essential_form.addRow("--arg-fmt:", self.argfmt_edit)

        self.tol_edit = QtWidgets.QLineEdit()
        self.tol_edit.setPlaceholderText("指定重新参数化的容忍度(默认=1E-4)")
        essential_form.addRow("--tolerance:", self.tol_edit)

        self.nframes_before_edit = QtWidgets.QLineEdit()
        self.nframes_before_edit.setPlaceholderText("在首帧之前要插入的帧数(默认=1)")
        essential_form.addRow("--nframes-before-start:", self.nframes_before_edit)

        self.nframes_edit = QtWidgets.QLineEdit()
        self.nframes_edit.setPlaceholderText("start与end之间要插入的帧数(默认=1)")
        essential_form.addRow("--nframes:", self.nframes_edit)

        self.nframes_after_edit = QtWidgets.QLineEdit()
        self.nframes_after_edit.setPlaceholderText("在末帧之后要插入的帧数(默认=1)")
        essential_form.addRow("--nframes-after-end:", self.nframes_after_edit)

        layout.addLayout(essential_form)

        # --------------------------------------------------------------------
        # 其它可选： --help/-h
        # --------------------------------------------------------------------
        self.help_cb = QtWidgets.QCheckBox("--help/-h")
        self.help_cb.setToolTip("打印帮助信息(help)")
        layout.addWidget(self.help_cb)

        # 监听输入变化
        # lineEdits
        all_edits = [
            self.start_edit, self.end_edit, self.path_edit,
            self.fixed_edit, self.metric_edit, self.out_edit,
            self.argfmt_edit, self.tol_edit,
            self.nframes_before_edit, self.nframes_edit, self.nframes_after_edit
        ]
        for w in all_edits:
            w.textChanged.connect(self.params_changed.emit)

        # combo
        self.mode_combo.currentIndexChanged.connect(self.params_changed.emit)

        # checkBox
        self.help_cb.stateChanged.connect(self.params_changed.emit)

        self.setLayout(layout)
        self.on_mode_changed(0)  # 初始显示

    def on_mode_changed(self, idx):
        """
        当用户在 "使用 --start + --end" 与 "使用 --path" 间切换时，切换堆叠Widget
        """
        if idx == 0:
            # 使用 start+end
            self.stacked_mode.setCurrentIndex(0)
        else:
            # 使用 path
            self.stacked_mode.setCurrentIndex(1)

    def get_command_flags(self):
        """
        返回 pathtools 的 list_of_flags, 不包含 "plumed pathtools"
        """
        flags = []

        # 根据模式判断
        mode_idx = self.mode_combo.currentIndex()
        if mode_idx == 0:
            # 使用 --start + --end
            start_val = self.start_edit.text().strip()
            if start_val:
                flags.append("--start")
                flags.append(start_val)

            end_val = self.end_edit.text().strip()
            if end_val:
                flags.append("--end")
                flags.append(end_val)
        else:
            # 使用 --path
            path_val = self.path_edit.text().strip()
            if path_val:
                flags.append("--path")
                flags.append(path_val)

        # 必需参数
        fixed_val = self.fixed_edit.text().strip()
        if fixed_val:
            flags.append("--fixed")
            flags.append(fixed_val)

        metric_val = self.metric_edit.text().strip()
        if metric_val:
            flags.append("--metric")
            flags.append(metric_val)

        out_val = self.out_edit.text().strip()
        if out_val:
            flags.append("--out")
            flags.append(out_val)

        argfmt_val = self.argfmt_edit.text().strip()
        if argfmt_val:
            flags.append("--arg-fmt")
            flags.append(argfmt_val)

        tol_val = self.tol_edit.text().strip()
        if tol_val:
            flags.append("--tolerance")
            flags.append(tol_val)

        nframes_before_val = self.nframes_before_edit.text().strip()
        if nframes_before_val:
            flags.append("--nframes-before-start")
            flags.append(nframes_before_val)

        nframes_val = self.nframes_edit.text().strip()
        if nframes_val:
            flags.append("--nframes")
            flags.append(nframes_val)

        nframes_after_val = self.nframes_after_edit.text().strip()
        if nframes_after_val:
            flags.append("--nframes-after-end")
            flags.append(nframes_after_val)

        # 可选: --help/-h
        if self.help_cb.isChecked():
            flags.append("--help")

        return flags
