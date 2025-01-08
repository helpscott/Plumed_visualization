"""
constant_page.py
实现 CONSTANT CV 的主界面 + 高级参数编辑对话框，合并为一个文件

CONSTANT:
  - 支持一个或多个常数
    * 若只有1个 -> VALUE=xxx
    * 若多个  -> VALUES=xxx,xxx,...
  - 高级参数(NOPBC, NODERIV) 用单独按钮（本文件内的 ConstantAdvancedDialog）
  - 输出属性: name.v-0, name.v-1, ...
"""

from PyQt5 import QtWidgets, QtCore

class ConstantAdvancedDialog(QtWidgets.QDialog):
    """
    弹出对话框，用于编辑CONSTANT的两个关键字:
    - NOPBC
    - NODERIV
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CONSTANT 高级参数")
        self.resize(300, 120)

        layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()

        self.nopbc_cb = QtWidgets.QCheckBox("NOPBC")
        # 为NOPBC添加中文鼠标悬浮提示
        self.nopbc_cb.setToolTip("忽略周期性边界条件进行距离计算（默认关闭）")

        self.noderiv_cb = QtWidgets.QCheckBox("NODERIV")
        # 为NODERIV添加中文鼠标悬浮提示
        self.noderiv_cb.setToolTip("仅返回数值，无导数信息（默认关闭）")

        form_layout.addRow(self.nopbc_cb)
        form_layout.addRow(self.noderiv_cb)

        layout.addLayout(form_layout)

        # 按钮行
        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("确定")
        self.cancel_btn = QtWidgets.QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def populate_data(self, data):
        """
        data 可能形如:
        {
          'NOPBC': bool,
          'NODERIV': bool
        }
        """
        self.nopbc_cb.setChecked(data.get('NOPBC', False))
        self.noderiv_cb.setChecked(data.get('NODERIV', False))

    def get_data(self):
        """
        返回例如:
        {
          'NOPBC': bool,
          'NODERIV': bool
        }
        """
        return {
            'NOPBC': self.nopbc_cb.isChecked(),
            'NODERIV': self.noderiv_cb.isChecked(),
        }


class ConstantPage(QtWidgets.QWidget):
    """
    主界面：用户可添加多个常数或只有一个常数。
    若常数个数=1 -> VALUE=xxx
    若常数个数>1 -> VALUES=xxx,xxx,...
    高级参数(NOPBC, NODERIV) 由按键打开 ConstantAdvancedDialog
    输出: name.v-0, name.v-1, ...
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cv_name = ""
        self.adv_data = {
            'NOPBC': False,
            'NODERIV': False
        }
        layout = QtWidgets.QVBoxLayout(self)

        prompt = QtWidgets.QLabel("定义一个或多个常数")
        prompt.setWordWrap(True)
        prompt.setStyleSheet("font-weight: bold;")
        layout.addWidget(prompt)

        # 列表展示当前的常数
        self.value_list = QtWidgets.QListWidget()
        layout.addWidget(self.value_list)

        # 按钮行: "增加常数" "删除选中"
        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("增加常数")
        self.remove_btn = QtWidgets.QPushButton("删除选中")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.on_add_value)
        self.remove_btn.clicked.connect(self.on_remove_value)

        # 高级参数按钮
        self.adv_btn = QtWidgets.QPushButton("高级参数")
        self.adv_btn.clicked.connect(self.open_advanced_dialog)
        layout.addWidget(self.adv_btn)

        layout.addStretch()

    def on_add_value(self):
        """
        弹出一个对话框让用户输入一个浮点数
        """
        val, ok = QtWidgets.QInputDialog.getDouble(
            self, "增加常数", "请输入一个常数值:", 0.0, -1e8, 1e8, 6
        )
        if ok:
            item = QtWidgets.QListWidgetItem(str(val))
            self.value_list.addItem(item)

    def on_remove_value(self):
        """
        删除列表选中的常数
        """
        item = self.value_list.currentItem()
        if item:
            row = self.value_list.row(item)
            self.value_list.takeItem(row)

    def open_advanced_dialog(self):
        """
        弹出ConstantAdvancedDialog以编辑 NOPBC & NODERIV
        """
        dlg = ConstantAdvancedDialog(self)
        dlg.populate_data(self.adv_data)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.adv_data.update(dlg.get_data())

    def set_cv_name(self, name):
        self.cv_name = name

    def get_cv_output(self):
        """
        输出形如:
          [ "cv_name.v-0", "cv_name.v-1", ... ]
        """
        n = self.value_list.count()
        if not self.cv_name:
            return []
        return [f"{self.cv_name}.v-{i}" for i in range(n)]

    def get_definition_line(self):
        """
        生成CONSTANT的定义行:
          - 若只有1个 => VALUE= x
          - 若多个  => VALUES= x,y,z
          + 若NOPBC => 末尾加 " NOPBC"
          + 若NODERIV => 末尾加 " NODERIV"
        """
        n = self.value_list.count()
        if n < 1:
            QtWidgets.QMessageBox.warning(self, "警告", "请至少添加一个常数！")
            return None

        vals = []
        for i in range(n):
            val_str = self.value_list.item(i).text().strip()
            vals.append(val_str)

        if n == 1:
            line = f"VALUE={vals[0]}"
        else:
            line = f"VALUES={','.join(vals)}"

        if self.adv_data.get('NOPBC', False):
            line += " NOPBC"
        if self.adv_data.get('NODERIV', False):
            line += " NODERIV"

        return line

    def populate_data(self, cv_data):
        """
        cv_data形如:
        {
          'name': 'xxx',
          'type': 'CONSTANT',
          'params': 'VALUE=1.0 NOPBC' / 'VALUES=1.0,2.0 NODERIV' / ...
        }
        """
        params = cv_data.get('params','').split()

        self.value_list.clear()
        self.adv_data = {
            'NOPBC': False,
            'NODERIV': False
        }

        val_list_str = ""

        for token in params:
            if token.startswith("VALUE="):
                val_list_str = token[len("VALUE="):]
            elif token.startswith("VALUES="):
                val_list_str = token[len("VALUES="):]
            elif token=="NOPBC":
                self.adv_data['NOPBC'] = True
            elif token=="NODERIV":
                self.adv_data['NODERIV'] = True

        if ',' in val_list_str:
            arr = val_list_str.split(',')
            for a in arr:
                a = a.strip()
                if a:
                    item = QtWidgets.QListWidgetItem(a)
                    self.value_list.addItem(item)
        else:
            s = val_list_str.strip()
            if s:
                item = QtWidgets.QListWidgetItem(s)
                self.value_list.addItem(item)
