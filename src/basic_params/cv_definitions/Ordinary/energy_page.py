from PyQt5 import QtWidgets, QtCore

class EnergyPage(QtWidgets.QWidget):
    """
    用于定义ENERGY类型的CV。
    ENERGY没有任何可设置的参数，也没有高级选项。
    只需在Plumed配置中写:
      mycv: ENERGY
    其中mycv是CV的label。
    输出也只有 mycv(本身) 这一项。
    """

    def __init__(self, group_labels, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("计算系统的总势能 (ENERGY)")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.prompt_label)

        # ENERGY没有可选参数，也没有高级选项
        self.cv_name = ""  # 用于存储Plumed中此CV的label名字

    def set_cv_name(self, name):
        """
        在CVDefinitionDialog保存后显式调用。
        例如: name='ene' => ene: ENERGY
        """
        self.cv_name = name.strip()

    def get_definition_line(self):
        """
        由于ENERGY无任何参数, 只返回空字符串作为params。
        """
        # 直接返回空即可
        return ""

    def populate_data(self, cv_data):
        """
        ENERGY无参数，无需解析；只记录cv_name。
        """
        self.cv_name = cv_data.get('name', '')

    def get_cv_output(self):
        """
        ENERGY默认输出只有 [cv_name]。
        """
        if not self.cv_name:
            return []
        return [self.cv_name]
