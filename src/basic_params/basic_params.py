# src/basic_params/basic_params.py

"""
basic_params.py
主文件，仅保留 BasicParamsWidget，其他逻辑拆分到 group_control.py、cv_control.py、accel_control.py、output_control.py
"""
import os
import subprocess
from PyQt5 import QtWidgets
from ..plumed_write.plumed_writer import write_plumed_file

# 引入拆分后的控制文件
from .group_control import GroupDefinitionDialog
from .cv_control import CVDefinitionDialog
from .accel_control import AccelerationMethodDialog
from .output_control import OutputFileController

# 保留对 restart_option 的引用
from .restart_option import get_restart_line

# 新增: 导入 ConfigManager
from .config_manager import ConfigManager

class BasicParamsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ------------------------
        # 原子群组定义
        group_group = QtWidgets.QGroupBox("原子群组定义（双击编辑）")
        g_layout = QtWidgets.QVBoxLayout(group_group)
        self.group_list = QtWidgets.QListWidget()
        g_layout.addWidget(self.group_list)

        g_btn_layout = QtWidgets.QHBoxLayout()
        self.add_group_btn = QtWidgets.QPushButton("增加原子群组")
        self.remove_group_btn = QtWidgets.QPushButton("删除选中群组")
        g_btn_layout.addWidget(self.add_group_btn)
        g_btn_layout.addWidget(self.remove_group_btn)
        g_btn_layout.addStretch()
        g_layout.addLayout(g_btn_layout)

        # ------------------------
        # CV定义
        cv_group = QtWidgets.QGroupBox("CV定义（双击编辑）")
        cv_layout = QtWidgets.QVBoxLayout(cv_group)
        self.cv_list = QtWidgets.QListWidget()
        cv_layout.addWidget(self.cv_list)

        cv_btn_layout = QtWidgets.QHBoxLayout()
        # 改名为“普通CV”
        self.add_cv_btn = QtWidgets.QPushButton("普通CV")
        self.remove_cv_btn = QtWidgets.QPushButton("删除选中CV")

        # 新增“函数”按钮
        self.function_btn = QtWidgets.QPushButton("函数")
        self.ref_btn = QtWidgets.QPushButton("参考结构对比")
        self.unofficial_btn = QtWidgets.QPushButton("非官方cv")

        cv_btn_layout.addWidget(self.add_cv_btn)
        cv_btn_layout.addWidget(self.ref_btn)
        cv_btn_layout.addWidget(self.function_btn)
        #cv_btn_layout.addWidget(self.unofficial_btn)
        cv_btn_layout.addWidget(self.remove_cv_btn)
        cv_btn_layout.addStretch()
        cv_layout.addLayout(cv_btn_layout)

        # ------------------------
        # 加速采样方法定义
        accel_group = QtWidgets.QGroupBox("加速采样方法定义（双击编辑）")
        a_layout = QtWidgets.QVBoxLayout(accel_group)
        self.accel_list = QtWidgets.QListWidget()
        a_layout.addWidget(self.accel_list)

        a_btn_layout = QtWidgets.QHBoxLayout()
        self.add_accel_btn = QtWidgets.QPushButton("增加加速采样方法")
        self.remove_accel_btn = QtWidgets.QPushButton("删除选中方法")
        a_btn_layout.addWidget(self.add_accel_btn)
        a_btn_layout.addWidget(self.remove_accel_btn)
        a_btn_layout.addStretch()
        a_layout.addLayout(a_btn_layout)

        self.restart_checkbox = QtWidgets.QCheckBox("使用RESTART指令?")
        a_layout.addWidget(self.restart_checkbox)

        # ------------------------
        # 输出文件定义
        output_group = QtWidgets.QGroupBox("输出文件定义（双击编辑）")
        o_layout = QtWidgets.QVBoxLayout(output_group)
        self.output_list = QtWidgets.QListWidget()
        o_layout.addWidget(self.output_list)

        o_btn_layout = QtWidgets.QHBoxLayout()
        self.add_output_btn = QtWidgets.QPushButton("增加输出文件")
        self.remove_output_btn = QtWidgets.QPushButton("删除选中输出文件")
        o_btn_layout.addWidget(self.add_output_btn)
        o_btn_layout.addWidget(self.remove_output_btn)
        o_btn_layout.addStretch()
        o_layout.addLayout(o_btn_layout)

        # ------------------------
        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(group_group)
        main_layout.addWidget(cv_group)
        main_layout.addWidget(accel_group)
        main_layout.addWidget(output_group)

        # 底部按钮：生成数据 + 查看文件 + 保存配置 + 加载配置
        bottom_btn_layout = QtWidgets.QHBoxLayout()
        self.generate_button = QtWidgets.QPushButton("生成数据")
        self.view_file_button = QtWidgets.QPushButton("查看文件")
        self.save_config_button = QtWidgets.QPushButton("保存配置")
        self.load_config_button = QtWidgets.QPushButton("加载配置")
        bottom_btn_layout.addStretch()
        bottom_btn_layout.addWidget(self.generate_button)
        bottom_btn_layout.addWidget(self.view_file_button)
        bottom_btn_layout.addWidget(self.save_config_button)
        bottom_btn_layout.addWidget(self.load_config_button)
        main_layout.addLayout(bottom_btn_layout)

        # 数据结构
        self.group_definitions = {}
        self.cv_definitions = {}
        self.accel_definitions = {}
        # 新增：输出文件管理器
        self.output_controller = OutputFileController()

        # 事件绑定
        # 群组
        self.add_group_btn.clicked.connect(self.add_group)
        self.remove_group_btn.clicked.connect(self.remove_group)
        self.group_list.itemDoubleClicked.connect(self.edit_group_item)

        # CV (普通/函数)
        self.add_cv_btn.clicked.connect(lambda: self.add_cv_with_mode('ordinary'))       # 普通CV
        self.ref_btn.clicked.connect(lambda: self.add_cv_with_mode('ref'))
        self.function_btn.clicked.connect(lambda: self.add_cv_with_mode('function'))  # 函数CV
        self.unofficial_btn.clicked.connect(lambda: self.add_cv_with_mode('unofficial'))
        self.remove_cv_btn.clicked.connect(self.remove_cv)
        self.cv_list.itemDoubleClicked.connect(self.edit_cv_item)

        # 加速采样
        self.add_accel_btn.clicked.connect(self.add_accel)
        self.remove_accel_btn.clicked.connect(self.remove_accel)
        self.accel_list.itemDoubleClicked.connect(self.edit_accel_item)

        # 输出文件
        self.add_output_btn.clicked.connect(self.add_output_file)
        self.remove_output_btn.clicked.connect(self.remove_output_file)
        self.output_list.itemDoubleClicked.connect(self.edit_output_file)

        # 生成 & 查看文件
        self.generate_button.clicked.connect(self.generate_file)
        self.view_file_button.clicked.connect(self.open_acc_dat_file)

        # 新增: 绑定保存和加载配置按钮
        self.save_config_button.clicked.connect(self.save_config)
        self.load_config_button.clicked.connect(self.load_config)

    # ------------------------
    # 群组
    def add_group(self):
        """添加一个新的原子群组，通过弹出对话框获取用户输入。"""
        dialog = GroupDefinitionDialog(
            self.get_single_atom_labels(),
            self.get_group_labels(),
            parent=self
        )
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            group_line = dialog.get_definition_line()
            group_data = dialog.get_group_data()
            if group_data and group_line:
                group_name = group_data['name']
                if group_name in self.group_definitions:
                    QtWidgets.QMessageBox.warning(self, "警告", "群组名称重复")
                    return
                self.group_definitions[group_name] = group_data
                self.group_list.addItem(group_name)

    def remove_group(self):
        item = self.group_list.currentItem()
        if not item:
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择一个群组")
            return
        group_name = item.text()
        if self.is_group_referenced(group_name):
            QtWidgets.QMessageBox.warning(
                self, "警告",
                f"无法删除群组 '{group_name}'，它正在被其他群组引用。"
            )
            return
        del self.group_definitions[group_name]
        self.group_list.takeItem(self.group_list.row(item))

    def edit_group_item(self, item):
        group_name = item.text()
        group_data = self.group_definitions.get(group_name, {})
        dialog = GroupDefinitionDialog(
            self.get_single_atom_labels(),
            self.get_group_labels(),
            group_data=group_data,
            parent=self
        )
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            new_group_data = dialog.get_group_data()
            new_group_line = dialog.get_definition_line()
            if new_group_data and new_group_line:
                new_group_name = new_group_data['name']
                if (new_group_name != group_name) and (new_group_name in self.group_definitions):
                    QtWidgets.QMessageBox.warning(self, "警告", "群组名称重复")
                    return
                del self.group_definitions[group_name]
                self.group_definitions[new_group_name] = new_group_data
                item.setText(new_group_name)

    # ------------------------
    # CV
    def add_cv_with_mode(self, mode):
        """根据模式添加不同类型的 CV。"""
        dialog = CVDefinitionDialog(
            self.get_group_labels(),
            mode=mode,
            parent=self
        )
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            cv_line = dialog.get_definition_line()
            if cv_line:
                cv_name = cv_line.split(':',1)[0].strip()
                if cv_name in self.cv_definitions:
                    QtWidgets.QMessageBox.warning(self, "警告", "CV名称重复")
                    return
                cv_outputs = dialog.get_cv_output()
                if not cv_outputs:
                    cv_outputs = [cv_name]
                self.cv_definitions[cv_name] = {
                    'line': cv_line,
                    'outputs': cv_outputs
                }
                self.cv_list.addItem(cv_name)

    def remove_cv(self):
        item = self.cv_list.currentItem()
        if not item:
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择一个CV")
            return
        cv_name = item.text()
        if self.is_cv_referenced(cv_name):
            QtWidgets.QMessageBox.warning(
                self, "警告",
                f"无法删除CV '{cv_name}'，它正在被加速采样方法引用。"
            )
            return
        del self.cv_definitions[cv_name]
        self.cv_list.takeItem(self.cv_list.row(item))

    def edit_cv_item(self, item):
        cv_name = item.text()
        cv_data_line = self.cv_definitions.get(cv_name, {}).get('line','')
        cv_data = self.parse_cv_line(cv_data_line)
        cv_data['name'] = cv_name

        cvs_ordinary = {
            "ANGLE", "TORSION", "VOLUME", "COORDINATION", "DISTANCE", "POSITION",
            "EXTRACV", "ENERGY", "DIPOLE", "DHENERGY", "CONSTANT", "CELL", "TIME"
        }
        cvs_function = {"COMBINE", "CUSTOM", "SORT"}
        cvs_ref = {"DRMSD", "MULTI_RMSD", "RMSD", "TARGET"}
        cvs_unofficial = {"GROUP_ANGLE"}

        cv_type_upper = cv_data['type'].upper()
        # 根据cv_data['type']判断mode
        if cv_type_upper in cvs_ordinary:
            mode_guess = "ordinary"
        elif cv_type_upper in cvs_function:
            mode_guess = "function"
        elif cv_type_upper in cvs_ref:
            mode_guess = "ref"
        elif cv_type_upper in cvs_unofficial:
            mode_guess = "unofficial"
        else:
            # 如果没有匹配到任何已知类型，可以根据需要设置默认值或抛出异常
            mode_guess = "ordinary"

        dialog = CVDefinitionDialog(
            self.get_group_labels(),
            cv_data=cv_data,
            mode=mode_guess,
            parent=self
        )
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            new_cv_line = dialog.get_definition_line()
            if new_cv_line:
                new_cv_name = new_cv_line.split(':',1)[0].strip()
                if (new_cv_name != cv_name) and (new_cv_name in self.cv_definitions):
                    QtWidgets.QMessageBox.warning(self, "警告", "CV名称重复")
                    return
                cv_outputs = dialog.get_cv_output()
                if not cv_outputs:
                    cv_outputs = [new_cv_name]
                del self.cv_definitions[cv_name]
                self.cv_definitions[new_cv_name] = {
                    'line': new_cv_line,
                    'outputs': cv_outputs
                }
                item.setText(new_cv_name)

    # ------------------------
    # 加速采样
    def add_accel(self):
        cv_outputs = self.get_all_cv_outputs()
        if not cv_outputs:
            QtWidgets.QMessageBox.warning(self, "警告","请先定义CV才能添加加速采样方法")
            return
        dialog = AccelerationMethodDialog(cv_outputs, parent=self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            t = data['type']
            line = data['line']
            name = data['name']
            outputs = data.get('outputs', [])  # 新增，从对话框获取
            if name in self.accel_definitions:
                idx = 2
                new_name = name + f"_{idx}"
                while new_name in self.accel_definitions:
                    idx += 1
                    new_name = name + f"_{idx}"
                name = new_name
            # 存储方式改为 dict，包含 outputs
            self.accel_definitions[name] = {
                'type': t,
                'line': line,
                'outputs': outputs
            }
            self.accel_list.addItem(name)

    def remove_accel(self):
        item = self.accel_list.currentItem()
        if not item:
            QtWidgets.QMessageBox.warning(self, "警告","请先选择一个加速采样方法")
            return
        name = item.text()
        del self.accel_definitions[name]
        self.accel_list.takeItem(self.accel_list.row(item))

    def edit_accel_item(self, item):
        name = item.text()
        existing_data = self.accel_definitions.get(name, None)
        if not existing_data:
            return
        t = existing_data.get('type', None)
        line = existing_data.get('line', None)
        outputs_old = existing_data.get('outputs', [])
        if not t or not line:
            return
        accel_data = {
            'name': name,
            'type': t,
            'line': line,
            'outputs': outputs_old
        }
        cv_outputs = self.get_all_cv_outputs()
        dialog = AccelerationMethodDialog(cv_outputs, accel_data=accel_data, parent=self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            t_new = data['type']
            line_new = data['line']
            new_name = data['name']
            outputs_new = data.get('outputs', [])
            if (new_name != name) and (new_name in self.accel_definitions):
                idx = 2
                tmp_name = new_name + f"_{idx}"
                while tmp_name in self.accel_definitions:
                    idx += 1
                    tmp_name = new_name + f"_{idx}"
                new_name = tmp_name
            del self.accel_definitions[name]
            self.accel_definitions[new_name] = {
                'type': t_new,
                'line': line_new,
                'outputs': outputs_new
            }
            item.setText(new_name)

    # ------------------------
    # 输出文件(PRINT)
    def add_output_file(self):
        available = self.get_all_outputs_for_print()
        fname = self.output_controller.add_output_file(available, parent_widget=self)
        if fname:
            self.output_list.addItem(fname)

    def remove_output_file(self):
        item = self.output_list.currentItem()
        if not item:
            QtWidgets.QMessageBox.warning(self, "警告","请先选择一个输出文件")
            return
        file_name = item.text()
        self.output_controller.remove_output_file(file_name)
        self.output_list.takeItem(self.output_list.row(item))

    def edit_output_file(self, item):
        file_name = item.text()
        available = self.get_all_outputs_for_print()
        new_fname = self.output_controller.edit_output_file(file_name, self, available)
        if new_fname and new_fname != file_name:
            item.setText(new_fname)

    # ------------------------
    # 生成文件
    def generate_file(self):
        try:
            def_lines = []
            # 群组
            for name, g in self.group_definitions.items():
                line = f"{name}: {g['type']} {g['params']}"
                def_lines.append(line)

            # CV
            for name, cv_data in self.cv_definitions.items():
                def_lines.append(cv_data['line'])

            acc_lines = []
            restart_line = get_restart_line(self.restart_checkbox.isChecked())
            if restart_line:
                acc_lines.append(restart_line)
            acc_lines.extend(def_lines)

            # 加速采样
            for name, accel_data in self.accel_definitions.items():
                t = accel_data['type']
                line = accel_data['line']
                acc_lines.append(line)

            # 输出文件(PRINT)
            for fname, val in self.output_controller.output_definitions.items():
                out_line = val['line']
                acc_lines.append(out_line)

            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
            data_dir = os.path.abspath(data_dir)
            os.makedirs(data_dir, exist_ok=True)

            self.acc_path = os.path.join(data_dir, "acc.dat")
            write_plumed_file(self.acc_path, acc_lines)
            QtWidgets.QMessageBox.information(self, "完成", f"已生成 {self.acc_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"生成文件失败: {e}")

    def open_acc_dat_file(self):
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.acc_path = os.path.abspath(os.path.join(data_dir, "acc.dat"))
        if not os.path.isfile(self.acc_path):
            QtWidgets.QMessageBox.warning(self, "警告", f"文件 {self.acc_path} 不存在，请先生成数据。")
            return
        try:
            subprocess.call(["gio", "open", self.acc_path])
        except Exception:
            QtWidgets.QMessageBox.information(self, "提示", f"请在文件管理器中查看: {self.acc_path}")

    # ------------------------
    # 保存配置
    def save_config(self):
        """
        打开文件对话框，让用户选择保存路径，并保存当前配置。
        自动为文件添加.json后缀（如果用户未手动添加）。
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "保存配置文件",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options
        )
        if file_path:
            try:
                # 自动添加.json后缀（如果未手动添加）
                if not file_path.lower().endswith('.json'):
                    file_path += '.json'
                ConfigManager.save_config(file_path, self)
                QtWidgets.QMessageBox.information(self, "成功", f"配置已保存到 {file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "错误", f"保存配置失败: {e}")

    # ------------------------
    # 加载配置
    def load_config(self):
        """
        打开文件对话框，让用户选择配置文件，并加载配置。
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "加载配置文件",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options
        )
        if file_path:
            try:
                ConfigManager.load_config(file_path, self)
                QtWidgets.QMessageBox.information(self, "成功", f"配置已加载自 {file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "错误", f"加载配置失败: {e}")

    # ------------------------
    # 其它辅助
    def get_all_cv_outputs(self):
        outputs = []
        for cv_name, cv_data in self.cv_definitions.items():
            outputs.extend(cv_data['outputs'])
        return outputs

    def get_all_accel_outputs(self):
        acc_out = []
        for name, accel_data in self.accel_definitions.items():
            # 直接把accel_data里的 'outputs' 收集过来
            acc_out.extend(accel_data.get('outputs', []))
        return acc_out

    def get_all_outputs_for_print(self):
        return self.get_all_cv_outputs() + self.get_all_accel_outputs()

    def parse_cv_line(self, line):
        parts = line.split(':', 1)
        if len(parts) != 2:
            return {}
        name = parts[0].strip()
        rest = parts[1].strip().split()
        if not rest:
            return {}
        cmd = rest[0]
        params = ' '.join(rest[1:])
        return {'name': name, 'type': cmd, 'params': params}

    def is_group_referenced(self, group_name):
        for g in self.group_definitions.values():
            if g['type'] == "GROUP" and group_name in g['params']:
                return True
        return False

    def is_cv_referenced(self, cv_name):
        # TODO: Implement actual reference check if necessary
        # 目前假设没有引用
        return False

    def get_single_atom_labels(self):
        return [
            g['name']
            for g in self.group_definitions.values()
            if g['type'] in ["COM", "CENTER", "FIXEDATOM", "GHOST"]
        ]

    def get_group_labels(self):
        return list(self.group_definitions.keys())
