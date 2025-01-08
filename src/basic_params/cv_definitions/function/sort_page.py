"""
sort_page.py
function类型CV: SORT

功能说明：
1) 可以添加多个ARG，每个ARG对应一个已定义的CV输出属性（从cv_outputs里选）。
2) 没有COEFFICIENTS、PARAMETERS、POWERS等，仅需指定ARG即可（多个）。
3) 高级选项包含NUMERICAL_DERIVATIVES(关键字)。若选则在输出中添加"NUMERICAL_DERIVATIVES"。
4) 输出属性形如 name.1, name.2, ...，即若有N个ARG，则生成N个输出属性。
"""

from PyQt5 import QtWidgets, QtCore

class SortArgItem(QtWidgets.QWidget):
    """
    单个输入：选择一个已有的cv输出属性
    """
    remove_requested = QtCore.pyqtSignal(QtWidgets.QWidget)

    def __init__(self, cv_outputs, parent=None):
        super().__init__(parent)
        self.cv_outputs = cv_outputs
        layout = QtWidgets.QHBoxLayout(self)

        self.cv_combo = QtWidgets.QComboBox()
        self.cv_combo.addItems(self.cv_outputs)
        layout.addWidget(QtWidgets.QLabel("ARG:"))
        layout.addWidget(self.cv_combo)

        self.remove_btn = QtWidgets.QPushButton("删除此项")
        self.remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(self.remove_btn)

        layout.addStretch()

    def get_data(self):
        return {
            'arg': self.cv_combo.currentText().strip()
        }

    def populate_data(self, arg_val):
        """ arg_val: 字符串 """
        if arg_val in self.cv_outputs:
            self.cv_combo.setCurrentText(arg_val)


class SortPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cv_name = ""
        self.cv_outputs = []  # 由外部注入
        layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("将指定多个CV输出属性进行排序 (SORT)")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.prompt_label)

        self.arg_group = QtWidgets.QGroupBox("指定多个ARG")
        arg_layout = QtWidgets.QVBoxLayout(self.arg_group)

        self.arg_list_layout = QtWidgets.QVBoxLayout()
        arg_layout.addLayout(self.arg_list_layout)

        self.add_arg_btn = QtWidgets.QPushButton("增加一个ARG")
        arg_layout.addWidget(self.add_arg_btn)
        layout.addWidget(self.arg_group)

        # 高级选项
        self.adv_box = QtWidgets.QGroupBox("高级参数(可选)")
        self.adv_box.setCheckable(True)
        self.adv_box.setChecked(False)
        adv_layout = QtWidgets.QVBoxLayout(self.adv_box)

        self.num_deriv_cb = QtWidgets.QCheckBox("NUMERICAL_DERIVATIVES")
        # 为NUMERICAL_DERIVATIVES复选框添加中文悬浮提示
        self.num_deriv_cb.setToolTip("启用数值方式计算导数（默认关闭）")
        adv_layout.addWidget(self.num_deriv_cb)

        layout.addWidget(self.adv_box)
        layout.addStretch()

        self.arg_items = []
        self.add_arg_btn.clicked.connect(self.add_arg_item)

        self.setLayout(layout)

    def add_arg_item(self):
        it = SortArgItem(self.cv_outputs)
        it.remove_requested.connect(self.remove_arg_item)
        self.arg_items.append(it)
        self.arg_list_layout.addWidget(it)

    def remove_arg_item(self, item):
        self.arg_items.remove(item)
        self.arg_list_layout.removeWidget(item)
        item.deleteLater()

    def set_cv_name(self, name):
        self.cv_name = name

    def get_cv_output(self):
        """
        若添加了N个ARG, 则输出属性为 [f"{self.cv_name}.{i}" for i in range(1,N+1)]
        """
        if not self.cv_name:
            return []
        n = len(self.arg_items)
        return [f"{self.cv_name}.{i}" for i in range(1, n + 1)]

    def get_definition_line(self):
        if not self.arg_items:
            QtWidgets.QMessageBox.warning(self, "警告", "SORT需要至少一个ARG")
            return None

        arg_list = []
        for it in self.arg_items:
            d = it.get_data()
            if not d['arg']:
                QtWidgets.QMessageBox.warning(self, "警告", "有ARG未选择CV输出属性")
                return None
            arg_list.append(d['arg'])

        arg_str = ",".join(arg_list)
        line = f"ARG={arg_str}"

        if self.adv_box.isChecked() and self.num_deriv_cb.isChecked():
            line += " NUMERICAL_DERIVATIVES"

        return line

    def populate_data(self, cv_data):
        """
        cv_data['params'] 可能包含 ARG=xxx NUMERICAL_DERIVATIVES?
        """
        params = cv_data.get('params', '').split()
        arg_val = ""
        is_numderiv = False

        for token in params:
            if token.startswith("ARG="):
                arg_val = token[len("ARG="):]
            elif token == "NUMERICAL_DERIVATIVES":
                is_numderiv = True

        self.adv_box.setChecked(is_numderiv)
        self.num_deriv_cb.setChecked(is_numderiv)

        if arg_val:
            arg_list = arg_val.split(',')
            # 清空已有
            for it in self.arg_items[:]:
                self.remove_arg_item(it)
            for a in arg_list:
                item = SortArgItem(self.cv_outputs)
                item.populate_data(a.strip())
                item.remove_requested.connect(self.remove_arg_item)
                self.arg_items.append(item)
                self.arg_list_layout.addWidget(item)
