"""
accel_control.py
负责加速采样方法的控制逻辑
"""
from PyQt5 import QtWidgets

from .accel_definitios.metad_widget import MetadWidget
from .accel_definitios.lower_walls_widget import LowerWallsWidget
from .accel_definitios.upper_walls_widget import UpperWallsWidget
from .accel_definitios.restraint_widget import RestraintWidget
from .accel_definitios.biasvalue_widget import BiasValueWidget

# 新增：导入 ExternalWidget
from .accel_definitios.external_widget import ExternalWidget

class AccelerationMethodDialog(QtWidgets.QDialog):
    def __init__(self, cv_outputs, accel_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("加速采样方法定义")
        self.cv_outputs = cv_outputs
        self.accel_data = accel_data

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout()

        self.name_edit = QtWidgets.QLineEdit()
        form_layout.addRow("名称:", self.name_edit)

        self.type_combo = QtWidgets.QComboBox()
        # 在这里新增 "EXTERNAL"
        self.type_combo.addItems([
            "METAD",
            "LOWER_WALLS",
            "UPPER_WALLS",
            "RESTRAINT",
            "BIASVALUE",
            "EXTERNAL",
        ])
        form_layout.addRow("类型:", self.type_combo)

        self.stack = QtWidgets.QStackedWidget()
        form_layout.addRow(self.stack)

        self.metad_page = MetadWidget(self.cv_outputs)
        self.lower_walls_page = LowerWallsWidget(self.cv_outputs)
        self.upper_walls_page = UpperWallsWidget(self.cv_outputs)
        self.restraint_page = RestraintWidget(self.cv_outputs)
        self.biasvalue_page = BiasValueWidget(self.cv_outputs)
        # 新增
        self.external_page = ExternalWidget(self.cv_outputs)

        self.pages = {}
        self.pages["METAD"] = self.metad_page
        self.pages["LOWER_WALLS"] = self.lower_walls_page
        self.pages["UPPER_WALLS"] = self.upper_walls_page
        self.pages["RESTRAINT"] = self.restraint_page
        self.pages["BIASVALUE"] = self.biasvalue_page
        self.pages["EXTERNAL"] = self.external_page

        self.stack.addWidget(self.metad_page)
        self.stack.addWidget(self.lower_walls_page)
        self.stack.addWidget(self.upper_walls_page)
        self.stack.addWidget(self.restraint_page)
        self.stack.addWidget(self.biasvalue_page)
        self.stack.addWidget(self.external_page)

        self.type_combo.currentTextChanged.connect(
            lambda txt: self.stack.setCurrentWidget(self.pages[txt])
        )

        layout.addLayout(form_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("确定")
        self.cancel_btn = QtWidgets.QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        if self.accel_data:
            self.populate_data()

    def populate_data(self):
        name = self.accel_data.get('name','')
        t = self.accel_data.get('type','METAD')
        line = self.accel_data.get('line','')

        self.name_edit.setText(name)
        self.type_combo.setCurrentText(t)

        if t == "METAD" and line:
            self.metad_page.set_accmet_name(name if name else "metad_1")
            self.metad_page.populate_data(line)
        elif t == "LOWER_WALLS" and line:
            self.lower_walls_page.set_accmet_name(name if name else "lower_walls_1")
            self.lower_walls_page.populate_data(line)
        elif t == "UPPER_WALLS" and line:
            self.upper_walls_page.set_accmet_name(name if name else "upper_walls_1")
            self.upper_walls_page.populate_data(line)
        elif t == "RESTRAINT" and line:
            self.restraint_page.set_accmet_name(name if name else "restraint_1")
            self.restraint_page.populate_data(line)
        elif t == "BIASVALUE" and line:
            self.biasvalue_page.set_accmet_name(name if name else "biasvalue_1")
            self.biasvalue_page.populate_data(line)
        elif t == "EXTERNAL" and line:
            self.external_page.set_accmet_name(name if name else "external_1")
            self.external_page.populate_data(line)

    def get_data(self):
        t = self.type_combo.currentText()
        page = self.pages[t]
        method_name = self.name_edit.text().strip()
        if not method_name:
            method_name = t.lower() + "_1"

        page.set_accmet_name(method_name)
        line = page.get_definition_line()

        outputs = []
        if hasattr(page, 'get_outputs') and callable(page.get_outputs):
            outputs = page.get_outputs()

        return {
            'name': method_name,
            'type': t,
            'line': line,
            'outputs': outputs
        }
