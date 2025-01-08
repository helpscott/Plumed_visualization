# src/basic_params/config_manager.py

import json
from typing import Dict, Any
from PyQt5 import QtWidgets


class ConfigManager:
    @staticmethod
    def save_config(file_path: str, basic_params_widget) -> None:
        """
        将当前的配置保存到指定的文件路径。

        参数:
            file_path (str): 配置文件的保存路径。
            basic_params_widget (BasicParamsWidget): 当前的基本参数窗口部件。
        """
        config = {
            'group_definitions': basic_params_widget.group_definitions,
            'cv_definitions': basic_params_widget.cv_definitions,
            'accel_definitions': basic_params_widget.accel_definitions,
            'output_definitions': basic_params_widget.output_controller.output_definitions,
            'restart_option': basic_params_widget.restart_checkbox.isChecked(),
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_config(file_path: str, basic_params_widget) -> None:
        """
        从指定的文件路径加载配置，并恢复到当前的基本参数窗口部件。

        参数:
            file_path (str): 配置文件的路径。
            basic_params_widget (BasicParamsWidget): 当前的基本参数窗口部件。
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 清空现有的定义
        basic_params_widget.group_definitions.clear()
        basic_params_widget.cv_definitions.clear()
        basic_params_widget.accel_definitions.clear()
        basic_params_widget.output_controller.output_definitions.clear()

        # 清空UI列表
        basic_params_widget.group_list.clear()
        basic_params_widget.cv_list.clear()
        basic_params_widget.accel_list.clear()
        basic_params_widget.output_list.clear()

        # 加载群组定义
        for group_name, group_data in config.get('group_definitions', {}).items():
            basic_params_widget.group_definitions[group_name] = group_data
            basic_params_widget.group_list.addItem(group_name)

        # 加载CV定义
        for cv_name, cv_data in config.get('cv_definitions', {}).items():
            basic_params_widget.cv_definitions[cv_name] = cv_data
            basic_params_widget.cv_list.addItem(cv_name)

        # 加载加速采样方法定义
        for accel_name, accel_data in config.get('accel_definitions', {}).items():
            basic_params_widget.accel_definitions[accel_name] = accel_data
            basic_params_widget.accel_list.addItem(accel_name)

        # 加载输出文件定义
        for file_name, file_data in config.get('output_definitions', {}).items():
            basic_params_widget.output_controller.output_definitions[file_name] = file_data
            basic_params_widget.output_list.addItem(file_name)

        # 加载RESTART选项
        restart = config.get('restart_option', False)
        basic_params_widget.restart_checkbox.setChecked(restart)
