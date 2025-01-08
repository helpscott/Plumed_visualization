"""
lower_walls_widget.py

实现了 LOWER_WALLS 方法的界面逻辑，
可以添加多个 WallsCVItem，每个CV都可设置 AT/KAPPA/OFFSET/EXP/EPS。
并且提供一个高级选项：NUMERICAL_DERIVATIVES。
"""

from PyQt5 import QtWidgets, QtCore


class WallsCVItem(QtWidgets.QWidget):
    """
    用于单个 ARG 的输入控件，包括:
      - ARG (从 cv_outputs 列表里选择)
      - AT
      - KAPPA
      - OFFSET
      - EXP
      - EPS
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

        # 第二行：AT, KAPPA
        param_form = QtWidgets.QFormLayout()

        # AT
        self.at_edit = QtWidgets.QLineEdit()
        self.at_edit.setPlaceholderText(
            "用于决定墙的位置 (默认示例 1.0)"
        )
        # KAPPA
        self.kappa_edit = QtWidgets.QLineEdit()
        self.kappa_edit.setPlaceholderText(
            "墙的力常数 (默认示例 150.0)"
        )

        param_form.addRow("AT:", self.at_edit)
        param_form.addRow("KAPPA:", self.kappa_edit)

        # 第三行：OFFSET, EXP, EPS
        self.offset_edit = QtWidgets.QLineEdit()
        self.offset_edit.setPlaceholderText(
            "墙的起点偏移量 (默认=0.0)"
        )
        self.exp_edit = QtWidgets.QLineEdit()
        self.exp_edit.setPlaceholderText(
            "幂次 (默认=2.0)"
        )
        self.eps_edit = QtWidgets.QLineEdit()
        self.eps_edit.setPlaceholderText(
            "缩放因子 (默认=1.0)"
        )

        param_form.addRow("OFFSET:", self.offset_edit)
        param_form.addRow("EXP:", self.exp_edit)
        param_form.addRow("EPS:", self.eps_edit)

        layout.addLayout(param_form)
        self.setLayout(layout)

    def get_data(self):
        """
        返回本项的参数：
         {
           'ARG': "xxx",
           'AT': "...",
           'KAPPA': "...",
           'OFFSET': "...",
           'EXP': "...",
           'EPS': "..."
         }
        若某些字段未填，则可用默认值(空字符串在后续拼接中可忽略或使用默认)。
        """
        data = {}
        data['ARG'] = self.arg_combo.currentText().strip()
        data['AT'] = self.at_edit.text().strip()
        data['KAPPA'] = self.kappa_edit.text().strip()
        data['OFFSET'] = self.offset_edit.text().strip()
        data['EXP'] = self.exp_edit.text().strip()
        data['EPS'] = self.eps_edit.text().strip()
        return data

    def populate_data(self, data):
        """
        将已有的设置回填到UI
        """
        arg_val = data.get('ARG', '')
        if arg_val in self.cv_outputs:
            self.arg_combo.setCurrentText(arg_val)

        self.at_edit.setText(data.get('AT', ''))
        self.kappa_edit.setText(data.get('KAPPA', ''))
        self.offset_edit.setText(data.get('OFFSET', ''))
        self.exp_edit.setText(data.get('EXP', ''))
        self.eps_edit.setText(data.get('EPS', ''))

    def refresh_cv_outputs(self, new_outputs):
        """
        若需要动态刷新可选的ARG
        """
        current_selected = self.arg_combo.currentText()
        self.arg_combo.clear()
        self.arg_combo.addItems(new_outputs)
        if current_selected in new_outputs:
            self.arg_combo.setCurrentText(current_selected)


class LowerWallsWidget(QtWidgets.QWidget):
    """
    界面逻辑：
      - 多个 ARG，每个 ARG 有 AT/KAPPA/OFFSET/EXP/EPS
      - 高级选项：NUMERICAL_DERIVATIVES (checkbox)
      - 生成指令行:
          label: LOWER_WALLS ...
             ARG=xxx,yyy
             AT=..., ...
             KAPPA=..., ...
             OFFSET=..., ...
             EXP=..., ...
             EPS=..., ...
             NUMERICAL_DERIVATIVES (如果勾选)
          ...
      - 输出: get_outputs -> [f"{label}.bias", f"{label}.force2"]
    """
    def __init__(self, cv_outputs, parent=None):
        super().__init__(parent)
        self.cv_outputs = cv_outputs
        self.walls_items = []
        self.method_name = "lower_walls_1"

        main_layout = QtWidgets.QVBoxLayout(self)

        # 基础参数的容器(可加更多全局性的参数时使用，这里只展示 NUMERICAL_DERIVATIVES)
        self.adv_group = QtWidgets.QGroupBox("高级选项")
        self.adv_group.setCheckable(True)
        self.adv_group.setChecked(False)
        adv_layout = QtWidgets.QVBoxLayout(self.adv_group)

        self.numderiv_checkbox = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES?")
        # 为 NUMERICAL_DERIVATIVES 添加中文悬浮提示
        self.numderiv_checkbox.setToolTip(
            "启用数值方式计算导数（默认关闭）"
        )
        adv_layout.addWidget(self.numderiv_checkbox)
        main_layout.addWidget(self.adv_group)

        # 管理多个 WallsCVItem
        walls_box = QtWidgets.QGroupBox("LOWER_WALLS - 选择多个ARG并设置参数")
        walls_layout = QtWidgets.QVBoxLayout(walls_box)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        container = QtWidgets.QWidget()
        self.container_layout = QtWidgets.QVBoxLayout(container)
        self.container_layout.setContentsMargins(0,0,0,0)
        scroll.setWidget(container)

        walls_layout.addWidget(scroll)

        # 添加按钮
        self.add_arg_btn = QtWidgets.QPushButton("添加ARG")
        self.add_arg_btn.clicked.connect(self.add_walls_item)
        walls_layout.addWidget(self.add_arg_btn)

        walls_box.setLayout(walls_layout)
        main_layout.addWidget(walls_box)

        self.setLayout(main_layout)

    def set_accmet_name(self, new_name):
        """
        AccelerationMethodDialog会调用这方法，给我们一个名字。
        我们这里把它理解为 lower_walls_name。
        """
        if new_name.strip():
            self.method_name = new_name.strip()

    def add_walls_item(self):
        item = WallsCVItem(self.cv_outputs)
        item.remove_requested.connect(self.remove_walls_item)
        self.walls_items.append(item)
        self.container_layout.addWidget(item)

    def remove_walls_item(self, item):
        self.walls_items.remove(item)
        self.container_layout.removeWidget(item)
        item.deleteLater()

    def get_definition_line(self):
        """
        生成形如：
           mywalls: LOWER_WALLS ...
              ARG=d1,d2
              AT=1.0,2.0
              KAPPA=150.0,150.0
              OFFSET=0,0
              EXP=2,2
              EPS=1,1
              NUMERICAL_DERIVATIVES
           ...
        的多行文本
        """
        if not self.walls_items:
            QtWidgets.QMessageBox.warning(self, "警告", "请至少添加一个ARG")
            return None

        # 收集所有参数
        arg_list = []
        at_list = []
        kappa_list = []
        offset_list = []
        exp_list = []
        eps_list = []

        for item in self.walls_items:
            d = item.get_data()
            arg_list.append(d['ARG'])
            at_list.append(d['AT'] or "")
            kappa_list.append(d['KAPPA'] or "")
            offset_list.append(d['OFFSET'] or "")
            exp_list.append(d['EXP'] or "")
            eps_list.append(d['EPS'] or "")

        lines = [f"{self.method_name}: LOWER_WALLS ..."]

        # ARG=
        lines.append(f"   ARG={','.join(arg_list)}")

        def join_or_default(lst, default_val):
            # 把空字符串转成 default_val
            return ",".join(x if x.strip() else default_val for x in lst)

        # 默认值
        at_default = "0.0"
        kappa_default = "150.0"
        offset_default = "0.0"
        exp_default = "2"
        eps_default = "1.0"

        lines.append(f"   AT={join_or_default(at_list, at_default)}")
        lines.append(f"   KAPPA={join_or_default(kappa_list, kappa_default)}")
        lines.append(f"   OFFSET={join_or_default(offset_list, offset_default)}")
        lines.append(f"   EXP={join_or_default(exp_list, exp_default)}")
        lines.append(f"   EPS={join_or_default(eps_list, eps_default)}")

        # 高级选项
        if self.adv_group.isChecked() and self.numderiv_checkbox.isChecked():
            lines.append("   NUMERICAL_DERIVATIVES")

        lines.append("...")
        return "\n".join(lines)

    def populate_data(self, full_text):
        """
        将已有的 LOWER_WALLS 指令解析并回填UI。
        """
        lines = full_text.strip().splitlines()
        if len(lines) < 2:
            return

        # 第一行解析 label
        first_line = lines[0].strip()
        if ":" in first_line:
            left, right = first_line.split(":", 1)
            self.method_name = left.strip()

        # 清空之前的 items
        for it in self.walls_items[:]:
            self.remove_walls_item(it)

        # 解析
        arg_list = []
        at_list = []
        kappa_list = []
        offset_list = []
        exp_list = []
        eps_list = []
        numerical_derivatives_found = False

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
            elif l.startswith("OFFSET="):
                offset_list = l.split("=", 1)[1].split(",")
                offset_list = [x.strip() for x in offset_list]
            elif l.startswith("EXP="):
                exp_list = l.split("=", 1)[1].split(",")
                exp_list = [x.strip() for x in exp_list]
            elif l.startswith("EPS="):
                eps_list = l.split("=", 1)[1].split(",")
                eps_list = [x.strip() for x in eps_list]
            elif "NUMERICAL_DERIVATIVES" in l:
                numerical_derivatives_found = True
            i += 1

        def fill_or_default(lst, length):
            while len(lst) < length:
                lst.append("")
            return lst

        max_count = len(arg_list)
        at_list = fill_or_default(at_list, max_count)
        kappa_list = fill_or_default(kappa_list, max_count)
        offset_list = fill_or_default(offset_list, max_count)
        exp_list = fill_or_default(exp_list, max_count)
        eps_list = fill_or_default(eps_list, max_count)

        for idx in range(max_count):
            item = WallsCVItem(self.cv_outputs)
            item_data = {
                'ARG': arg_list[idx],
                'AT': at_list[idx],
                'KAPPA': kappa_list[idx],
                'OFFSET': offset_list[idx],
                'EXP': exp_list[idx],
                'EPS': eps_list[idx],
            }
            item.populate_data(item_data)
            item.remove_requested.connect(self.remove_walls_item)
            self.walls_items.append(item)
            self.container_layout.addWidget(item)

        if numerical_derivatives_found:
            self.adv_group.setChecked(True)
            self.numderiv_checkbox.setChecked(True)

    def get_outputs(self):
        """
        LOWER_WALLS 默认输出:
         - label.bias
         - label.force2
        """
        return [f"{self.method_name}.bias", f"{self.method_name}.force2"]
