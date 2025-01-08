"""
group_angle_page.py

实现 GROUP_ANGLE 的界面逻辑。
用途：计算一组角；需要四个原子组（ATOMI, ATOMJ, ATOMK, ATOML），
并可选关键字 MEAN、MOMENT2。

最终输出形如：
[可选行] LOAD FILE=GroupAngle.cpp
GROUP_ANGLE ...
 LABEL=xxx
 ATOMI=...
 ATOMJ=...
 ATOMK=...
 ATOML=...
 [可选] MEAN
 [可选] MOMENT2
... GROUP_ANGLE
"""

from PyQt5 import QtWidgets, QtCore

class GroupAnglePage(QtWidgets.QWidget):
    """
    界面：
      - 提示说明
      - 4个下拉框：ATOMI, ATOMJ, ATOMK, ATOML (从 group_labels 里选)
      - 2个关键字复选框：MEAN(计算该组角的平均值)、MOMENT2(计算该组角的方差)
      - 无高级参数

    生成的指令行可在 get_definition_line() 中返回。
    """

    # 类级别标记，用于在写入acc.dat时确保 LOAD FILE=GroupAngle.cpp 只出现一次
    load_inserted = False

    def __init__(self, group_labels, parent=None):
        super().__init__(parent)
        self.group_labels = group_labels

        # 用于存储上层传入的CV名称(来自父对话框中的self.name_edit)
        self.cv_label_name = ""

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # 提示
        prompt_label = QtWidgets.QLabel(
            "计算一组角。注意，四个原子组的输入应为同等大小的原子组。"
        )
        prompt_label.setWordWrap(True)
        prompt_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(prompt_label)

        form = QtWidgets.QFormLayout()

        # ATOMI
        self.atomi_combo = QtWidgets.QComboBox()
        self.atomi_combo.addItems(self.group_labels)
        form.addRow("Vector1 - Atom1 (ATOMI):", self.atomi_combo)

        # ATOMJ
        self.atomj_combo = QtWidgets.QComboBox()
        self.atomj_combo.addItems(self.group_labels)
        form.addRow("Vector1 - Atom2 (ATOMJ):", self.atomj_combo)

        # ATOMK
        self.atomk_combo = QtWidgets.QComboBox()
        self.atomk_combo.addItems(self.group_labels)
        form.addRow("Vector2 - Atom1 (ATOMK):", self.atomk_combo)

        # ATOML
        self.atoml_combo = QtWidgets.QComboBox()
        self.atoml_combo.addItems(self.group_labels)
        form.addRow("Vector2 - Atom2 (ATOML):", self.atoml_combo)

        layout.addLayout(form)

        # 关键字可选复选框：MEAN / MOMENT2
        keyword_box = QtWidgets.QGroupBox("可选关键字")
        kw_layout = QtWidgets.QVBoxLayout(keyword_box)

        self.mean_cb = QtWidgets.QCheckBox("MEAN")
        self.mean_cb.setToolTip("计算该组角的平均值")
        kw_layout.addWidget(self.mean_cb)

        self.moment2_cb = QtWidgets.QCheckBox("MOMENT2")
        self.moment2_cb.setToolTip("计算该组角的方差")
        kw_layout.addWidget(self.moment2_cb)

        layout.addWidget(keyword_box)

        layout.addStretch()

    def set_cv_name(self, label_name):
        """
        由 CVDefinitionDialog 调用，将在对话框中填写的self.name_edit内容传进来。
        """
        self.cv_label_name = label_name.strip()

    def get_definition_line(self):
        """
        返回形如：
          LOAD FILE=GroupAngle.cpp   (若尚未添加过)
          GROUP_ANGLE ...
           LABEL=xxx
           ATOMI=...
           ATOMJ=...
           ATOMK=...
           ATOML=...
           [可选 MEAN]
           [可选 MOMENT2]
          ... GROUP_ANGLE
        """
        # 若未填写名称
        if not self.cv_label_name:
            QtWidgets.QMessageBox.warning(
                self, "警告", "请先在上层对话框中填写一个名称(label)！"
            )
            return None

        # 收集4个atom group
        i_val = self.atomi_combo.currentText().strip()
        j_val = self.atomj_combo.currentText().strip()
        k_val = self.atomk_combo.currentText().strip()
        l_val = self.atoml_combo.currentText().strip()
        if (not i_val) or (not j_val) or (not k_val) or (not l_val):
            QtWidgets.QMessageBox.warning(
                self, "警告", "请先选择4个原子组(ATOMI,ATOMJ,ATOMK,ATOML)！"
            )
            return None

        lines = []
        # 如果还未插入过LOAD FILE=GroupAngle.cpp，则添加
        if not GroupAnglePage.load_inserted:
            lines.append("LOAD FILE=GroupAngle.cpp")
            GroupAnglePage.load_inserted = True

        lines.append("GROUP_ANGLE ...")

        # LABEL=xxx
        lines.append(f" LABEL={self.cv_label_name}")

        # ATOMI/ATOMJ/ATOMK/ATOML
        lines.append(f" ATOMI={i_val}")
        lines.append(f" ATOMJ={j_val}")
        lines.append(f" ATOMK={k_val}")
        lines.append(f" ATOML={l_val}")

        # 关键字
        if self.mean_cb.isChecked():
            lines.append(" MEAN")
        if self.moment2_cb.isChecked():
            lines.append(" MOMENT2")

        lines.append("... GROUP_ANGLE")

        # 将多行合并为一个字符串
        return "\n".join(lines)

    def populate_data(self, cv_data):
        """
        当编辑已有CV时（如果需要），将已保存的参数回显到UI。
        目前此示例仅做占位。可根据需求解析cv_data['params']填回UI。
        """
        # 如果需要实现回显逻辑，请在此处解析cv_data
        pass

    def get_cv_output(self):
        """
        假设该CV只有自己名字 -> [self.cv_label_name]
        """
        if not self.cv_label_name:
            return []
        return [self.cv_label_name]
