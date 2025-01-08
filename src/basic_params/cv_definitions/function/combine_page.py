from PyQt5 import QtWidgets, QtCore

class CombineArgItem(QtWidgets.QWidget):
    remove_requested = QtCore.pyqtSignal(QtWidgets.QWidget)

    def __init__(self, cv_outputs, parent=None):
        super().__init__(parent)
        self.cv_outputs = cv_outputs

        layout = QtWidgets.QHBoxLayout(self)

        self.cv_combo = QtWidgets.QComboBox()
        self.cv_combo.addItems(self.cv_outputs)
        layout.addWidget(QtWidgets.QLabel("ARG:"))
        layout.addWidget(self.cv_combo)

        # COEFFICIENTS
        coeff_label = QtWidgets.QLabel("COEFF:")
        # 为COEFFICIENTS标签添加中文悬浮提示
        coeff_label.setToolTip(
            "COEFFICIENTS（默认=1.0）：\n"
            "用于对各项ARG进行加权的系数"
        )
        self.coeff_spin = QtWidgets.QDoubleSpinBox()
        self.coeff_spin.setRange(-999999, 999999)
        self.coeff_spin.setValue(1.0)
        layout.addWidget(coeff_label)
        layout.addWidget(self.coeff_spin)

        # PARAMETERS
        param_label = QtWidgets.QLabel("PARAM:")
        # 为PARAMETERS标签添加中文悬浮提示
        param_label.setToolTip(
            "PARAMETERS（默认=0.0）：\n"
            "为函数中的各ARG添加一个位移/参数"
        )
        self.param_spin = QtWidgets.QDoubleSpinBox()
        self.param_spin.setRange(-999999, 999999)
        self.param_spin.setValue(0.0)
        layout.addWidget(param_label)
        layout.addWidget(self.param_spin)

        # POWERS
        power_label = QtWidgets.QLabel("POWER:")
        # 为POWERS标签添加中文悬浮提示
        power_label.setToolTip(
            "POWERS（默认=1.0）：\n"
            "将ARG提升到指定的幂次"
        )
        self.power_spin = QtWidgets.QDoubleSpinBox()
        self.power_spin.setRange(-999999, 999999)
        self.power_spin.setValue(1.0)
        layout.addWidget(power_label)
        layout.addWidget(self.power_spin)

        self.remove_btn = QtWidgets.QPushButton("删除此项")
        self.remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(self.remove_btn)

        layout.addStretch()

    def get_data(self):
        return {
            'arg': self.cv_combo.currentText().strip(),
            'coeff': self.coeff_spin.value(),
            'param': self.param_spin.value(),
            'power': self.power_spin.value(),
        }

    def populate_data(self, d):
        if d['arg'] in self.cv_outputs:
            self.cv_combo.setCurrentText(d['arg'])
        self.coeff_spin.setValue(d['coeff'])
        self.param_spin.setValue(d['param'])
        self.power_spin.setValue(d['power'])


class CombinePage(QtWidgets.QWidget):
    def __init__(self, group_labels, parent=None):
        super().__init__(parent)
        self.group_labels = group_labels
        self.cv_name = ""
        self.cv_outputs = []  # 由外部注入

        layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("计算一组变量的多项式组合 (COMBINE)")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.prompt_label)

        self.arg_group = QtWidgets.QGroupBox("选择多个CV输出属性，并设置参数")
        arg_layout = QtWidgets.QVBoxLayout(self.arg_group)

        self.arg_list_layout = QtWidgets.QVBoxLayout()
        arg_layout.addLayout(self.arg_list_layout)

        self.add_arg_btn = QtWidgets.QPushButton("增加一个ARG")
        arg_layout.addWidget(self.add_arg_btn)
        layout.addWidget(self.arg_group)

        # PERIODIC
        self.periodic_group = QtWidgets.QGroupBox("周期性设置 (PERIODIC)")
        periodic_layout = QtWidgets.QFormLayout(self.periodic_group)

        self.periodic_label = QtWidgets.QLabel("PERIODIC模式:")
        # 为PERIODIC标签添加中文悬浮提示
        self.periodic_label.setToolTip(
            "若函数输出是周期性的，则需指定周期区间。\n"
            "若输出不周期性，可设置 PERIODIC=NO。"
        )
        self.periodic_combo = QtWidgets.QComboBox()
        self.periodic_combo.addItems(["NO", "YES"])
        periodic_layout.addRow(self.periodic_label, self.periodic_combo)

        self.periodic_min_line = QtWidgets.QLineEdit()
        self.periodic_max_line = QtWidgets.QLineEdit()
        h_p = QtWidgets.QHBoxLayout()
        h_p.addWidget(QtWidgets.QLabel("下界:"))
        h_p.addWidget(self.periodic_min_line)
        h_p.addWidget(QtWidgets.QLabel("上界:"))
        h_p.addWidget(self.periodic_max_line)
        periodic_layout.addRow(h_p)

        layout.addWidget(self.periodic_group)

        # 高级参数
        self.adv_box = QtWidgets.QGroupBox("高级参数 (可选)")
        self.adv_box.setCheckable(True)
        self.adv_box.setChecked(False)
        adv_layout = QtWidgets.QFormLayout(self.adv_box)

        self.numerical_deriv_cb = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 为NUMERICAL_DERIVATIVES复选框添加中文悬浮提示
        self.numerical_deriv_cb.setToolTip(
            "启用数值方式计算导数（默认关闭）"
        )
        adv_layout.addRow(self.numerical_deriv_cb)

        self.normalize_cb = QtWidgets.QCheckBox("NORMALIZE")
        # 为NORMALIZE复选框添加中文悬浮提示
        self.normalize_cb.setToolTip(
            "将所有系数归一化，使它们加和后等于1（默认关闭）"
        )
        adv_layout.addRow(self.normalize_cb)

        layout.addWidget(self.adv_box)
        layout.addStretch()

        self.arg_items = []
        self.add_arg_btn.clicked.connect(self.add_arg_item)

        self.setLayout(layout)

    def add_arg_item(self):
        it = CombineArgItem(self.cv_outputs)
        it.remove_requested.connect(self.remove_arg_item)
        self.arg_items.append(it)
        self.arg_list_layout.addWidget(it)

    def remove_arg_item(self, it):
        self.arg_items.remove(it)
        self.arg_list_layout.removeWidget(it)
        it.deleteLater()

    def set_cv_name(self, name):
        self.cv_name = name

    def get_cv_output(self):
        return [self.cv_name] if self.cv_name else []

    def get_definition_line(self):
        if not self.arg_items:
            QtWidgets.QMessageBox.warning(self, "警告", "请至少添加一个ARG！")
            return None

        arg_list = []
        coeff_list = []
        param_list = []
        power_list = []

        for it in self.arg_items:
            d = it.get_data()
            arg_list.append(d['arg'])
            coeff_list.append(str(d['coeff']))
            param_list.append(str(d['param']))
            power_list.append(str(d['power']))

        # 必须至少1个ARG
        if not arg_list:
            QtWidgets.QMessageBox.warning(self, "警告", "COMBINE缺少ARG！")
            return None

        arg_str = ",".join(arg_list)
        coeff_str = ",".join(coeff_list)
        param_str = ",".join(param_list)
        power_str = ",".join(power_list)

        # PERIODIC
        if self.periodic_combo.currentText() == "NO":
            periodic_line = "PERIODIC=NO"
        else:
            p_min = self.periodic_min_line.text().strip()
            p_max = self.periodic_max_line.text().strip()
            if (not p_min) or (not p_max):
                QtWidgets.QMessageBox.warning(self, "警告", "周期模式为YES时，需要输入上下限!")
                return None
            periodic_line = f"PERIODIC={p_min},{p_max}"

        line = (
            f"ARG={arg_str} COEFFICIENTS={coeff_str} PARAMETERS={param_str} "
            f"POWERS={power_str} {periodic_line}"
        )

        if self.adv_box.isChecked():
            if self.numerical_deriv_cb.isChecked():
                line += " NUMERICAL_DERIVATIVES"
            if self.normalize_cb.isChecked():
                line += " NORMALIZE"

        return line

    def populate_data(self, cv_data):
        """
        从cv_data中拿到params, 解析
        """
        params = cv_data.get('params', '')
        tokens = params.split()

        arg_str = ""
        coeff_str = ""
        param_str = ""
        power_str = ""
        periodic_val = ""
        is_numderiv = False
        is_normalize = False

        for token in tokens:
            if token.startswith("ARG="):
                arg_str = token[len("ARG="):]
            elif token.startswith("COEFFICIENTS="):
                coeff_str = token[len("COEFFICIENTS="):]
            elif token.startswith("PARAMETERS="):
                param_str = token[len("PARAMETERS="):]
            elif token.startswith("POWERS="):
                power_str = token[len("POWERS="):]
            elif token.startswith("PERIODIC="):
                periodic_val = token[len("PERIODIC="):]
            elif token == "NUMERICAL_DERIVATIVES":
                is_numderiv = True
            elif token == "NORMALIZE":
                is_normalize = True

        # 填充高级
        self.adv_box.setChecked(is_numderiv or is_normalize)
        self.numerical_deriv_cb.setChecked(is_numderiv)
        self.normalize_cb.setChecked(is_normalize)

        # PERIODIC
        if periodic_val.upper() == "NO":
            self.periodic_combo.setCurrentText("NO")
            self.periodic_min_line.clear()
            self.periodic_max_line.clear()
        else:
            self.periodic_combo.setCurrentText("YES")
            parts = periodic_val.split(',')
            if len(parts) == 2:
                self.periodic_min_line.setText(parts[0].strip())
                self.periodic_max_line.setText(parts[1].strip())

        # 解析ARG
        arg_list = arg_str.split(',') if arg_str else []
        coeff_list_ = coeff_str.split(',') if coeff_str else []
        param_list_ = param_str.split(',') if param_str else []
        power_list_ = power_str.split(',') if power_str else []

        length = len(arg_list)

        def fill(lst, ln, default):
            while len(lst) < ln:
                lst.append(default)

        fill(coeff_list_, length, '1')
        fill(param_list_, length, '0')
        fill(power_list_, length, '1')

        for it in self.arg_items[:]:
            self.remove_arg_item(it)

        # 给 self.arg_items 重新创建
        for i in range(length):
            arg_d = {
                'arg': arg_list[i].strip(),
                'coeff': float(coeff_list_[i]),
                'param': float(param_list_[i]),
                'power': float(power_list_[i])
            }
            item = CombineArgItem(self.cv_outputs)
            item.populate_data(arg_d)
            item.remove_requested.connect(self.remove_arg_item)
            self.arg_items.append(item)
            self.arg_list_layout.addWidget(item)
