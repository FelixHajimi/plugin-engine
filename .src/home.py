from PySide6 import QtWidgets


class Home(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        title = QtWidgets.QLabel("Home")
        title.setProperty("type", "title")
        layout.addWidget(title)

        desc = QtWidgets.QLabel("Welcome to use.\nSelect the left menu to start the operation.")
        desc.setProperty("type", "text")
        layout.addWidget(desc)

        layout.addStretch()
