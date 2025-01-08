"""
addon.py

附加模块(AddonWidget)的占位示例。
暂不对具体功能进行实现，仅提供选择功能的UI结构示例。
"""

from PyQt5 import QtWidgets, QtCore


class PlaceholderPage(QtWidgets.QWidget):
    """
    用于在选择某一子功能后，显示占位说明的页面。
    """
    def __init__(self, info_text, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel(info_text)
        label.setWordWrap(True)
        layout.addWidget(label)

        layout.addStretch()


class AddonWidget(QtWidgets.QWidget):
    """
    此类展示一个附加模块的占位界面。
    顶部是一个功能选择下拉框，下方根据选择切换界面。
    目前仅做示例，不实现具体功能。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # 顶部提示和选择功能
        top_hlayout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("选择附加功能：")
        self.function_combo = QtWidgets.QComboBox()
        # 这里添加几项示例功能名称
        self.function_combo.addItems([
            "功能A(示例)",
            "功能B(示例)",
            "功能C(示例)"
        ])

        top_hlayout.addWidget(label)
        top_hlayout.addWidget(self.function_combo)
        main_layout.addLayout(top_hlayout)

        # 下方堆叠页面（或简单的占位容器）
        self.stack = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.stack)

        # 添加若干占位页面
        # Page A
        self.page_a = PlaceholderPage("这是功能A的占位说明，未真正实现。")
        self.stack.addWidget(self.page_a)

        # Page B
        self.page_b = PlaceholderPage("这是功能B的占位说明，未真正实现。")
        self.stack.addWidget(self.page_b)

        # Page C
        self.page_c = PlaceholderPage("这是功能C的占位说明，未真正实现。")
        self.stack.addWidget(self.page_c)

        # 连接信号：当下拉框选择改变时，切换到相应页面
        self.function_combo.currentIndexChanged.connect(self.switch_page)

        # 默认选中第 0 项
        self.stack.setCurrentIndex(0)

    def switch_page(self, index):
        """
        根据当前功能选择来切换QStackedWidget显示的页面
        """
        self.stack.setCurrentIndex(index)
