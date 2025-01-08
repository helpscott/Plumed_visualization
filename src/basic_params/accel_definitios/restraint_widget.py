"""
restraint_widget.py

实现了 RESTRAINT 方法的界面逻辑。
每个 ARG 可设置 AT, KAPPA, SLOPE（默认为0） 等参数，并提供一个高级选项：NUMERICAL_DERIVATIVES。
"""

from PyQt5 import QtWidgets, QtCore

class RestraintCVItem(QtWidgets.QWidget):
    """
    用于单个 ARG 的输入控件:
      - ARG (从 cv_outputs 列表里选择)
      - AT
      - KAPPA
      - SLOPE
    """
    remove_requested = QtCore.pyqtSignal(QtWidgets.QWidget)

    def __init__(self, cv_outputs, parent=None):
        super().__init__(parent)
        self.cv_outputs = cv_outputs

        layout = QtWidgets.QVBoxLayout(self)

        # 第一行：下拉选择 ARG + 删除按钮
        top_hlayout = QtWidgets.QHBoxLayout()
        self.arg_combo = QtWidgets.QComboBox()
        self.arg_combo.addItems(self.cv_outputs)
        top_hlayout.addWidget(QtWidgets.QLabel("选择ARG:"))
        top_hlayout.addWidget(self.arg_combo)

        self.remove_btn = QtWidgets.QPushButton("删除此项")
        self.remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        top_hlayout.addWidget(self.remove_btn)
        layout.addLayout(top_hlayout)

        # 第二行：AT, KAPPA, SLOPE
        param_form = QtWidgets.QFormLayout()

        # AT
        self.at_edit = QtWidgets.QLineEdit()
        self.at_edit.setPlaceholderText("AT：指定束缚位置")
        # KAPPA (默认=0.0)
        self.kappa_edit = QtWidgets.QLineEdit()
        self.kappa_edit.setPlaceholderText("KAPPA：(default=0.0) 指定谐合力常数")
        # SLOPE (默认=0.0)
        self.slope_edit = QtWidgets.QLineEdit()
        self.slope_edit.setPlaceholderText("SLOPE：(default=0.0) 指定线性力常数")

        param_form.addRow("AT:", self.at_edit)
        param_form.addRow("KAPPA:", self.kappa_edit)
        param_form.addRow("SLOPE:", self.slope_edit)

        layout.addLayout(param_form)
        self.setLayout(layout)

    def get_data(self):
        """
        返回本项的参数:
         {
           'ARG': "xxx",
           'AT': "...",
           'KAPPA': "...",
           'SLOPE': "..."
         }
        """
        return {
            'ARG': self.arg_combo.currentText().strip(),
            'AT': self.at_edit.text().strip(),
            'KAPPA': self.kappa_edit.text().strip(),
            'SLOPE': self.slope_edit.text().strip()
        }

    def populate_data(self, data):
        """
        将已有的设置回填到UI
        """
        arg_val = data.get('ARG', '')
        if arg_val in self.cv_outputs:
            self.arg_combo.setCurrentText(arg_val)
        self.at_edit.setText(data.get('AT', ''))
        self.kappa_edit.setText(data.get('KAPPA', ''))
        self.slope_edit.setText(data.get('SLOPE', ''))

    def refresh_cv_outputs(self, new_outputs):
        current_selected = self.arg_combo.currentText()
        self.arg_combo.clear()
        self.arg_combo.addItems(new_outputs)
        if current_selected in new_outputs:
            self.arg_combo.setCurrentText(current_selected)


class RestraintWidget(QtWidgets.QWidget):
    """
    界面逻辑:
      - 多个 ARG, 每个 ARG 有 AT/KAPPA/SLOPE
      - 高级选项：NUMERICAL_DERIVATIVES (checkbox)
      - 生成指令行:
        label: RESTRAINT ...
          ARG=d1,d2
          AT=..., ...
          KAPPA=..., ...
          SLOPE=..., ...
          NUMERICAL_DERIVATIVES  (如果勾选)
        ...
      - 默认输出: label.bias, label.force2
    """
    def __init__(self, cv_outputs, parent=None):
        super().__init__(parent)
        self.cv_outputs = cv_outputs
        self.items = []
        self.method_name = "restraint_1"

        main_layout = QtWidgets.QVBoxLayout(self)

        # 高级选项(只展示 NUMERICAL_DERIVATIVES)
        self.adv_group = QtWidgets.QGroupBox("高级选项")
        self.adv_group.setCheckable(True)
        self.adv_group.setChecked(False)
        adv_layout = QtWidgets.QVBoxLayout(self.adv_group)

        self.numderiv_checkbox = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES?")
        # 为NUMERICAL_DERIVATIVES添加中文悬浮提示
        self.numderiv_checkbox.setToolTip(
            "启用数值方式计算导数（默认关闭）"
        )
        adv_layout.addWidget(self.numderiv_checkbox)
        main_layout.addWidget(self.adv_group)

        # 主区域：多个 RestraintCVItem
        group_box = QtWidgets.QGroupBox("RESTRAINT - 选择多个ARG并设置参数")
        group_layout = QtWidgets.QVBoxLayout(group_box)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        container = QtWidgets.QWidget()
        self.container_layout = QtWidgets.QVBoxLayout(container)
        self.container_layout.setContentsMargins(0,0,0,0)
        scroll.setWidget(container)

        group_layout.addWidget(scroll)

        self.add_arg_btn = QtWidgets.QPushButton("添加ARG")
        self.add_arg_btn.clicked.connect(self.add_item)
        group_layout.addWidget(self.add_arg_btn)

        group_box.setLayout(group_layout)
        main_layout.addWidget(group_box)

        self.setLayout(main_layout)

    def set_accmet_name(self, new_name):
        if new_name.strip():
            self.method_name = new_name.strip()

    def add_item(self):
        item = RestraintCVItem(self.cv_outputs)
        item.remove_requested.connect(self.remove_item)
        self.items.append(item)
        self.container_layout.addWidget(item)

    def remove_item(self, item):
        self.items.remove(item)
        self.container_layout.removeWidget(item)
        item.deleteLater()

    def get_definition_line(self):
        """
        生成诸如:
           myrestraint: RESTRAINT ...
             ARG=d1,d2
             AT=1.0,1.5
             KAPPA=150.0,150.0
             SLOPE=0.0,0.0
             NUMERICAL_DERIVATIVES
           ...
        的多行字符串
        """
        if not self.items:
            QtWidgets.QMessageBox.warning(self, "警告", "请至少添加一个ARG")
            return None

        arg_list = []
        at_list = []
        kappa_list = []
        slope_list = []

        for it in self.items:
            d = it.get_data()
            arg_list.append(d['ARG'] or "")
            at_list.append(d['AT'] or "")
            kappa_list.append(d['KAPPA'] or "")
            slope_list.append(d['SLOPE'] or "")

        lines = [f"{self.method_name}: RESTRAINT ..."]

        # ARG=
        lines.append(f"   ARG={','.join(arg_list)}")

        def join_or_default(lst, default_val):
            return ",".join(x if x.strip() else default_val for x in lst)

        # 这里设定 AT 和 KAPPA 默认各 0.0, SLOPE=0.0
        at_default = "0.0"
        kappa_default = "0.0"
        slope_default = "0.0"

        lines.append(f"   AT={join_or_default(at_list, at_default)}")
        lines.append(f"   KAPPA={join_or_default(kappa_list, kappa_default)}")
        lines.append(f"   SLOPE={join_or_default(slope_list, slope_default)}")

        if self.adv_group.isChecked() and self.numderiv_checkbox.isChecked():
            lines.append("   NUMERICAL_DERIVATIVES")

        lines.append("...")
        return "\n".join(lines)

    def populate_data(self, full_text):
        """
        解析现有的 RESTRAINT 指令并回填到UI.
        形如:
          label: RESTRAINT ...
            ARG=d1,d2
            AT=1.0,1.5
            KAPPA=150.0,120.0
            SLOPE=10.0,0.0
            NUMERICAL_DERIVATIVES
          ...
        """
        lines = full_text.strip().splitlines()
        if len(lines) < 2:
            return

        first_line = lines[0].strip()
        if ":" in first_line:
            left, right = first_line.split(":", 1)
            self.method_name = left.strip()

        # 清空原有 items
        for it in self.items[:]:
            self.remove_item(it)

        arg_list = []
        at_list = []
        kappa_list = []
        slope_list = []
        numerical_deriv_found = False

        i = 1
        while i < len(lines):
            l = lines[i].strip()
            if l == "...":
                break
            if l.startswith("ARG="):
                arg_list = l.split("=", 1)[1].split(",")
                arg_list = [x.strip() for x in arg_list if x.strip()]
            elif l.startswith("AT="):
                at_list = l.split("=", 1)[1].split(",")
                at_list = [x.strip() for x in at_list]
            elif l.startswith("KAPPA="):
                kappa_list = l.split("=", 1)[1].split(",")
                kappa_list = [x.strip() for x in kappa_list]
            elif l.startswith("SLOPE="):
                slope_list = l.split("=", 1)[1].split(",")
                slope_list = [x.strip() for x in slope_list]
            elif "NUMERICAL_DERIVATIVES" in l:
                numerical_deriv_found = True
            i += 1

        # 对齐长度
        def fill_or_default(lst, length):
            while len(lst) < length:
                lst.append("")
            return lst

        max_n = len(arg_list)
        at_list = fill_or_default(at_list, max_n)
        kappa_list = fill_or_default(kappa_list, max_n)
        slope_list = fill_or_default(slope_list, max_n)

        for idx in range(max_n):
            item = RestraintCVItem(self.cv_outputs)
            data = {
                'ARG': arg_list[idx],
                'AT': at_list[idx],
                'KAPPA': kappa_list[idx],
                'SLOPE': slope_list[idx]
            }
            item.populate_data(data)
            item.remove_requested.connect(self.remove_item)
            self.items.append(item)
            self.container_layout.addWidget(item)

        if numerical_deriv_found:
            self.adv_group.setChecked(True)
            self.numderiv_checkbox.setChecked(True)

    def get_outputs(self):
        """
        RESTRAINT 默认输出:
         - label.bias
         - label.force2
        """
        return [f"{self.method_name}.bias", f"{self.method_name}.force2"]
