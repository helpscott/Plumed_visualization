"""
biasvalue_widget.py

实现了 BIASVALUE 方法的界面逻辑。
可以添加多个 ARG (每个 ARG 无额外数值参数)，并提供一个高级选项：NUMERICAL_DERIVATIVES。

在指令行中形如:
  label: BIASVALUE ...
    ARG=d1,d2
    NUMERICAL_DERIVATIVES (可选)
  ...

输出量包括:
  - label.bias
  - label.{arg}_bias (对每个 arg 产生一个)
"""

from PyQt5 import QtWidgets, QtCore


class BiasValueCVItem(QtWidgets.QWidget):
    """
    用于单个 ARG 的输入控件:
      - ARG (从 cv_outputs 列表中选择)
    """
    remove_requested = QtCore.pyqtSignal(QtWidgets.QWidget)

    def __init__(self, cv_outputs, parent=None):
        super().__init__(parent)
        self.cv_outputs = cv_outputs

        layout = QtWidgets.QVBoxLayout(self)

        top_hlayout = QtWidgets.QHBoxLayout()
        self.arg_combo = QtWidgets.QComboBox()
        self.arg_combo.addItems(self.cv_outputs)
        top_hlayout.addWidget(QtWidgets.QLabel("选择ARG:"))
        top_hlayout.addWidget(self.arg_combo)

        self.remove_btn = QtWidgets.QPushButton("删除此项")
        self.remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        top_hlayout.addWidget(self.remove_btn)
        layout.addLayout(top_hlayout)

        self.setLayout(layout)

    def get_data(self):
        """
        返回一个 dict：
         {
           'ARG': <用户选择的内容>
         }
        """
        return {
            'ARG': self.arg_combo.currentText().strip()
        }

    def populate_data(self, data):
        """
        恢复已有的设置
        """
        arg_val = data.get('ARG', '')
        if arg_val in self.cv_outputs:
            self.arg_combo.setCurrentText(arg_val)

    def refresh_cv_outputs(self, new_outputs):
        """
        若需要动态刷新可选 ARG
        """
        current_selected = self.arg_combo.currentText()
        self.arg_combo.clear()
        self.arg_combo.addItems(new_outputs)
        if current_selected in new_outputs:
            self.arg_combo.setCurrentText(current_selected)


class BiasValueWidget(QtWidgets.QWidget):
    """
    界面逻辑:
      - 多个 ARG (每项只有 ARG)
      - 高级选项: NUMERICAL_DERIVATIVES (checkbox)
      - 生成指令行:
         label: BIASVALUE ...
           ARG=d1,d2,...
           NUMERICAL_DERIVATIVES (如果勾选)
         ...
      - 输出:
         - label.bias
         - label.{arg}_bias 对每个 arg 生成
    """
    def __init__(self, cv_outputs, parent=None):
        super().__init__(parent)
        self.cv_outputs = cv_outputs
        self.items = []
        self.method_name = "biasvalue_1"

        main_layout = QtWidgets.QVBoxLayout(self)

        # 高级选项
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

        # 主区域: 多个 BiasValueCVItem
        group_box = QtWidgets.QGroupBox("BIASVALUE - 选择多个ARG")
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
        item = BiasValueCVItem(self.cv_outputs)
        item.remove_requested.connect(self.remove_item)
        self.items.append(item)
        self.container_layout.addWidget(item)

    def remove_item(self, item):
        self.items.remove(item)
        self.container_layout.removeWidget(item)
        item.deleteLater()

    def get_definition_line(self):
        """
        生成指令行, 形如:
          mybias: BIASVALUE ...
            ARG=d1,d2
            NUMERICAL_DERIVATIVES
          ...
        """
        if not self.items:
            QtWidgets.QMessageBox.warning(self, "警告", "请至少添加一个ARG")
            return None

        arg_list = []
        for it in self.items:
            d = it.get_data()
            arg_list.append(d['ARG'])

        lines = [f"{self.method_name}: BIASVALUE ..."]
        lines.append(f"   ARG={','.join(arg_list)}")

        if self.adv_group.isChecked() and self.numderiv_checkbox.isChecked():
            lines.append("   NUMERICAL_DERIVATIVES")

        lines.append("...")
        return "\n".join(lines)

    def populate_data(self, full_text):
        """
        解析 BIASVALUE 指令并回填到UI,
        形如:
          label: BIASVALUE ...
            ARG=d1,d2
            NUMERICAL_DERIVATIVES
          ...
        """
        lines = full_text.strip().splitlines()
        if len(lines) < 2:
            return

        first_line = lines[0].strip()
        if ":" in first_line:
            left, _ = first_line.split(":", 1)
            self.method_name = left.strip()

        for it in self.items[:]:
            self.remove_item(it)

        arg_list = []
        numerical_derivatives_found = False

        i = 1
        while i < len(lines):
            l = lines[i].strip()
            if l == "...":
                break
            if l.startswith("ARG="):
                arg_list = l.split("=", 1)[1].split(",")
                arg_list = [x.strip() for x in arg_list if x.strip()]
            elif "NUMERICAL_DERIVATIVES" in l:
                numerical_derivatives_found = True
            i += 1

        for arg in arg_list:
            item = BiasValueCVItem(self.cv_outputs)
            item.populate_data({'ARG': arg})
            item.remove_requested.connect(self.remove_item)
            self.items.append(item)
            self.container_layout.addWidget(item)

        if numerical_derivatives_found:
            self.adv_group.setChecked(True)
            self.numderiv_checkbox.setChecked(True)

    def get_outputs(self):
        """
        BIASVALUE 输出:
         - label.bias
         - label.{arg}_bias (对每个 arg)
        """
        outputs = [f"{self.method_name}.bias"]
        arg_list = []
        for it in self.items:
            d = it.get_data()
            arg_list.append(d['ARG'])
        # 对每个 arg 都加上 _bias
        for arg in arg_list:
            outputs.append(f"{self.method_name}.{arg}_bias")
        return outputs
