"""
cv_output_selector.py
将原先 MetadCVItem 的功能单独放到这里，便于后续复用或动态刷新CV输出列表
"""
from PyQt5 import QtWidgets, QtCore

class MetadCVItem(QtWidgets.QWidget):
    remove_requested = QtCore.pyqtSignal(QtWidgets.QWidget)

    def __init__(self, cv_outputs, parent=None):
        super().__init__(parent)
        self.cv_outputs = cv_outputs
        layout = QtWidgets.QVBoxLayout(self)

        h_layout = QtWidgets.QHBoxLayout()
        self.cv_combo = QtWidgets.QComboBox()
        # 初始化时加载cv_outputs列表
        self.cv_combo.addItems(self.cv_outputs)

        h_layout.addWidget(QtWidgets.QLabel("CV输出属性:"))
        h_layout.addWidget(self.cv_combo)

        self.remove_btn = QtWidgets.QPushButton("删除此CV")
        self.remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        h_layout.addWidget(self.remove_btn)
        layout.addLayout(h_layout)

        # 下面是 GRID_MIN, GRID_MAX, grid_bin, sigma 等参数
        grid_layout = QtWidgets.QFormLayout()
        # 1) GRID_MIN
        self.label_grid_min = QtWidgets.QLabel("GRID_MIN:")
        # 添加中文悬浮提示
        self.label_grid_min.setToolTip(
            "GRID_MIN：网格的下界(若都设置可进行网格预定义)，\n"
            "若不指定，则自动从数据中探测。"
        )
        self.grid_min_line = QtWidgets.QLineEdit()
        self.grid_min_line.setPlaceholderText("例如：-pi")
        grid_layout.addRow(self.label_grid_min, self.grid_min_line)

        # 2) GRID_MAX
        self.label_grid_max = QtWidgets.QLabel("GRID_MAX:")
        # 添加中文悬浮提示
        self.label_grid_max.setToolTip(
            "GRID_MAX：网格的上界(若都设置可进行网格预定义)，\n"
            "若不指定，则自动从数据中探测。"
        )
        self.grid_max_line = QtWidgets.QLineEdit()
        self.grid_max_line.setPlaceholderText("例如：pi")
        grid_layout.addRow(self.label_grid_max, self.grid_max_line)

        layout.addLayout(grid_layout)

        # 高级参数(可选)
        self.adv_box = QtWidgets.QGroupBox("此CV的高级参数(可选)")
        self.adv_box.setCheckable(True)
        self.adv_box.setChecked(False)
        adv_layout = QtWidgets.QFormLayout(self.adv_box)

        # 3) GRID_BIN
        self.label_grid_bin = QtWidgets.QLabel("GRID_BIN:")
        # 添加中文悬浮提示
        self.label_grid_bin.setToolTip(
            "GRID_BIN：网格的箱数"
        )
        self.grid_bin_spin = QtWidgets.QSpinBox()
        self.grid_bin_spin.setRange(1, 999999)
        self.grid_bin_spin.setValue(100)
        adv_layout.addRow(self.label_grid_bin, self.grid_bin_spin)

        # 4) SIGMA
        self.label_sigma = QtWidgets.QLabel("SIGMA:")
        # 添加中文悬浮提示
        self.label_sigma.setToolTip(
            "SIGMA：高斯 hills 的宽度"
        )
        self.sigma_spin = QtWidgets.QDoubleSpinBox()
        self.sigma_spin.setRange(0.0, 999999.0)
        self.sigma_spin.setDecimals(3)
        self.sigma_spin.setValue(0.2)
        adv_layout.addRow(self.label_sigma, self.sigma_spin)

        layout.addWidget(self.adv_box)
        self.setLayout(layout)

    def get_data(self):
        """
        将用户在UI中设置的参数整理为dict
        """
        cv_name = self.cv_combo.currentText().strip()
        grid_min = self.grid_min_line.text().strip()
        grid_max = self.grid_max_line.text().strip()

        params = {}
        params['ARG'] = cv_name
        if grid_min:
            params['GRID_MIN'] = grid_min
        if grid_max:
            params['GRID_MAX'] = grid_max
        if self.adv_box.isChecked():
            params['GRID_BIN'] = self.grid_bin_spin.value()
            params['SIGMA'] = self.sigma_spin.value()
        else:
            # 即使关闭高级选项，也为metad提供默认值
            params['GRID_BIN'] = 100
            params['SIGMA'] = 0.2

        return params

    def populate_data(self, data):
        """
        恢复已经保存的数据到UI
        """
        arg_val = data.get('ARG', '')
        if arg_val in self.cv_outputs:
            self.cv_combo.setCurrentText(arg_val)

        if 'GRID_MIN' in data:
            self.grid_min_line.setText(data['GRID_MIN'])
        if 'GRID_MAX' in data:
            self.grid_max_line.setText(data['GRID_MAX'])

        grid_bin_val = data.get('GRID_BIN', 100)
        sigma_val = data.get('SIGMA', 0.2)
        self.grid_bin_spin.setValue(int(grid_bin_val))
        self.sigma_spin.setValue(float(sigma_val))

        # 为保持一致性，这里自动勾选高级选项
        self.adv_box.setChecked(True)

    def refresh_cv_outputs(self, new_outputs):
        """
        如果需要动态刷新最新的cv输出属性，可在外部调用此函数
        """
        current_selected = self.cv_combo.currentText()
        self.cv_combo.clear()
        self.cv_combo.addItems(new_outputs)

        # 如果之前选中的cv依然存在，则重新选中
        if current_selected in new_outputs:
            self.cv_combo.setCurrentText(current_selected)
