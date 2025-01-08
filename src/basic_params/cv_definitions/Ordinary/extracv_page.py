from PyQt5 import QtWidgets, QtCore

class ExtraCVPage(QtWidgets.QWidget):
    """
    用于定义EXTRACV类型的CV。
    只有一个参数: NAME=xxxx (来自MD engine的CV名称)
    自身在plumed配置中写作:
      mycv: EXTRACV NAME=xxxxx
    其中mycv是CV的label（在CVDefinitionDialog中填写），
    NAME=xxxx是外部输入的MD engine的CV名称。
    """

    def __init__(self, group_labels, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.prompt_label = QtWidgets.QLabel("使用外部MD引擎预先计算的CV (EXTRACV)")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.prompt_label)

        form = QtWidgets.QFormLayout()
        self.name_line = QtWidgets.QLineEdit()
        self.name_line.setPlaceholderText("在MD引擎中定义的CV名称，例如lambda")
        form.addRow("NAME=", self.name_line)

        self.layout.addLayout(form)

        # EXTRACV 没有其他高级参数，故不设置高级参数选项
        # 默认输出只有 CV 的 label 本身（没有.x等）

        self.cv_name = ""  # 用于存储plumed中此CV的label名字

    def set_cv_name(self, name):
        """
        由CVDefinitionDialog保存后显式调用。
        例如: name='l' => l: EXTRACV NAME=xxxx
        """
        self.cv_name = name.strip()

    def get_definition_line(self):
        """
        返回 'NAME=xxx' 部分.
        """
        engine_name = self.name_line.text().strip()
        if not engine_name:
            QtWidgets.QMessageBox.warning(self, "警告", "请填写MD引擎中的CV名称 (NAME=xxx)！")
            return None

        return f"NAME={engine_name}"

    def populate_data(self, cv_data):
        """
        根据已有cv_data进行UI回填。
        cv_data 是 { 'name':..., 'type': 'EXTRACV', 'params':... }
        params 可能包含 'NAME=xxx'
        """
        self.cv_name = cv_data.get('name', '')
        params = cv_data.get('params', '')
        tokens = params.split()

        # 只有1个关键参数: NAME=xxxx
        name_val = ""
        for tk in tokens:
            if tk.startswith("NAME="):
                name_val = tk[len("NAME="):]

        if name_val:
            self.name_line.setText(name_val)

    def get_cv_output(self):
        """
        EXTRACV 默认输出就一个: [cv_name]，没有其他.x 或 .y 等。
        """
        if not self.cv_name:
            return []
        return [self.cv_name]
