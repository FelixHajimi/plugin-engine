from PySide6 import QtWidgets, QtCore
import typing


class API:
    def showMessage(
        self,
        text: str,
        level: int = 0,
        duration: int = 3000,
        clickedFunc: typing.Callable | None = None,
        customWidget: QtWidgets.QWidget | None = None,
    ): ...


class Translation:
    def exec(self, key: str, fallback: str = "") -> typing.Any: ...


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.api: API
        self.tran: Translation

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        title = QtWidgets.QLabel(self.tran.exec("title", "Example Plugin"))
        title.setProperty("class", "text")
        title.setProperty("type", "title")
        layout.addWidget(title)

        desc = QtWidgets.QLabel(self.tran.exec("desc", "This is a plugin page for testing."))
        desc.setProperty("class", "text")
        desc.setProperty("type", "body")
        layout.addWidget(desc)

        toastButton = QtWidgets.QPushButton(self.tran.exec("toast", "Show a message"))
        toastButton.setProperty("class", "button")
        toastButton.setProperty("type", "primary")
        toastButton.clicked.connect(
            lambda: self.api.showMessage(self.tran.exec("toastText", "Hello from example"))
        )
        layout.addWidget(toastButton)

        layout.addStretch()

    @QtCore.Slot(dict)
    def onReceive(self, data: dict):
        content = data.get("content")
        if data["type"] == "methods":
            self.tran = content["translation"]
        elif data["type"] == "initUI":
            self.initUI()
