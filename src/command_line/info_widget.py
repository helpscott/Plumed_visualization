# info_widget.py

from PyQt5 import QtWidgets, QtCore

class InfoWidget(QtWidgets.QWidget):
    """
    info 工具界面：
      - 此工具可获取plumed版本相关信息
      - 提供若干布尔型命令行参数:
         --configuration
         --root
         --user-doc
         --developer-doc
         --version
         --long-version
         --git-version
         --include-dir
         --soext
      当用户勾选/取消勾选时，发出 params_changed 信号，以便上层刷新命令行。
    """
    params_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # 最顶部的说明
        desc_label = QtWidgets.QLabel("一个可获取当前 plumed 版本信息的工具")
        desc_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(desc_label)

        # 布尔选项组
        grid = QtWidgets.QFormLayout()

        self.configuration_cb = QtWidgets.QCheckBox("--configuration")
        self.configuration_cb.setToolTip("打印配置文件信息")
        grid.addRow(self.configuration_cb)

        self.root_cb = QtWidgets.QCheckBox("--root")
        self.root_cb.setToolTip("打印plumed源码根目录位置")
        grid.addRow(self.root_cb)

        self.userdoc_cb = QtWidgets.QCheckBox("--user-doc")
        self.userdoc_cb.setToolTip("打印用户手册(HTML)的位置")
        grid.addRow(self.userdoc_cb)

        self.developerdoc_cb = QtWidgets.QCheckBox("--developer-doc")
        self.developerdoc_cb.setToolTip("打印开发者文档(HTML)的位置")
        grid.addRow(self.developerdoc_cb)

        self.version_cb = QtWidgets.QCheckBox("--version")
        self.version_cb.setToolTip("打印plumed版本号")
        grid.addRow(self.version_cb)

        self.longversion_cb = QtWidgets.QCheckBox("--long-version")
        self.longversion_cb.setToolTip("打印完整版本号(long version)")
        grid.addRow(self.longversion_cb)

        self.gitversion_cb = QtWidgets.QCheckBox("--git-version")
        self.gitversion_cb.setToolTip("打印git版本号(若有)")
        grid.addRow(self.gitversion_cb)

        self.includedir_cb = QtWidgets.QCheckBox("--include-dir")
        self.includedir_cb.setToolTip("打印plumed的include目录位置")
        grid.addRow(self.includedir_cb)

        self.soext_cb = QtWidgets.QCheckBox("--soext")
        self.soext_cb.setToolTip("打印共享库文件后缀(so/dylib)")
        grid.addRow(self.soext_cb)

        layout.addLayout(grid)

        # 监听checkbox state变化
        all_cbs = [
            self.configuration_cb, self.root_cb, self.userdoc_cb, self.developerdoc_cb,
            self.version_cb, self.longversion_cb, self.gitversion_cb,
            self.includedir_cb, self.soext_cb
        ]
        for cb in all_cbs:
            cb.stateChanged.connect(self.params_changed.emit)

        self.setLayout(layout)

    def get_command_flags(self):
        """
        返回 info 的list_of_flags, 不包含 "plumed info"
        """
        flags = []
        # 每个布尔选项如果被勾选，就添加到列表
        if self.configuration_cb.isChecked():
            flags.append("--configuration")
        if self.root_cb.isChecked():
            flags.append("--root")
        if self.userdoc_cb.isChecked():
            flags.append("--user-doc")
        if self.developerdoc_cb.isChecked():
            flags.append("--developer-doc")
        if self.version_cb.isChecked():
            flags.append("--version")
        if self.longversion_cb.isChecked():
            flags.append("--long-version")
        if self.gitversion_cb.isChecked():
            flags.append("--git-version")
        if self.includedir_cb.isChecked():
            flags.append("--include-dir")
        if self.soext_cb.isChecked():
            flags.append("--soext")

        return flags
