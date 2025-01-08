def select_file_dialog(parent, title, filter_str):
    from PyQt5 import QtWidgets
    file_name, _ = QtWidgets.QFileDialog.getOpenFileName(parent, title, "", filter_str)
    return file_name
