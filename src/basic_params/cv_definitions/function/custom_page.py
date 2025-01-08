"""
custom_page.py
function类型CV: CUSTOM

功能说明：
1) 可以添加多个ARG，每个ARG对应一个已定义的CV输出属性（从cv_outputs里选）。
2) 每个ARG都可以指定一个VAR名称：前三个若不修改则默认 x、y、z，从第4个开始若不修改则自动依次 x1,y1,z1,x2,y2,z2...
   用户也可以手动修改VAR名称。
3) FUNC：用户可在UI中输入自定义的函数表达式（字符串），不进行过多的格式限制。
4) PERIODIC：两种模式：
   - NO -> PERIODIC=NO
   - CUSTOM -> 用户输入两个数值上下界 -> PERIODIC=xxx,yyy
5) 高级参数NUMERICAL_DERIVATIVES(关键字型)可选。

输出写入时格式示例：
  ARG=d1.x,d2
  VAR=x,y
  FUNC=y-x
  PERIODIC=NO
  NUMERICAL_DERIVATIVES
"""

from PyQt5 import QtWidgets, QtCore

class CustomArgItem(QtWidgets.QWidget):
    """
    单个输入：选择一个已有的cv输出属性 + 指定VAR名称
    """
    remove_requested = QtCore.pyqtSignal(QtWidgets.QWidget)

    def __init__(self, cv_outputs, index=0, parent=None):
        super().__init__(parent)
        self.cv_outputs = cv_outputs
        self.index = index  # 第几个arg，用来给默认var命名
        layout = QtWidgets.QHBoxLayout(self)

        self.cv_combo = QtWidgets.QComboBox()
        self.cv_combo.addItems(self.cv_outputs)
        layout.addWidget(QtWidgets.QLabel("ARG:"))
        layout.addWidget(self.cv_combo)

        # VAR
        var_label = QtWidgets.QLabel("VAR:")
        # 为VAR标签添加中文悬浮提示
        var_label.setToolTip(
            "VAR：为该ARG在函数表达式中起的变量名。\n"
            "如前3个缺省为 x, y, z。之后可用 x1, y1, z1 等命名。"
        )
        layout.addWidget(var_label)
        self.var_line = QtWidgets.QLineEdit()
        # 自动给默认名称
        self.var_line.setText(self._default_var_name_by_index(self.index))
        layout.addWidget(self.var_line)

        self.remove_btn = QtWidgets.QPushButton("删除此项")
        self.remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(self.remove_btn)

        layout.addStretch()

    def _default_var_name_by_index(self, idx):
        """
        idx=0->x,1->y,2->z,3->x1,4->y1,5->z1,6->x2,y2,z2,...
        """
        base = idx // 3   # 以3为一个循环
        pos = idx % 3
        if base == 0:
            return ["x", "y", "z"][pos]  # idx in [0,1,2]
        else:
            prefix = ["x", "y", "z"][pos]
            return f"{prefix}{base}"

    def get_data(self):
        return {
            'arg': self.cv_combo.currentText().strip(),
            'var': self.var_line.text().strip()
        }

    def populate_data(self, data):
        # data应包含 'arg','var'
        arg_val = data.get('arg', '')
        var_val = data.get('var', self._default_var_name_by_index(self.index))

        if arg_val in self.cv_outputs:
            self.cv_combo.setCurrentText(arg_val)

        self.var_line.setText(var_val)


class CustomPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cv_name = ""
        self.cv_outputs = []  # 由外部注入
        layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("自定义函数 (CUSTOM)")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.prompt_label)

        # ARG + VAR
        self.arg_group = QtWidgets.QGroupBox("添加多个ARG并命名VAR")
        arg_vlayout = QtWidgets.QVBoxLayout(self.arg_group)

        self.arg_list_layout = QtWidgets.QVBoxLayout()
        arg_vlayout.addLayout(self.arg_list_layout)

        self.add_arg_btn = QtWidgets.QPushButton("增加一个ARG")
        arg_vlayout.addWidget(self.add_arg_btn)
        layout.addWidget(self.arg_group)

        # FUNC表达式
        func_form = QtWidgets.QFormLayout()
        func_label = QtWidgets.QLabel("FUNC:")
        # 为FUNC标签添加中文悬浮提示
        func_label.setToolTip(
            "FUNC：要计算的函数表达式。\n"
            "例如 (y - x)**2 或 sin(x)+cos(y) 等"
        )
        self.func_line = QtWidgets.QLineEdit()
        func_form.addRow(func_label, self.func_line)
        layout.addLayout(func_form)

        # PERIODIC
        self.periodic_group = QtWidgets.QGroupBox("周期性 (PERIODIC)")
        per_form = QtWidgets.QFormLayout(self.periodic_group)

        self.periodic_label = QtWidgets.QLabel("PERIODIC模式:")
        # 为PERIODIC标签添加中文悬浮提示
        self.periodic_label.setToolTip(
            "如果函数输出是周期性的，请输入上下界。\n"
            "如果不周期性，则设置 PERIODIC=NO。"
        )
        self.periodic_combo = QtWidgets.QComboBox()
        self.periodic_combo.addItems(["NO", "CUSTOM"])
        per_form.addRow(self.periodic_label, self.periodic_combo)

        # 当用户选择CUSTOM时输入上下界
        h_layout = QtWidgets.QHBoxLayout()
        self.per_min_line = QtWidgets.QLineEdit()
        self.per_max_line = QtWidgets.QLineEdit()
        h_layout.addWidget(QtWidgets.QLabel("下界:"))
        h_layout.addWidget(self.per_min_line)
        h_layout.addWidget(QtWidgets.QLabel("上界:"))
        h_layout.addWidget(self.per_max_line)
        per_form.addRow(h_layout)

        layout.addWidget(self.periodic_group)

        # 高级选项
        self.adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        self.adv_box.setCheckable(True)
        self.adv_box.setChecked(False)
        adv_layout = QtWidgets.QVBoxLayout(self.adv_box)
        self.num_deriv_cb = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 为 NUMERICAL_DERIVATIVES 复选框添加中文悬浮提示
        self.num_deriv_cb.setToolTip(
            "启用数值方式计算导数（默认关闭）"
        )
        adv_layout.addWidget(self.num_deriv_cb)

        layout.addWidget(self.adv_box)
        layout.addStretch()

        self.arg_items = []
        self.add_arg_btn.clicked.connect(self.add_arg_item)

        self.setLayout(layout)

    def add_arg_item(self):
        idx = len(self.arg_items)
        it = CustomArgItem(self.cv_outputs, index=idx)
        it.remove_requested.connect(self.remove_arg_item)
        self.arg_items.append(it)
        self.arg_list_layout.addWidget(it)

    def remove_arg_item(self, it):
        self.arg_items.remove(it)
        self.arg_list_layout.removeWidget(it)
        it.deleteLater()
        # 是否重排VAR？目前不自动重排，保留用户填写

    def set_cv_name(self, name):
        self.cv_name = name

    def get_cv_output(self):
        """这个CV只有自己名字作为输出"""
        return [self.cv_name] if self.cv_name else []

    def get_definition_line(self):
        # 1) ARG+VAR
        if not self.arg_items:
            QtWidgets.QMessageBox.warning(self, "警告", "CUSTOM 需要至少一个ARG！")
            return None
        arg_list = []
        var_list = []
        for i, it in enumerate(self.arg_items):
            d = it.get_data()
            if not d['arg']:
                QtWidgets.QMessageBox.warning(self, "警告", f"第{i+1}个ARG未选择！")
                return None
            arg_list.append(d['arg'])
            var_item = d['var'] if d['var'] else it._default_var_name_by_index(i)
            var_list.append(var_item)

        arg_str = ",".join(arg_list)
        var_str = ",".join(var_list)

        # 2) FUNC
        func_expr = self.func_line.text().strip()
        if not func_expr:
            QtWidgets.QMessageBox.warning(self, "警告", "请填写FUNC表达式！")
            return None

        # 3) PERIODIC
        if self.periodic_combo.currentText() == "NO":
            periodic_part = "PERIODIC=NO"
        else:
            # CUSTOM => 需要上下界
            pmin = self.per_min_line.text().strip()
            pmax = self.per_max_line.text().strip()
            if (not pmin) or (not pmax):
                QtWidgets.QMessageBox.warning(self, "警告", "PERIODIC=CUSTOM时，需要输入上下界！")
                return None
            periodic_part = f"PERIODIC={pmin},{pmax}"

        # 4) 高级
        adv_list = []
        if self.adv_box.isChecked():
            if self.num_deriv_cb.isChecked():
                adv_list.append("NUMERICAL_DERIVATIVES")

        # 组合
        # 例： ARG=a,b VAR=x,y FUNC=(y-x) PERIODIC=NO NUMERICAL_DERIVATIVES
        line_parts = []
        line_parts.append(f"ARG={arg_str}")
        line_parts.append(f"VAR={var_str}")
        line_parts.append(f"FUNC={func_expr}")
        line_parts.append(periodic_part)
        if adv_list:
            line_parts.extend(adv_list)

        return " ".join(line_parts)

    def populate_data(self, cv_data):
        """
        从params中解析:
          ARG=xxx
          VAR=xxx
          FUNC=xxx
          PERIODIC=xx or NO
          NUMERICAL_DERIVATIVES
        """
        params = cv_data.get('params', '').split()
        arg_val = ""
        var_val = ""
        func_val = ""
        periodic_val = ""
        numerical_deriv = False

        # 首先将 tokens 组合回去，如果有FUNC=xxxx(里面可能包含括号等)
        # 简易处理：基于空格分隔时，FUNC=后面可能会被截断
        # 但目前我们还是用最简单的解析方式
        for token in params:
            if token.startswith("ARG="):
                arg_val = token[len("ARG="):]
            elif token.startswith("VAR="):
                var_val = token[len("VAR="):]
            elif token.startswith("FUNC="):
                func_val = token[len("FUNC="):]
            elif token.startswith("PERIODIC="):
                periodic_val = token[len("PERIODIC="):]
            elif token == "NUMERICAL_DERIVATIVES":
                numerical_deriv = True

        self.func_line.setText(func_val)

        # PERIODIC
        if periodic_val.upper() == "NO":
            self.periodic_combo.setCurrentText("NO")
            self.per_min_line.clear()
            self.per_max_line.clear()
        else:
            self.periodic_combo.setCurrentText("CUSTOM")
            pparts = periodic_val.split(',')
            if len(pparts) == 2:
                self.per_min_line.setText(pparts[0].strip())
                self.per_max_line.setText(pparts[1].strip())

        # 高级
        if numerical_deriv:
            self.adv_box.setChecked(True)
            self.num_deriv_cb.setChecked(True)
        else:
            self.adv_box.setChecked(False)
            self.num_deriv_cb.setChecked(False)

        # 解析 ARG/VAR
        arg_list = arg_val.split(',') if arg_val else []
        var_list_ = var_val.split(',') if var_val else []
        length = len(arg_list)

        # 先清空现有items
        for it in self.arg_items[:]:
            self.remove_arg_item(it)

        for i in range(length):
            a = arg_list[i].strip()
            v = ""
            if i < len(var_list_):
                v = var_list_[i].strip()
            item = CustomArgItem(self.cv_outputs, index=i)
            item.populate_data({'arg': a, 'var': v})
            item.remove_requested.connect(self.remove_arg_item)
            self.arg_items.append(item)
            self.arg_list_layout.addWidget(item)
