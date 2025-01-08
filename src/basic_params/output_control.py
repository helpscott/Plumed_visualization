"""
output_control.py
负责输出文件(PRINT)的控制逻辑
"""
from PyQt5 import QtWidgets
from .output_definitions.output_definition_dialog import OutputDefinitionDialog

class OutputFileController:
    """
    简易的工具类或dialog也可。
    这里用一个controller示例，仅保留对外的方法。
    """

    def __init__(self):
        # 存储输出定义: {file_name: {'data':..., 'line':...}, ...}
        self.output_definitions = {}

    def add_output_file(self, available_outputs, parent_widget):
        dialog = OutputDefinitionDialog(available_outputs=available_outputs, parent=parent_widget)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            out_data = dialog.get_data()
            line = dialog.get_line()
            if not line:
                return None
            file_name = out_data['file']
            if file_name in self.output_definitions:
                idx = 2
                tmp_name = file_name + f"_{idx}"
                while tmp_name in self.output_definitions:
                    idx += 1
                    tmp_name = file_name + f"_{idx}"
                file_name = tmp_name
            self.output_definitions[file_name] = {
                'data': out_data,
                'line': line
            }
            return file_name
        return None

    def remove_output_file(self, file_name):
        if file_name in self.output_definitions:
            del self.output_definitions[file_name]

    def edit_output_file(self, file_name, parent_widget, available_outputs):
        existing = self.output_definitions.get(file_name, {})
        if not existing:
            return None
        out_data = existing.get('data', {})
        dialog = OutputDefinitionDialog(available_outputs=available_outputs, output_data=out_data, parent=parent_widget)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_data = dialog.get_data()
            new_line = dialog.get_line()
            if not new_line:
                return None
            new_file_name = new_data['file']
            if not new_file_name:
                new_file_name = file_name
            if new_file_name != file_name and new_file_name in self.output_definitions:
                idx = 2
                tmp_name = new_file_name + f"_{idx}"
                while tmp_name in self.output_definitions:
                    idx += 1
                    tmp_name = new_file_name + f"_{idx}"
                new_file_name = tmp_name
            del self.output_definitions[file_name]
            self.output_definitions[new_file_name] = {
                'data': new_data,
                'line': new_line
            }
            return new_file_name
        return None
