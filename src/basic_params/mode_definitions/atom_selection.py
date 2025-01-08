from PyQt5 import QtWidgets

class AtomSelectionWidget(QtWidgets.QWidget):
    """
    用于选择单个原子编号或“单原子群组”标签的组合框。
    注意：
        - 当组合框中选中 "Atom Index" 时，会启用 self.spin，让用户输入单个原子编号。
        - 当组合框中选中某个标签（由 `group_labels` 提供）时，认为该标签仅代表一个单原子群组，
          此时 spin 被禁用，只返回该标签作为选择结果。
        - 如果需要选择多原子组，请在外部逻辑中禁止此处或改用其他组件。本组件只支持“单个原子”
          或“仅包含单个原子的群组”。
    """
    def __init__(self, group_labels, parent=None):
        """
        :param group_labels: List[str], 仅含单原子群组的标签。若包含多原子组，则不应在此处使用。
        :param parent: 父级控件
        """
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)

        self.combo = QtWidgets.QComboBox()
        # 第0项用于单原子编号
        self.combo.addItem("Atom Index")
        # 其余项均视作“单原子群组”的标签
        self.combo.addItems(group_labels)

        # 用于输入/显示单个原子编号
        self.spin = QtWidgets.QSpinBox()
        self.spin.setRange(1, 999999)
        self.spin.setValue(1)
        self.spin.setEnabled(True)

        self.combo.currentIndexChanged.connect(self.on_combo_changed)

        layout.addWidget(self.combo)
        layout.addWidget(self.spin)

    def on_combo_changed(self, index):
        """
        当组合框切换时：
          - index=0 表示 "Atom Index" 模式，启用 spin 让用户输编号
          - 否则为单原子群组标签，禁用 spin
        """
        if index == 0:
            self.spin.setEnabled(True)
        else:
            self.spin.setEnabled(False)

    def get_selection(self):
        """
        返回用户的选择：
          - 若当前选中 "Atom Index"，则返回 spin.value()（字符串形式）
          - 若当前选中某个标签，则直接返回该标签字符串
        """
        index = self.combo.currentIndex()
        if index == 0:
            # 用户选择的是单个编号
            return str(self.spin.value())
        else:
            # 用户选择的是单原子群组标签
            return self.combo.currentText()

    def set_selection(self, selection):
        """
        根据传入的 selection 设置组件状态：
          - 若 selection 是纯数字，则视为原子编号
          - 否则在组合框中查找对应的标签。
            如未找到，则回退到 "Atom Index" 并设置编号为1
        """
        if selection.isdigit():
            self.combo.setCurrentIndex(0)
            self.spin.setValue(int(selection))
        else:
            idx = self.combo.findText(selection)
            if idx != -1:
                self.combo.setCurrentIndex(idx)
            else:
                # 若未能找到对应标签，回退到原子编号模式
                self.combo.setCurrentIndex(0)
                self.spin.setValue(1)
