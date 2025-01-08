"""
cv_control.py
负责CV的控制逻辑
"""
from PyQt5 import QtWidgets

# ordinary
from .cv_definitions.Ordinary.angle_page import AnglePage
from .cv_definitions.Ordinary.torsion_page import TorsionPage
from .cv_definitions.Ordinary.volume_page import VolumePage
from .cv_definitions.Ordinary.coordination_page import CoordinationPage
from .cv_definitions.Ordinary.distance_page import DistancePage
from .cv_definitions.Ordinary.position_page import PositionPage
from .cv_definitions.Ordinary.extracv_page import ExtraCVPage
from .cv_definitions.Ordinary.energy_page import EnergyPage
from .cv_definitions.Ordinary.dipole_page import DipolePage
from .cv_definitions.Ordinary.dhenergy_page import DHENERGYPage
from .cv_definitions.Ordinary.constant_page import ConstantPage

# ------ 新增import ------
from .cv_definitions.Ordinary.cell_page import CellPage
from .cv_definitions.Ordinary.time_page import TimePage
# function
from .cv_definitions.function.combine_page import CombinePage
from .cv_definitions.function.custom_page import CustomPage
from .cv_definitions.function.sort_page import SortPage
from .cv_definitions.dis_from_ref.drmsd_page import DRMSDPage
from .cv_definitions.dis_from_ref.rmsd_page import RMSDPage
from .cv_definitions.dis_from_ref.multi_rmsd_page import MultiRMSDPage
from .cv_definitions.dis_from_ref.target_page import TargetPage
from .cv_definitions.unofficial.group_angle_page import GroupAnglePage


class CVDefinitionDialog(QtWidgets.QDialog):
    def __init__(self, group_labels, cv_data=None, mode='ordinary', parent=None):
        super().__init__(parent)
        self.setWindowTitle("CV定义")
        self.cv_data = cv_data
        self.group_labels = group_labels
        self.mode = mode

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()
        self.name_edit = QtWidgets.QLineEdit()
        form_layout.addRow("名称:", self.name_edit)

        self.type_combo = QtWidgets.QComboBox()
        if self.mode == 'ordinary':
            # 在此处加入 "CELL"
            self.type_combo.addItems([
                "ANGLE", "TORSION", "VOLUME",
                "COORDINATION", "DISTANCE", "POSITION",
                "EXTRACV", "ENERGY", "DIPOLE", "DHENERGY",
                "CONSTANT", "CELL", "TIME"   # <-- 新增 "CELL"
            ])
        elif self.mode == 'ref':
            self.type_combo.addItems(["DRMSD", "MULTI_RMSD", "RMSD", "TARGET"])
        elif self.mode == 'function':
            self.type_combo.addItems(["COMBINE", "CUSTOM", "SORT"])
        elif self.mode == 'unofficial':
            self.type_combo.addItems(["GROUP_ANGLE"])

        form_layout.addRow("类型:", self.type_combo)

        self.stack = QtWidgets.QStackedWidget()
        form_layout.addRow(self.stack)

        # ordinary pages
        self.ordinary_pages = {}
        self.ordinary_pages["ANGLE"] = AnglePage(self.group_labels)
        self.ordinary_pages["TORSION"] = TorsionPage(self.group_labels)
        self.ordinary_pages["VOLUME"] = VolumePage()
        self.ordinary_pages["COORDINATION"] = CoordinationPage(self.group_labels)
        self.ordinary_pages["DISTANCE"] = DistancePage(self.group_labels)
        self.ordinary_pages["POSITION"] = PositionPage(self.group_labels)
        self.ordinary_pages["EXTRACV"] = ExtraCVPage(self.group_labels)
        self.ordinary_pages["ENERGY"] = EnergyPage(self.group_labels)
        self.ordinary_pages["DIPOLE"] = DipolePage(self.group_labels)
        self.ordinary_pages["DHENERGY"] = DHENERGYPage(self.group_labels)
        self.ordinary_pages["CONSTANT"] = ConstantPage()
        # 新增
        self.ordinary_pages["CELL"] = CellPage()
        self.ordinary_pages["TIME"] = TimePage()
        self.ref_pages = {}
        self.ref_pages["DRMSD"] = DRMSDPage()
        self.ref_pages["RMSD"] = RMSDPage()
        self.ref_pages["MULTI_RMSD"] = MultiRMSDPage()
        self.ref_pages["TARGET"] = TargetPage()
        # function pages

        self.function_pages = {}
        self.function_pages["COMBINE"] = CombinePage(self.group_labels)
        self.function_pages["CUSTOM"] = CustomPage()
        self.function_pages["SORT"] = SortPage()

        self.unofficial_pages = {}
        self.unofficial_pages["GROUP_ANGLE"] = GroupAnglePage(self.group_labels)

        if self.mode == 'ordinary':
            for k in [
                "ANGLE", "TORSION", "VOLUME", "COORDINATION",
                "DISTANCE", "POSITION", "EXTRACV", "ENERGY",
                "DIPOLE", "DHENERGY", "CONSTANT", "CELL", "TIME"
            ]:
                self.stack.addWidget(self.ordinary_pages[k])
        elif self.mode == 'ref':
            for kk in [
                "DRMSD", "MULTI_RMSD", "RMSD", "TARGET"
            ]:
                self.stack.addWidget(self.ref_pages[kk])
        elif self.mode == 'function':
            for kkk in [
                "COMBINE", "CUSTOM", "SORT"
            ]:
                self.stack.addWidget(self.function_pages[kkk])
        elif self.mode == 'unofficial':
            for kkkk in [
                "GROUP_ANGLE"
            ]:
                self.stack.addWidget(self.unofficial_pages[kkkk])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addLayout(form_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("保存")
        self.cancel_btn = QtWidgets.QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.on_save_clicked)
        self.cancel_btn.clicked.connect(self.reject)
        self.setLayout(layout)

        if self.cv_data:
            self.populate_data()
        else:
            self.on_type_changed(self.type_combo.currentText())

    def on_type_changed(self, new_type):
        if self.mode == 'ordinary':
            page = self.ordinary_pages[new_type]
        elif self.mode == 'ref':
            page = self.ref_pages[new_type]
        elif self.mode == 'function':
            page = self.function_pages[new_type]
            if hasattr(self.parent(), 'get_all_cv_outputs'):
                page.cv_outputs = self.parent().get_all_cv_outputs()
        elif self.mode == 'unofficial':
            page = self.unofficial_pages.get(new_type)
        self.stack.setCurrentWidget(page)

    def populate_data(self):
        self.name_edit.setText(self.cv_data['name'])
        t = self.cv_data['type'].upper()
        self.type_combo.setCurrentText(t)

        if self.mode == 'ordinary':
            page = self.ordinary_pages.get(t, None)
        elif self.mode == 'ref':
            page = self.ref_pages.get(t, None)
        elif self.mode == 'function':
            page = self.function_pages.get(t, None)
            if page and hasattr(self.parent(), 'get_all_cv_outputs'):
                page.cv_outputs = self.parent().get_all_cv_outputs()
        elif self.mode == 'unofficial':
            page = self.unofficial_pages.get(t, None)

        if page:
            page.populate_data(self.cv_data)
            if hasattr(page, 'set_cv_name'):
                page.set_cv_name(self.cv_data['name'])

    def on_save_clicked(self):
        line = self.get_definition_line()
        if line is None:
            return
        cmd = self.type_combo.currentText()
        if self.mode == 'ordinary':
            page = self.ordinary_pages[cmd]
        elif self.mode == 'ref':
            page = self.ref_pages[cmd]
        elif self.mode == 'function':
            page = self.function_pages[cmd]
        elif self.mode == 'unofficial':
            page = self.unofficial_pages[cmd]

        name = self.name_edit.text().strip()
        if hasattr(page, 'set_cv_name'):
            page.set_cv_name(name)
        self.accept()

    def get_cv_output(self):
        cmd = self.type_combo.currentText()
        if self.mode == 'ordinary':
            page = self.ordinary_pages[cmd]
        elif self.mode == 'ref':
            page = self.ref_pages[cmd]
        elif self.mode == 'function':
            page = self.function_pages[cmd]
        elif self.mode == 'unofficial':
            page = self.unofficial_pages[cmd]

        if hasattr(page, 'get_cv_output'):
            return page.get_cv_output()
        else:
            cv_name = self.name_edit.text().strip()
            return [cv_name] if cv_name else []

    def get_definition_line(self):
        name = self.name_edit.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self, "警告", "请为CV定义名称！")
            return None

        cmd = self.type_combo.currentText()
        if self.mode == 'ordinary':
            page = self.ordinary_pages[cmd]
        elif self.mode == 'ref':
            page = self.ref_pages[cmd]
        elif self.mode == 'function':
            page = self.function_pages[cmd]
        elif self.mode == 'unofficial':
            page = self.unofficial_pages[cmd]

        params = page.get_definition_line()

        # 在这里，如果是普通CV，且不是 [VOLUME, DISTANCE, POSITION, EXTRACV, ENERGY, DIPOLE, DHENERGY, CONSTANT, CELL] 并且params为空 => 警告
        if self.mode == 'ordinary':
            if cmd not in [
                "VOLUME", "DISTANCE", "POSITION", "EXTRACV",
                "ENERGY", "DIPOLE", "DHENERGY", "CONSTANT", "CELL", "TIME"
            ] and not params:
                QtWidgets.QMessageBox.warning(self, "警告", "CV定义不完整！")
                return None

        line = f"{name}: {cmd}"
        if params:
            line += f" {params}"
        return line
