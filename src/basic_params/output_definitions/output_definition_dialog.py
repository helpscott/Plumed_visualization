from PyQt5 import QtWidgets, QtCore

class OutputDefinitionDialog(QtWidgets.QDialog):
    """
    用于定义单个PRINT输出，包括：
      - FILE=xxx（默认COLVAR）
      - STRIDE=xxx（默认100）
      - 多个输出属性(通过“增加输出属性”按钮添加)
    最终生成一行: PRINT ARG=xxx,yyy,... FILE=xxx STRIDE=yyy
    """

    def __init__(self, available_outputs, output_data=None, parent=None):
        """
        :param available_outputs: List[str], 所有可供选择的输出属性(来自CV和加速采样)
        :param output_data: dict or None, 如果是编辑已有数据, 形如:
          {
            'file': 'COLVAR',
            'stride': 100,
            'args': ['cv1', 'metad_1.bias', ...],
            'line': 'PRINT ARG=cv1,metad_1.bias ...'
          }
        """
        super().__init__(parent)
        self.setWindowTitle("输出文件定义")
        self.available_outputs = available_outputs
        self.output_data = output_data or {}

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()

        # FILE
        self.file_label = QtWidgets.QLabel("FILE:")
        # 给FILE标签添加中文悬浮提示
        self.file_label.setToolTip(
            "输出文件的名称，用于保存指定输出量（默认为COLVAR）。"
        )
        self.file_line = QtWidgets.QLineEdit("COLVAR")
        form_layout.addRow(self.file_label, self.file_line)

        # STRIDE
        self.stride_label = QtWidgets.QLabel("STRIDE:")
        # 给STRIDE标签添加中文悬浮提示
        self.stride_label.setToolTip(
            "输出频率（默认为100），可控制每隔多少步输出一次。"
        )
        self.stride_spin = QtWidgets.QSpinBox()
        self.stride_spin.setRange(1, 999999)
        self.stride_spin.setValue(100)
        form_layout.addRow(self.stride_label, self.stride_spin)

        layout.addLayout(form_layout)

        # 输出属性（列表可添加/删除）
        self.output_group = QtWidgets.QGroupBox("输出属性(双击可删除)")
        og_layout = QtWidgets.QVBoxLayout(self.output_group)

        self.output_list = QtWidgets.QListWidget()
        og_layout.addWidget(self.output_list)

        self.add_output_btn = QtWidgets.QPushButton("增加输出属性")
        og_layout.addWidget(self.add_output_btn)

        layout.addWidget(self.output_group)

        # 按钮行
        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("确定")
        self.cancel_btn = QtWidgets.QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        # 绑定事件
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.add_output_btn.clicked.connect(self.add_output_attr)
        self.output_list.itemDoubleClicked.connect(self.remove_output_attr)

        # 如果是编辑模式，填充数据
        if self.output_data:
            self.populate_data(self.output_data)

    def add_output_attr(self):
        """
        弹出一个下拉框列出 available_outputs, 用户选中后加入 output_list
        """
        if not self.available_outputs:
            QtWidgets.QMessageBox.warning(self, "警告", "暂无可用的输出属性！")
            return

        attr, ok = QtWidgets.QInputDialog.getItem(
            self, "选择输出属性", "可用输出属性:",
            self.available_outputs, 0, False
        )
        if ok and attr:
            existing = [self.output_list.item(i).text() for i in range(self.output_list.count())]
            if attr in existing:
                QtWidgets.QMessageBox.warning(self, "警告", f"输出属性'{attr}'已存在！")
                return
            self.output_list.addItem(attr)

    def remove_output_attr(self, item):
        row = self.output_list.row(item)
        self.output_list.takeItem(row)

    def populate_data(self, data):
        """
        data 形如: {
            'file': 'COLVAR',
            'stride': 100,
            'args': [...],
            'line': 'PRINT ARG=xxx,... FILE=... STRIDE=...'
        }
        """
        self.file_line.setText(data.get('file', 'COLVAR'))
        self.stride_spin.setValue(data.get('stride', 100))
        args_list = data.get('args', [])
        for a in args_list:
            self.output_list.addItem(a)

    def get_data(self):
        """
        获取对话框当前数据（不含 line）
        """
        f = self.file_line.text().strip() or "COLVAR"
        stride_val = self.stride_spin.value()
        arg_list = [self.output_list.item(i).text().strip() for i in range(self.output_list.count())]

        return {
            'file': f,
            'stride': stride_val,
            'args': arg_list
        }

    def get_line(self):
        """
        生成 PRINT ARG=xxx,xxx FILE=xxx STRIDE=xxx
        """
        d = self.get_data()
        if not d['args']:
            QtWidgets.QMessageBox.warning(self, "警告", "请至少添加一个输出属性！")
            return None
        arg_str = ",".join(d['args'])
        line = f"PRINT ARG={arg_str} FILE={d['file']} STRIDE={d['stride']}"
        return line
