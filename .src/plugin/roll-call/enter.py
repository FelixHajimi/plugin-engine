from PySide6 import QtWidgets, QtCore, QtGui
import random


class API:
    pluginId: str

    def __init__(self, pluginId: str): ...
    def readFile(self, id: str, encoding: str = "utf-8"): ...


class Translation:
    languageMap: dict[str, dict[str, str]]
    language: str

    def __init__(self, languageMap: dict[str, dict[str, str]], language: str): ...
    def exec(self, key: str, fallback: str = "") -> str: ...


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.api: API

        self.tran: Translation
        self.language: str
        self.languageMap: dict[str, dict[str, str]]

    def initUI(self):
        self.setStyleSheet("""
QLabel {
    font-size: 14px;
    color: #333;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 6px;
}
QListWidget {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding:4px;
    background: #ffffff;
}
QListWidget::item {
    padding:4px;
}
QPushButton {
    border: none;
    background-color: #e5e7eb;
    color: #1f2937;
    border-radius: 6px;
    font-size:14px;
}
QPushButton:hover {
    background-color: #d1d5db;
}
QPushButton:pressed {
    background-color: #9ca3af;
}
QPushButton:disabled {
    background-color: #f3f4f6;
    color:#9ca3af;
}
""")

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setSpacing(2)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        # Wait List
        waitList = QtWidgets.QListWidget()
        mainLayout.addWidget(waitList, 0, 0, 1, 2)

        # Called List
        calledList = QtWidgets.QListWidget()
        mainLayout.addWidget(calledList, 1, 0, 1, 2)

        # Message Label
        messageLabel = QtWidgets.QLabel()
        messageLabel.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        messageLabel.setStyleSheet("font-size: 36px;")
        messageLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        messageLabel.setText("-")
        mainLayout.addWidget(messageLabel, 0, 2, 2, 2)

        # Bottom Buttons
        policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        mainLayout.setRowMinimumHeight(3, 50)

        self.importButton = QtWidgets.QPushButton()
        self.importButton.setText(self.tran.exec("button.importList"))
        self.importButton.setSizePolicy(policy)

        def importButtonFunc():
            studentList = self.api.readFile("studentList")
            if studentList is None:
                return
            waitList.clear()
            calledList.clear()
            waitList.addItems([item["name"] for item in studentList])

        importButtonFunc()

        self.importButton.clicked.connect(importButtonFunc)
        mainLayout.addWidget(self.importButton, 3, 0, 1, 1)

        self.resetButton = QtWidgets.QPushButton()
        self.resetButton.setText(self.tran.exec("button.reset"))
        self.resetButton.setSizePolicy(policy)

        def resetButtonFunc():
            waitList.clear()
            calledList.clear()

        self.resetButton.clicked.connect(resetButtonFunc)
        mainLayout.addWidget(self.resetButton, 3, 1, 1, 1)

        self.randomPickButton = QtWidgets.QPushButton()
        self.randomPickButton.setText(self.tran.exec("button.randomPick"))
        self.randomPickButton.setSizePolicy(policy)

        def randomPickButtonFunc():
            studentList = [
                item.text()
                for i in range(waitList.count())
                if (item := waitList.item(i))
            ]
            if studentList:
                name = random.choice(studentList)
                messageLabel.setText(name)
                waitList.takeItem(studentList.index(name))
                calledList.addItem(name)
            else:
                messageLabel.setText("-")

        self.randomPickButton.clicked.connect(randomPickButtonFunc)
        mainLayout.addWidget(self.randomPickButton, 3, 2, 1, 1)

        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setText(self.tran.exec("button.cancel"))
        self.cancelButton.setSizePolicy(policy)

        def cancelButtonFunc():
            if calledList.currentItem() is None:
                messageLabel.setText("-")
                return
            name = calledList.currentItem().text()
            calledList.takeItem(calledList.currentIndex().row())
            waitList.addItem(name)

        self.cancelButton.clicked.connect(cancelButtonFunc)
        mainLayout.addWidget(self.cancelButton, 3, 3, 1, 1)

        self.setLayout(mainLayout)

    def updateUI(self):
        self.importButton.setText(self.tran.exec("button.importList"))
        self.resetButton.setText(self.tran.exec("button.reset"))
        self.randomPickButton.setText(self.tran.exec("button.randomPick"))
        self.cancelButton.setText(self.tran.exec("button.cancel"))

    @QtCore.Slot(dict)
    def onReceive(self, data: dict):
        content = data.get("content")
        if data["type"] == "setting":
            self.language = content["general.language"]["value"]
        elif data["type"] == "languageMap":
            self.languageMap = content
        elif data["type"] == "methods":
            self.tran = content["translation"](self.languageMap, self.language)
        elif data["type"] == "initUI":
            self.initUI()
        elif data["type"] == "updateUI":
            self.updateUI()
