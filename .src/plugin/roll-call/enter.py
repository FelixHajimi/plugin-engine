from PySide6 import QtWidgets, QtCore, QtGui
import random


class API:
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

        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.setSpacing(2)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        # Wait List
        self.waitList = QtWidgets.QListWidget()
        self.mainLayout.addWidget(self.waitList, 0, 0, 1, 2)

        # Called List
        self.calledList = QtWidgets.QListWidget()
        self.mainLayout.addWidget(self.calledList, 1, 0, 1, 2)

        # Message Label
        self.messageLabel = QtWidgets.QLabel()
        self.messageLabel.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.messageLabel.setStyleSheet("font-size: 36px;")
        self.messageLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.messageLabel.setText("-")
        self.mainLayout.addWidget(self.messageLabel, 0, 2, 2, 2)

        # Bottom Buttons
        policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        self.mainLayout.setRowMinimumHeight(3, 50)

        self.importButton = QtWidgets.QPushButton()
        self.importButton.setText(self.tran.exec("button.importList"))
        self.importButton.setSizePolicy(policy)

        def importButtonFunc():
            studentList = self.api.readFile("studentList")
            if studentList is None:
                return
            self.waitList.clear()
            self.calledList.clear()
            self.waitList.addItems([item["name"] for item in studentList])

        importButtonFunc()

        self.importButton.clicked.connect(importButtonFunc)
        self.mainLayout.addWidget(self.importButton, 3, 0, 1, 1)

        self.resetButton = QtWidgets.QPushButton()
        self.resetButton.setText(self.tran.exec("button.reset"))
        self.resetButton.setSizePolicy(policy)

        def resetButtonFunc():
            self.waitList.clear()
            self.calledList.clear()

        self.resetButton.clicked.connect(resetButtonFunc)
        self.mainLayout.addWidget(self.resetButton, 3, 1, 1, 1)

        self.randomPickButton = QtWidgets.QPushButton()
        self.randomPickButton.setText(self.tran.exec("button.randomPick"))
        self.randomPickButton.setSizePolicy(policy)

        def randomPickButtonFunc():
            studentList = [
                item.text()
                for i in range(self.waitList.count())
                if (item := self.waitList.item(i))
            ]
            if studentList:
                name = random.choice(studentList)
                self.messageLabel.setText(name)
                self.waitList.takeItem(studentList.index(name))
                self.calledList.addItem(name)
            else:
                self.messageLabel.setText("-")

        self.randomPickButton.clicked.connect(randomPickButtonFunc)
        self.mainLayout.addWidget(self.randomPickButton, 3, 2, 1, 1)

        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setText(self.tran.exec("button.cancel"))
        self.cancelButton.setSizePolicy(policy)

        def cancelButtonFunc():
            if self.calledList.currentItem() is None:
                self.messageLabel.setText("-")
                return
            name = self.calledList.currentItem().text()
            self.calledList.takeItem(self.calledList.currentIndex().row())
            self.waitList.addItem(name)

        self.cancelButton.clicked.connect(cancelButtonFunc)
        self.mainLayout.addWidget(self.cancelButton, 3, 3, 1, 1)

        self.setLayout(self.mainLayout)

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
