"""
external_widget.py

实现了 EXTERNAL 方法的界面逻辑。
可以添加多个 ARG，并需要指定 FILE=xxx.grid (由用户自行选择文件)，
可设置 SCALE (默认1.0), 以及NUMERICAL_DERIVATIVES / NOSPLINE / SPARSE 这三个可选布尔选项。
"""

from PyQt5 import QtWidgets, QtCore
import os

class ExternalCVItem(QtWidgets.QWidget):
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
        """返回 {'ARG': <用户选的CV>}"""
        return {
            'ARG': self.arg_combo.currentText().strip()
        }

    def populate_data(self, data):
        """恢复已有的设置"""
        arg_val = data.get('ARG', '')
        if arg_val in self.cv_outputs:
            self.arg_combo.setCurrentText(arg_val)

    def refresh_cv_outputs(self, new_outputs):
        current_selected = self.arg_combo.currentText()
        self.arg_combo.clear()
        self.arg_combo.addItems(new_outputs)
        if current_selected in new_outputs:
            self.arg_combo.setCurrentText(current_selected)


class ExternalWidget(QtWidgets.QWidget):
    """
    界面逻辑:
      - 多个 ARG
      - FILE=  (用户可通过按钮选择文件路径)
      - SCALE= (默认1.0)
      - 三个可选布尔: NUMERICAL_DERIVATIVES, NOSPLINE, SPARSE

      EXTERNAL 指令形如:
         label: EXTERNAL ...
           ARG=d1,d2
           FILE=bias.grid
           SCALE=1.0
           NUMERICAL_DERIVATIVES
           NOSPLINE
           SPARSE
         ...
    默认输出量只有 label.bias
    """

    def __init__(self, cv_outputs, parent=None):
        super().__init__(parent)
        self.cv_outputs = cv_outputs
        self.items = []
        self.method_name = "external_1"

        main_layout = QtWidgets.QVBoxLayout(self)

        # 顶部：文件、SCALE
        file_group = QtWidgets.QGroupBox("EXTERNAL 的基本设置")
        file_layout = QtWidgets.QFormLayout(file_group)

        self.file_edit = QtWidgets.QLineEdit()
        self.file_edit.setPlaceholderText("请选择外部势能文件 (如 bias.grid)")
        self.file_btn = QtWidgets.QPushButton("选择文件")
        self.file_btn.clicked.connect(self.select_file)
        file_h = QtWidgets.QHBoxLayout()
        file_h.addWidget(self.file_edit)
        file_h.addWidget(self.file_btn)
        file_layout.addRow("FILE:", file_h)

        # 创建一个标签并给其添加 tooltip
        self.scale_label = QtWidgets.QLabel("SCALE:")
        self.scale_label.setToolTip(
            "SCALE（默认=1.0）：可用于放大/缩小或反转外部势能，如需要负值等。"
        )
        self.scale_spin = QtWidgets.QDoubleSpinBox()
        self.scale_spin.setRange(-1e6, 1e6)
        self.scale_spin.setValue(1.0)
        self.scale_spin.setDecimals(4)
        file_layout.addRow(self.scale_label, self.scale_spin)

        main_layout.addWidget(file_group)

        # 中部：ARG 列表
        arg_group = QtWidgets.QGroupBox("多个ARG (变量)")
        arg_layout = QtWidgets.QVBoxLayout(arg_group)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        container = QtWidgets.QWidget()
        self.container_layout = QtWidgets.QVBoxLayout(container)
        self.container_layout.setContentsMargins(0,0,0,0)
        scroll.setWidget(container)

        arg_layout.addWidget(scroll)

        self.add_arg_btn = QtWidgets.QPushButton("添加ARG")
        self.add_arg_btn.clicked.connect(self.add_item)
        arg_layout.addWidget(self.add_arg_btn)

        main_layout.addWidget(arg_group)
        arg_group.setLayout(arg_layout)

        # 底部：高级布尔选项
        adv_group = QtWidgets.QGroupBox("高级选项")
        adv_group.setCheckable(True)
        adv_group.setChecked(False)
        adv_layout = QtWidgets.QVBoxLayout(adv_group)

        self.numderiv_checkbox = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        self.numderiv_checkbox.setToolTip(
            "NUMERICAL_DERIVATIVES (默认关闭)：使用数值方式计算导数。"
        )
        self.nospline_checkbox = QtWidgets.QCheckBox("NOSPLINE")
        self.nospline_checkbox.setToolTip(
            "NOSPLINE (默认关闭)：不使用样条插值来计算能量和力。"
        )
        self.sparse_checkbox = QtWidgets.QCheckBox("SPARSE")
        self.sparse_checkbox.setToolTip(
            "SPARSE (默认关闭)：表示外部势能使用稀疏网格。"
        )

        adv_layout.addWidget(self.numderiv_checkbox)
        adv_layout.addWidget(self.nospline_checkbox)
        adv_layout.addWidget(self.sparse_checkbox)

        main_layout.addWidget(adv_group)

        self.setLayout(main_layout)

    def set_accmet_name(self, new_name):
        if new_name.strip():
            self.method_name = new_name.strip()

    def select_file(self):
        """让用户选择一个文件 (不限定格式)"""
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "选择外部势能文件", os.getcwd(), "All Files (*.*)"
        )
        if fname:
            self.file_edit.setText(fname)

    def add_item(self):
        item = ExternalCVItem(self.cv_outputs)
        item.remove_requested.connect(self.remove_item)
        self.items.append(item)
        self.container_layout.addWidget(item)

    def remove_item(self, item):
        self.items.remove(item)
        self.container_layout.removeWidget(item)
        item.deleteLater()

    def get_definition_line(self):
        """
        生成 EXTERNAL 指令:
         myext: EXTERNAL ...
           ARG=d1,d2
           FILE=xxx.grid
           SCALE=1.0
           NUMERICAL_DERIVATIVES
           NOSPLINE
           SPARSE
         ...
        """
        if not self.items:
            QtWidgets.QMessageBox.warning(self, "警告", "请至少添加一个ARG")
            return None

        arg_list = []
        for it in self.items:
            d = it.get_data()
            arg_list.append(d['ARG'])

        lines = [f"{self.method_name}: EXTERNAL ..."]

        # ARG=
        lines.append(f"   ARG={','.join(arg_list)}")

        # FILE=
        fpath = self.file_edit.text().strip()
        if not fpath:
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择外部势能文件 (FILE)")
            return None
        lines.append(f"   FILE={fpath}")

        # SCALE
        scale_val = self.scale_spin.value()
        lines.append(f"   SCALE={scale_val}")

        # 若高级选项群组被勾选
        adv_group = self.findChild(QtWidgets.QGroupBox, "")
        if adv_group and adv_group.isChecked():
            if self.numderiv_checkbox.isChecked():
                lines.append("   NUMERICAL_DERIVATIVES")
            if self.nospline_checkbox.isChecked():
                lines.append("   NOSPLINE")
            if self.sparse_checkbox.isChecked():
                lines.append("   SPARSE")

        lines.append("...")
        return "\n".join(lines)

    def populate_data(self, full_text):
        """
        恢复形如:
           label: EXTERNAL ...
             ARG=d1,d2
             FILE=bias.grid
             SCALE=2.5
             NUMERICAL_DERIVATIVES
             NOSPLINE
             SPARSE
           ...
        的已有配置
        """
        lines = full_text.strip().splitlines()
        if len(lines) < 2:
            return

        first_line = lines[0].strip()
        if ":" in first_line:
            left, right = first_line.split(":", 1)
            self.method_name = left.strip()

        # 清空 items
        for it in self.items[:]:
            self.remove_item(it)

        # 重置 UI
        self.file_edit.clear()
        self.scale_spin.setValue(1.0)
        self.numderiv_checkbox.setChecked(False)
        self.nospline_checkbox.setChecked(False)
        self.sparse_checkbox.setChecked(False)

        arg_list = []
        advanced_flags = []

        i = 1
        while i < len(lines):
            l = lines[i].strip()
            if l == "...":
                break

            if l.startswith("ARG="):
                arg_list = l.split("=",1)[1].split(",")
                arg_list = [x.strip() for x in arg_list if x.strip()]
            elif l.startswith("FILE="):
                val = l.split("=",1)[1].strip()
                self.file_edit.setText(val)
            elif l.startswith("SCALE="):
                val = l.split("=",1)[1].strip()
                try:
                    self.scale_spin.setValue(float(val))
                except:
                    self.scale_spin.setValue(1.0)
            else:
                # 检测高级选项
                advanced_flags.append(l)

            i += 1

        # 恢复 arg
        for arg in arg_list:
            item = ExternalCVItem(self.cv_outputs)
            item.populate_data({'ARG': arg})
            item.remove_requested.connect(self.remove_item)
            self.items.append(item)
            self.container_layout.addWidget(item)

        # 如果有高级选项
        adv_group = self.findChild(QtWidgets.QGroupBox, "")
        if advanced_flags:
            adv_group.setChecked(True)
            if any("NUMERICAL_DERIVATIVES" in f for f in advanced_flags):
                self.numderiv_checkbox.setChecked(True)
            if any("NOSPLINE" in f for f in advanced_flags):
                self.nospline_checkbox.setChecked(True)
            if any("SPARSE" in f for f in advanced_flags):
                self.sparse_checkbox.setChecked(True)

    def get_outputs(self):
        """
        EXTERNAL 默认输出: label.bias
        """
        return [f"{self.method_name}.bias"]
