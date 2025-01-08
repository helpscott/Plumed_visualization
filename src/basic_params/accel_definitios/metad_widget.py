"""
metad_widget.py
此处原本包含 MetadCVItem，现在改为从 cv_output_selector.py 中导入
"""
from PyQt5 import QtWidgets, QtCore
# 新增：从 mode_definitions.cv_output_selector 导入 MetadCVItem
from ..mode_definitions.cv_output_selector import MetadCVItem

class MetadAdvancedDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("METAD高级参数")
        layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()

        # 1) TAU
        self.tau_checkbox = QtWidgets.QCheckBox("使用TAU")
        # 为 TAU 添加中文悬浮提示
        self.tau_checkbox.setToolTip(
            "TAU：在well-tempered metadynamics中，令 hill 高度 = ( kBΔT*pace*timestep ) / tau"
        )
        self.tau_spin = QtWidgets.QDoubleSpinBox()
        self.tau_spin.setRange(0.0,999999.0)
        self.tau_spin.setDecimals(3)
        self.tau_spin.setValue(0.0)
        tau_h = QtWidgets.QHBoxLayout()
        tau_h.addWidget(self.tau_checkbox)
        tau_h.addWidget(self.tau_spin)
        form_layout.addRow("TAU:", tau_h)

        # 2) DAMPFACTOR
        self.dampfactor_checkbox = QtWidgets.QCheckBox("使用DAMPFACTOR")
        # 为 DAMPFACTOR 添加中文悬浮提示
        self.dampfactor_checkbox.setToolTip(
            "DAMPFACTOR：阻尼因子，用于 hills 衰减。\n"
            "在元动力学计算中，以 exp(-max(V)/( kBT*DAMPFACTOR )) 形式衰减 hills"
        )
        self.dampfactor_spin = QtWidgets.QDoubleSpinBox()
        self.dampfactor_spin.setRange(0.0,999999.0)
        self.dampfactor_spin.setDecimals(3)
        self.dampfactor_spin.setValue(0.0)
        damp_h = QtWidgets.QHBoxLayout()
        damp_h.addWidget(self.dampfactor_checkbox)
        damp_h.addWidget(self.dampfactor_spin)
        form_layout.addRow("DAMPFACTOR:", damp_h)

        # 3) ADAPTIVE
        self.adaptive_checkbox = QtWidgets.QCheckBox("使用ADAPTIVE")
        # 为 ADAPTIVE 添加中文悬浮提示
        self.adaptive_checkbox.setToolTip(
            "ADAPTIVE：使用自适应的 hills 宽度方案，可选 GEOM 或 DIFF。\n"
            "  - GEOM：几何方式\n  - DIFF：扩散方式"
        )
        self.adaptive_combo = QtWidgets.QComboBox()
        self.adaptive_combo.addItems(["GEOM","DIFF"])
        adaptive_h = QtWidgets.QHBoxLayout()
        adaptive_h.addWidget(self.adaptive_checkbox)
        adaptive_h.addWidget(self.adaptive_combo)
        form_layout.addRow("ADAPTIVE:", adaptive_h)

        # 4) SIGMA_MAX/SIGMA_MIN
        self.sigmax_checkbox = QtWidgets.QCheckBox("使用SIGMA_MAX/SIGMA_MIN")
        # 为 SIGMA_MAX/MIN 做提示
        self.sigmax_checkbox.setToolTip(
            "SIGMA_MAX/SIGMA_MIN：指定自适应 hills 宽度的上下界。\n"
            "负数表示不设置此界。"
        )
        self.sigmax_line = QtWidgets.QLineEdit()
        self.sigmax_line.setPlaceholderText("例如：0.5,1.0")
        self.sigmin_line = QtWidgets.QLineEdit()
        self.sigmin_line.setPlaceholderText("例如：0.2,0.1")
        sig_h = QtWidgets.QHBoxLayout()
        sig_h.addWidget(self.sigmax_checkbox)
        sig_h.addWidget(QtWidgets.QLabel("SIGMA_MAX:"))
        sig_h.addWidget(self.sigmax_line)
        sig_h.addWidget(QtWidgets.QLabel("SIGMA_MIN:"))
        sig_h.addWidget(self.sigmin_line)
        form_layout.addRow("SIGMA_MAX/MIN:", sig_h)

        # 5) CALC_RCT
        self.calc_rct_checkbox = QtWidgets.QCheckBox("CALC_RCT")
        self.calc_rct_checkbox.setToolTip(
            "CALC_RCT (默认=off)：\n"
            "计算 c(t) 重加权因子，并使用它来获取归一化的偏置项 [rbias = bias - rct]\n"
            "此方法与非格点上的 metadynamics 不兼容。"
        )
        form_layout.addRow(self.calc_rct_checkbox)

        # 6) ACCELERATION
        self.acc_checkbox = QtWidgets.QCheckBox("ACCELERATION")
        self.acc_checkbox.setToolTip(
            "ACCELERATION (默认=off)：\n"
            "是否在 metadynamics 中计算加速采样因子"
        )
        form_layout.addRow(self.acc_checkbox)

        # 7) CALC_MAX_BIAS
        self.calc_max_bias_checkbox = QtWidgets.QCheckBox("CALC_MAX_BIAS")
        self.calc_max_bias_checkbox.setToolTip(
            "CALC_MAX_BIAS (默认=off)：\n"
            "若勾选，则计算 metadynamics V(s, t) 的最大值"
        )
        form_layout.addRow(self.calc_max_bias_checkbox)

        # 8) CALC_TRANSITION_BIAS
        self.calc_trans_bias_checkbox = QtWidgets.QCheckBox("CALC_TRANSITION_BIAS")
        self.calc_trans_bias_checkbox.setToolTip(
            "CALC_TRANSITION_BIAS (默认=off)：\n"
            "若勾选，则计算 metadynamics transition bias V*(t)"
        )
        form_layout.addRow(self.calc_trans_bias_checkbox)

        # 9) FREQUENCY_ADAPTIVE
        self.freq_adaptive_checkbox = QtWidgets.QCheckBox("FREQUENCY_ADAPTIVE")
        self.freq_adaptive_checkbox.setToolTip(
            "FREQUENCY_ADAPTIVE (默认=off)：\n"
            "若勾选，则启用频率自适应的 metadynamics，使 hill 添加频率\n"
            "随着加速因子而动态调整"
        )
        form_layout.addRow(self.freq_adaptive_checkbox)

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

        self.setLayout(layout)

    def get_data(self):
        data = {}
        if self.tau_checkbox.isChecked():
            data['TAU'] = self.tau_spin.value()
        if self.dampfactor_checkbox.isChecked():
            data['DAMPFACTOR'] = self.dampfactor_spin.value()
        if self.adaptive_checkbox.isChecked():
            data['ADAPTIVE'] = self.adaptive_combo.currentText()
            if self.sigmax_checkbox.isChecked():
                sigmax_list = [x.strip() for x in self.sigmax_line.text().split(',') if x.strip()!=""]
                sigmin_list = [x.strip() for x in self.sigmin_line.text().split(',') if x.strip()!=""]
                if len(sigmax_list)>0:
                    data['SIGMA_MAX'] = sigmax_list
                if len(sigmin_list)>0:
                    data['SIGMA_MIN'] = sigmin_list
        if self.calc_rct_checkbox.isChecked():
            data['CALC_RCT'] = True
        if self.acc_checkbox.isChecked():
            data['ACCELERATION'] = True
        if self.calc_max_bias_checkbox.isChecked():
            data['CALC_MAX_BIAS'] = True
        if self.calc_trans_bias_checkbox.isChecked():
            data['CALC_TRANSITION_BIAS'] = True
        if self.freq_adaptive_checkbox.isChecked():
            data['FREQUENCY_ADAPTIVE'] = True
        return data

    def populate_data(self, data):
        if 'TAU' in data:
            self.tau_checkbox.setChecked(True)
            self.tau_spin.setValue(data['TAU'])
        if 'DAMPFACTOR' in data:
            self.dampfactor_checkbox.setChecked(True)
            self.dampfactor_spin.setValue(data['DAMPFACTOR'])
        if 'ADAPTIVE' in data:
            self.adaptive_checkbox.setChecked(True)
            idx = self.adaptive_combo.findText(data['ADAPTIVE'])
            if idx>=0:
                self.adaptive_combo.setCurrentIndex(idx)
            if 'SIGMA_MAX' in data or 'SIGMA_MIN' in data:
                self.sigmax_checkbox.setChecked(True)
                if 'SIGMA_MAX' in data:
                    self.sigmax_line.setText(','.join(data['SIGMA_MAX']))
                if 'SIGMA_MIN' in data:
                    self.sigmin_line.setText(','.join(data['SIGMA_MIN']))
        if 'CALC_RCT' in data:
            self.calc_rct_checkbox.setChecked(True)
        if 'ACCELERATION' in data:
            self.acc_checkbox.setChecked(True)
        if 'CALC_MAX_BIAS' in data:
            self.calc_max_bias_checkbox.setChecked(True)
        if 'CALC_TRANSITION_BIAS' in data:
            self.calc_trans_bias_checkbox.setChecked(True)
        if 'FREQUENCY_ADAPTIVE' in data:
            self.freq_adaptive_checkbox.setChecked(True)


class MetadWidget(QtWidgets.QWidget):
    """
    新增一个FILE=的全局参数，默认值HILLS
    并将对 CV 输出属性的管理拆分到 mode_definitions.cv_output_selector
    """
    def __init__(self, cv_outputs, parent=None):
        super().__init__(parent)
        self.cv_outputs = cv_outputs
        self.cv_items = []
        self.method_name = "metad_1"
        layout = QtWidgets.QVBoxLayout(self)

        # ------------ METAD 基础参数组 ------------
        base_group = QtWidgets.QGroupBox("METAD 基础参数")
        base_layout = QtWidgets.QFormLayout(base_group)

        # 1) BIASFACTOR
        self.label_biasfactor = QtWidgets.QLabel("BIASFACTOR:")
        self.label_biasfactor.setToolTip(
            "use well-tempered metadynamics and use this bias factor.\n"
            "请注意，你还需要设置 temp（温度）。"
        )
        self.biasfactor_spin = QtWidgets.QDoubleSpinBox()
        self.biasfactor_spin.setRange(0.0,999999.0)
        self.biasfactor_spin.setValue(5.0)
        base_layout.addRow(self.label_biasfactor, self.biasfactor_spin)

        # 2) TEMP
        self.label_temp = QtWidgets.QLabel("TEMP:")
        self.label_temp.setToolTip(
            "系统温度（元动力学中需要）。\n"
            "TEMP：以K为单位，仅当使用well-tempered时需要设置。"
        )
        self.temp_spin = QtWidgets.QDoubleSpinBox()
        self.temp_spin.setRange(0.0,999999.0)
        self.temp_spin.setValue(300.0)
        base_layout.addRow(self.label_temp, self.temp_spin)

        # 3) PACE
        self.label_pace = QtWidgets.QLabel("PACE:")
        self.label_pace.setToolTip(
            "向势能面中加入 hills 的频率（每多少步加一次）"
        )
        self.pace_spin = QtWidgets.QSpinBox()
        self.pace_spin.setRange(1,999999)
        self.pace_spin.setValue(2000)
        base_layout.addRow(self.label_pace, self.pace_spin)

        # 4) HEIGHT
        self.label_height = QtWidgets.QLabel("HEIGHT:")
        self.label_height.setToolTip(
            "高斯凸包 (hills) 的高度。\n"
            "若使用 TAU 和 (BIASFACTOR 或 DAMPFACTOR) 则可不设置本项"
        )
        self.height_spin = QtWidgets.QDoubleSpinBox()
        self.height_spin.setRange(0.0,999999.0)
        self.height_spin.setValue(10.0)
        base_layout.addRow(self.label_height, self.height_spin)

        # 5) FILE
        self.label_file = QtWidgets.QLabel("FILE:")
        self.label_file.setToolTip(
            "(默认=HILLS) 用于存储已添加 hills 的文件名"
        )
        self.file_line = QtWidgets.QLineEdit("HILLS")
        base_layout.addRow(self.label_file, self.file_line)

        layout.addWidget(base_group)

        # ------------ 选择CV ------------
        cv_group = QtWidgets.QGroupBox("选择CV (可添加多个)")
        cv_vlayout = QtWidgets.QVBoxLayout(cv_group)

        # 使用QScrollArea可以拖动，并为其设置较大的最小高度
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        cv_container = QtWidgets.QWidget()
        cv_container_layout = QtWidgets.QVBoxLayout(cv_container)
        cv_container_layout.setContentsMargins(0,0,0,0)
        self.cv_list_layout = cv_container_layout
        scroll.setWidget(cv_container)

        # 设置较大的最小高度让用户有更多空间
        scroll.setMinimumHeight(400)
        scroll.setMinimumWidth(350)

        cv_vlayout.addWidget(scroll)
        self.add_cv_btn = QtWidgets.QPushButton("增加CV")
        self.add_cv_btn.clicked.connect(self.add_cv_item)
        cv_vlayout.addWidget(self.add_cv_btn)

        layout.addWidget(cv_group)

        # ------------ 高级设置按钮 ------------
        self.adv_btn = QtWidgets.QPushButton("高级设置")
        self.adv_btn.clicked.connect(self.open_advanced_settings)
        layout.addWidget(self.adv_btn)

        self.advanced_settings = None
        self.setLayout(layout)

    def set_accmet_name(self, name):
        if name.strip():
            self.method_name = name.strip()

    def add_cv_item(self):
        """
        原先创建 MetadCVItem( self.cv_outputs ) 由新的文件( cv_output_selector.py )中导入
        """
        from ..mode_definitions.cv_output_selector import MetadCVItem
        item = MetadCVItem(self.cv_outputs)
        item.remove_requested.connect(self.remove_cv_item)
        self.cv_items.append(item)
        self.cv_list_layout.addWidget(item)

    def remove_cv_item(self, item):
        self.cv_items.remove(item)
        self.cv_list_layout.removeWidget(item)
        item.deleteLater()

    def open_advanced_settings(self):
        dialog = MetadAdvancedDialog(self)
        if self.advanced_settings:
            dialog.populate_data(self.advanced_settings.get_data())
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.advanced_settings = dialog

    def get_definition_line(self):
        if not self.cv_items:
            QtWidgets.QMessageBox.warning(self, "警告", "请至少添加一个CV")
            return None

        params = {}
        params['BIASFACTOR'] = self.biasfactor_spin.value()
        params['TEMP'] = self.temp_spin.value()
        params['PACE'] = self.pace_spin.value()
        params['HEIGHT'] = self.height_spin.value()
        params['FILE'] = self.file_line.text().strip() if self.file_line.text().strip() else "HILLS"

        arg_list = []
        all_grid_min = []
        all_grid_max = []
        all_grid_bin = []
        all_sigma = []

        for cv_item in self.cv_items:
            d = cv_item.get_data()
            arg_list.append(d['ARG'])
            all_grid_min.append(d.get('GRID_MIN',""))
            all_grid_max.append(d.get('GRID_MAX',""))
            all_grid_bin.append(str(d['GRID_BIN']))
            all_sigma.append(str(d['SIGMA']))

        def all_filled(lst):
            return all(x.strip() != "" for x in lst)

        lines = []
        lines.append(f"{self.method_name}: METAD ...")

        base_line = f"   ARG={','.join(arg_list)}"
        base_line += f" BIASFACTOR={params['BIASFACTOR']} TEMP={params['TEMP']} PACE={params['PACE']} HEIGHT={params['HEIGHT']}"
        # 拼接FILE
        base_line += f" FILE={params['FILE']}"
        # 再拼接SIGMA
        sigma_str = ",".join(all_sigma)
        base_line += f" SIGMA={sigma_str}"
        lines.append(base_line)

        grid_line_parts = []
        if all_filled(all_grid_min):
            grid_line_parts.append("GRID_MIN="+",".join(all_grid_min))
        if all_filled(all_grid_max):
            grid_line_parts.append("GRID_MAX="+",".join(all_grid_max))
        if all_filled(all_grid_bin):
            grid_line_parts.append("GRID_BIN="+",".join(all_grid_bin))

        if grid_line_parts:
            lines.append("   " + " ".join(grid_line_parts))

        if self.advanced_settings:
            adv_data = self.advanced_settings.get_data()
            if adv_data.get('TAU') is not None:
                lines.append("   TAU="+str(adv_data['TAU']))
            if adv_data.get('DAMPFACTOR') is not None:
                lines.append("   DAMPFACTOR="+str(adv_data['DAMPFACTOR']))
            if adv_data.get('ADAPTIVE'):
                lines.append("   ADAPTIVE="+adv_data['ADAPTIVE'])
                if adv_data.get('SIGMA_MAX'):
                    lines.append("   SIGMA_MAX="+",".join(adv_data['SIGMA_MAX']))
                if adv_data.get('SIGMA_MIN'):
                    lines.append("   SIGMA_MIN="+",".join(adv_data['SIGMA_MIN']))
            if adv_data.get('CALC_RCT'):
                lines.append("   CALC_RCT")
            if adv_data.get('ACCELERATION'):
                lines.append("   ACCELERATION")
            if adv_data.get('CALC_MAX_BIAS'):
                lines.append("   CALC_MAX_BIAS")
            if adv_data.get('CALC_TRANSITION_BIAS'):
                lines.append("   CALC_TRANSITION_BIAS")
            if adv_data.get('FREQUENCY_ADAPTIVE'):
                lines.append("   FREQUENCY_ADAPTIVE")

        lines.append("...")
        return "\n".join(lines)

    def populate_data(self, params_str):
        lines = params_str.splitlines()
        if len(lines)<2:
            return

        main_params = {}
        adv_data = {}
        cv_args = []

        def parse_keyvals(l):
            parts = l.strip().split()
            res = {}
            for p in parts:
                if '=' in p:
                    k,v = p.split('=',1)
                    res[k.strip()] = v.strip()
                else:
                    res[p.strip()] = True
            return res

        first_line = lines[0].strip()
        if ':' in first_line:
            fl_parts = first_line.split(':',1)
            self.method_name = fl_parts[0].strip()

        i = 1
        while i < len(lines):
            l = lines[i].strip()
            if l == '...':
                break
            if l.startswith('ARG='):
                base_params = parse_keyvals(l)
                arg_str = base_params.get('ARG','')
                cv_args = arg_str.split(',') if arg_str else []
                main_params.update(base_params)
            elif l.startswith('GRID_MIN=') or l.startswith('GRID_MAX=') or l.startswith('GRID_BIN='):
                grid_params = parse_keyvals(l)
                main_params.update(grid_params)
            else:
                ad = parse_keyvals(l)
                adv_data.update(ad)
            i+=1

        self.biasfactor_spin.setValue(float(main_params.get('BIASFACTOR','5.0')))
        self.temp_spin.setValue(float(main_params.get('TEMP','300.0')))
        self.pace_spin.setValue(int(main_params.get('PACE','2000')))
        self.height_spin.setValue(float(main_params.get('HEIGHT','10.0')))

        # 读取 FILE
        file_val = main_params.get('FILE','HILLS')
        self.file_line.setText(file_val if file_val else "HILLS")

        sigma_list = main_params.get('SIGMA','0.2').split(',')
        grid_min_list = main_params.get('GRID_MIN','').split(',') if 'GRID_MIN' in main_params else []
        grid_max_list = main_params.get('GRID_MAX','').split(',') if 'GRID_MAX' in main_params else []
        grid_bin_list = main_params.get('GRID_BIN','').split(',') if 'GRID_BIN' in main_params else []

        cv_count = len(cv_args)

        def extend_list(lst, length, default=''):
            while len(lst)<length:
                lst.append(default)
            return lst

        sigma_list = extend_list(sigma_list, cv_count, '0.2')
        grid_bin_list = extend_list(grid_bin_list, cv_count, '100')
        grid_min_list = extend_list(grid_min_list, cv_count, '')
        grid_max_list = extend_list(grid_max_list, cv_count, '')

        # 清空已有CV项
        for it in self.cv_items[:]:
            self.remove_cv_item(it)

        # 重新创建CV项
        from ..mode_definitions.cv_output_selector import MetadCVItem
        for i in range(cv_count):
            item = MetadCVItem(self.cv_outputs)
            cv_data = {
                'ARG': cv_args[i],
                'SIGMA': sigma_list[i],
                'GRID_BIN': grid_bin_list[i]
            }
            if grid_min_list[i]:
                cv_data['GRID_MIN'] = grid_min_list[i]
            if grid_max_list[i]:
                cv_data['GRID_MAX'] = grid_max_list[i]
            item.populate_data(cv_data)
            self.cv_items.append(item)
            self.cv_list_layout.addWidget(item)

        if adv_data:
            out_data = {}
            if 'TAU' in adv_data:
                out_data['TAU'] = float(adv_data['TAU'])
            if 'DAMPFACTOR' in adv_data:
                out_data['DAMPFACTOR'] = float(adv_data['DAMPFACTOR'])
            if 'ADAPTIVE' in adv_data:
                out_data['ADAPTIVE'] = adv_data['ADAPTIVE']
            if 'SIGMA_MAX' in adv_data:
                val = adv_data['SIGMA_MAX']
                out_data['SIGMA_MAX'] = val.split(',') if isinstance(val,str) else val
            if 'SIGMA_MIN' in adv_data:
                val = adv_data['SIGMA_MIN']
                out_data['SIGMA_MIN'] = val.split(',') if isinstance(val,str) else val

            for k in ['CALC_RCT','ACCELERATION','CALC_MAX_BIAS','CALC_TRANSITION_BIAS','FREQUENCY_ADAPTIVE']:
                if k in adv_data and adv_data[k] is True:
                    out_data[k] = True

            adv_dlg = MetadAdvancedDialog(self)
            adv_dlg.populate_data(out_data)
            self.advanced_settings = adv_dlg
        else:
            self.advanced_settings = None

    # 新增：让 METAD 也能提供输出名
    def get_outputs(self):
        outputs = [f"{self.method_name}.bias"]  # 原本就返回这个
        if self.advanced_settings:
            adv_data = self.advanced_settings.get_data()
            extra_map = {
                'CALC_RCT': ['rbias', 'rct'],
                'ACCELERATION': ['acc'],
                'CALC_MAX_BIAS': ['maxbias'],
                'CALC_TRANSITION_BIAS': ['transbias'],
                'FREQUENCY_ADAPTIVE': ['pace']
            }
            for key, val in adv_data.items():
                if key in extra_map and val is True:
                    for q in extra_map[key]:
                        outputs.append(f"{self.method_name}.{q}")
        return outputs
