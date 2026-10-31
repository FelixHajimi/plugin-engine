from PySide6 import QtWidgets, QtCore


class API:
    def __init__(self, pluginId: str): ...
    def readFile(self, id: str, encoding: str = "utf-8"): ...


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.api: API

    def initUI(self):
        self.setStyleSheet("""
QLabel[type=title] {
    font-size: 24px;
    font-weight: bold;
    color: #222222;
}

QLabel[type=text] {
    font-size: 14px;
    color: #666666;
}
""")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        title = QtWidgets.QLabel("Example Plugin")
        title.setProperty("type", "title")
        layout.addWidget(title)

        desc = QtWidgets.QLabel("This is a plugin page for testing.")
        desc.setProperty("type", "text")
        layout.addWidget(desc)

        layout.addStretch()

    @QtCore.Slot(dict)
    def onReceive(self, data: dict):
        pass
