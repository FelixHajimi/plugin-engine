from PySide6 import QtWidgets
import typing
import re


class Translation:
    languageMap: dict[str, dict[str, typing.Any]]
    language: str

    def __init__(
        self, languageMap: dict[str, dict[str, typing.Any]], language: str
    ): ...

    def exec(self, key: str, fallback: str = "") -> typing.Any: ...


class AddItem(QtWidgets.QWidget):
    def __init__(
        self,
        tran: Translation,
        createFunc: typing.Callable,
        title: str,
        data: dict | None = None,
    ):
        super().__init__()
        self.tran = tran
        self.data: dict
        self.setWindowTitle(title)
        self.setFixedWidth(380)

        mainLayout = QtWidgets.QFormLayout(self)

        self.messageLineEdit = QtWidgets.QLineEdit()
        self.messageLineEdit.setPlaceholderText(tran.exec("createItem.message"))
        mainLayout.addRow(tran.exec("createItem.message") + ":", self.messageLineEdit)

        self.remarksTextEdit = QtWidgets.QTextEdit()
        self.remarksTextEdit.setPlaceholderText(tran.exec("createItem.remarks"))
        mainLayout.addRow(tran.exec("createItem.remarks") + ":", self.remarksTextEdit)

        self.typeCombobox = QtWidgets.QComboBox()
        self.typeCombobox.addItems(tran.exec("createItem.typeList"))
        mainLayout.addRow(tran.exec("createItem.type") + ":", self.typeCombobox)

        self.repeatCombobox = QtWidgets.QComboBox()
        self.repeatCombobox.addItems(tran.exec("createItem.repeatList"))
        self.repeatCombobox.currentIndexChanged.connect(self.changeTimeFormat)
        mainLayout.addRow(tran.exec("createItem.repeat") + ":", self.repeatCombobox)

        self.displayCombobox = QtWidgets.QComboBox()
        self.displayCombobox.addItems(tran.exec("createItem.displayList"))
        mainLayout.addRow(tran.exec("createItem.display") + ":", self.displayCombobox)

        # Time
        timeSettingGroup = QtWidgets.QGroupBox()
        timeSettingGroup.setTitle(tran.exec("createItem.timeSetting"))
        timeLayout = QtWidgets.QFormLayout(timeSettingGroup)

        self.timeLineEdit = QtWidgets.QLineEdit()
        self.timeLineEdit.setPlaceholderText("HH:MM:SS")
        timeLayout.addRow(tran.exec("createItem.time") + ":", self.timeLineEdit)

        weekGroup = QtWidgets.QGroupBox()
        weekGroup.setTitle(tran.exec("createItem.week"))
        self.weekGroupLayout = QtWidgets.QHBoxLayout(weekGroup)
        timeLayout.addRow(weekGroup)

        dayGroup = QtWidgets.QGroupBox()
        dayGroup.setTitle(tran.exec("createItem.day"))
        self.dayGroupLayout = QtWidgets.QGridLayout(dayGroup)
        timeLayout.addRow(dayGroup)

        monthGroup = QtWidgets.QGroupBox()
        monthGroup.setTitle(tran.exec("createItem.month"))
        self.monthGroupLayout = QtWidgets.QGridLayout(monthGroup)
        timeLayout.addRow(monthGroup)

        self.weekButtons: list[QtWidgets.QPushButton] = []
        for label in tran.exec("createItem.weekList"):
            button = QtWidgets.QPushButton()
            button.setCheckable(True)
            button.setText(label)
            self.weekButtons.append(button)
            self.weekGroupLayout.addWidget(button)
        self.dayButtons: list[QtWidgets.QPushButton] = []
        for index, label in enumerate(tran.exec("createItem.dayList")):
            button = QtWidgets.QPushButton()
            button.setCheckable(True)
            button.setText(label)
            self.dayButtons.append(button)
            self.dayGroupLayout.addWidget(button, index // 7, index % 7)
        self.monthButtons: list[QtWidgets.QPushButton] = []
        for index, label in enumerate(tran.exec("createItem.monthList")):
            button = QtWidgets.QPushButton()
            button.setCheckable(True)
            button.setText(label)
            self.monthButtons.append(button)
            self.monthGroupLayout.addWidget(button, index // 7, index % 7)

        mainLayout.addRow(timeSettingGroup)

        okButton = QtWidgets.QPushButton()

        def okFunc():
            if not re.fullmatch(r"\d\d:\d\d:\d\d", self.timeLineEdit.text()):
                return
            self.data = {
                "message": self.messageLineEdit.text(),
                "remarks": self.remarksTextEdit.toPlainText(),
                "type": self.typeCombobox.currentIndex(),
                "repeat": self.repeatCombobox.currentIndex(),
                "display": self.displayCombobox.currentIndex(),
                "time": {
                    "time": self.timeLineEdit.text(),
                    "week": [
                        index
                        for index, button in enumerate(self.weekButtons)
                        if button.isChecked()
                    ],
                    "day": [
                        index
                        for index, button in enumerate(self.dayButtons)
                        if button.isChecked()
                    ],
                    "month": [
                        index
                        for index, button in enumerate(self.monthButtons)
                        if button.isChecked()
                    ],
                },
            }
            createFunc(self.data)
            self.close()

        okButton.clicked.connect(okFunc)
        okButton.setText(tran.exec("createItem.ok"))
        mainLayout.addRow(okButton)

        self.changeTimeFormat(0)
        if data:
            self.messageLineEdit.setText(data["message"])
            self.remarksTextEdit.setText(data["remarks"])
            self.typeCombobox.setCurrentIndex(
                ["fixed", "temporary"].index(data["type"])
            )
            self.repeatCombobox.setCurrentIndex(
                ["day", "week", "month", "year"].index(data["repeat"])
            )
            self.displayCombobox.setCurrentIndex(
                ["normal", "countdown"].index(data["display"])
            )

            self.timeLineEdit.setText(data["time"]["time"])

            def setCheckedButtons(
                buttons: list[QtWidgets.QPushButton], checked: list[int]
            ):
                for button in checked:
                    buttons[button].setChecked(True)

            setCheckedButtons(self.weekButtons, [week for week in data["time"]["week"]])
            setCheckedButtons(self.dayButtons, [day for day in data["time"]["day"]])
            setCheckedButtons(
                self.monthButtons, [month for month in data["time"]["month"]]
            )

    def changeTimeFormat(self, index: int):
        def setDisabledButtons(buttons: list[QtWidgets.QPushButton], disabled: bool):
            for button in buttons:
                button.setDisabled(disabled)

        if index == 0:
            setDisabledButtons(self.weekButtons, True)
            setDisabledButtons(self.dayButtons, True)
            setDisabledButtons(self.monthButtons, True)
        elif index == 1:
            setDisabledButtons(self.weekButtons, False)
            setDisabledButtons(self.dayButtons, True)
            setDisabledButtons(self.monthButtons, True)
        elif index == 2:
            setDisabledButtons(self.weekButtons, True)
            setDisabledButtons(self.dayButtons, False)
            setDisabledButtons(self.monthButtons, True)
        elif index == 3:
            setDisabledButtons(self.weekButtons, True)
            setDisabledButtons(self.dayButtons, False)
            setDisabledButtons(self.monthButtons, False)
