from PySide6 import QtWidgets, QtCore
import time
import typing
from dataclasses import dataclass, field
from . import addItem


class Translation:
    languageMap: dict[str, dict[str, typing.Any]]
    language: str

    def __init__(
        self, languageMap: dict[str, dict[str, typing.Any]], language: str
    ): ...
    def exec(self, key: str, fallback: str = "") -> typing.Any: ...


tran: Translation


class API:
    pluginId: str

    def readFile(self, id: str, encoding: str = "utf-8"): ...
    def writeFile(self, id: str, _object: typing.Any, encoding: str = "utf-8"): ...
    def showMessage(
        self,
        text: str,
        level: int = 0,
        delay: int = 3000,
        clickedFunc: typing.Callable = lambda: None,
        customWidget: QtWidgets.QWidget | None = None,
    ): ...
    def addUpdateFunc(self, func: typing.Callable, delay: int): ...


@dataclass
class TimeItem:
    @dataclass
    class Time:
        time: str
        week: list[int] = field(default_factory=list)
        day: list[int] = field(default_factory=list)
        month: list[int] = field(default_factory=list)

        def getTimeValue(self) -> int:
            h, m, s = map(int, self.time.split(":"))
            return h * 3600 + m * 60 + s

    message: str
    remarks: str
    type: str
    repeat: str
    display: str
    time: Time

    def __post_init__(self):
        self.time = self.Time(**self.time)
        if isinstance(self.type, int):
            self.type = ["fixed", "temporary"][self.type]
        if isinstance(self.repeat, int):
            self.repeat = ["day", "week", "month", "year"][self.repeat]
        if isinstance(self.display, int):
            self.display = ["normal", "countdown"][self.display]

    def getDict(self):
        return {
            "message": self.message,
            "remarks": self.remarks,
            "type": self.type,
            "repeat": self.repeat,
            "display": self.display,
            "time": {
                "time": self.time.time,
                "week": self.time.week,
                "day": self.time.day,
                "month": self.time.month,
            },
        }


def isInToday(item: TimeItem, now: time.struct_time) -> bool:
    repeat = item.repeat
    matched = False
    if repeat == "day":
        matched = True
    elif repeat == "week":
        matched = now.tm_wday in item.time.week
    elif repeat == "month":
        matched = now.tm_mday in item.time.day
    elif repeat == "year":
        matched = now.tm_mon in item.time.month and now.tm_mday in item.time.day
    if not matched:
        return False
    now_sec = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
    return item.time.getTimeValue() > now_sec


def displayText(item: TimeItem) -> str:
    def findRecent(values: list[int], now: int) -> int:
        if not values:
            return now
        candidates = [number for number in values if number >= now]
        return min(candidates) if candidates else values[0]

    nowTime = time.localtime()

    _time = item.time.time
    week = tran.exec("createItem.weekList")[findRecent(item.time.week, nowTime.tm_wday)]
    day = tran.exec("createItem.dayList")[
        findRecent(item.time.day, nowTime.tm_mday - 1)
    ]
    month = tran.exec("createItem.monthList")[
        findRecent(item.time.month, nowTime.tm_mon - 1)
    ]
    if item.repeat == "day":
        return f"{item.message} - {_time}"
    elif item.repeat == "week":
        return f"{item.message} - {week} {_time}"
    elif item.repeat == "month":
        return f"{item.message} - {day} {_time}"
    elif item.repeat == "year":
        return f"{item.message} - {month}{day} {_time}"
    return ""


class TimeItemWindow(QtWidgets.QWidget):
    def __init__(self, item: TimeItem, api: API, updateList: typing.Callable):
        super().__init__()
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("timeItemWindow")
        self.setFixedHeight(50)
        self.editItemWindow: QtWidgets.QWidget
        self.item = item
        self.api = api
        self.updateList = updateList
        self.initUI()

    def initUI(self):
        self.mainLayout = QtWidgets.QHBoxLayout(self)

        self.displayLabel = QtWidgets.QLabel()
        self.displayLabel.setText(displayText(self.item))
        if self.item.type == "fixed":
            self.displayLabel.setStyleSheet(
                "background-color: rgba(0, 0, 0, 0);color: rgba(0, 0, 0, 255)"
            )
        elif self.item.type == "temporary":
            self.displayLabel.setStyleSheet(
                "background-color: rgba(0, 0, 0, 0);color: rgba(0, 0, 0, 100)"
            )
        self.mainLayout.addWidget(self.displayLabel)
        self.mainLayout.addStretch()

        self.editButton = QtWidgets.QPushButton()
        self.editButton.setText("🖊")
        self.editButton.setProperty("class", "button")

        self.editButton.clicked.connect(self.editButtonFunc)
        self.editButton.hide()
        self.mainLayout.addWidget(self.editButton)

        self.deleteButton = QtWidgets.QPushButton()
        self.deleteButton.setProperty("class", "button")
        self.deleteButton.setText("🚮")

        self.deleteButton.clicked.connect(self.deleteButtonFunc)
        self.deleteButton.hide()
        self.mainLayout.addWidget(self.deleteButton)

    def editButtonFunc(self):
        def createFunc(itemData: dict):
            data = self.api.readFile("timeline")
            if self.item.message in data:
                del data[self.item.message]
            self.item = TimeItem(**itemData)
            if self.item.message not in data:
                data[self.item.message] = self.item.getDict()
            self.api.writeFile("timeline", data)

            self.displayLabel.setText(displayText(self.item))
            if self.item.type == "fixed":
                self.displayLabel.setStyleSheet(
                    "background-color: rgba(0, 0, 0, 0);color: rgba(0, 0, 0, 255)"
                )
            elif self.item.type == "temporary":
                self.displayLabel.setStyleSheet(
                    "background-color: rgba(0, 0, 0, 0);color: rgba(0, 0, 0, 100)"
                )
            self.updateList()
        self.editItemWindow = addItem.AddItem(
            tran,
            createFunc,
            tran.exec("editSchedule"),
            self.item.getDict(),
        )
        self.editItemWindow.show()

    def deleteButtonFunc(self, force: bool=False):
        confirmationDelete = None
        if not force:
            confirmationDelete = QtWidgets.QMessageBox.question(
                None,
                tran.exec("confirmationDelete"),
                tran.exec("confirmationDelete") + self.item.message + "?",
            )
        if confirmationDelete == QtWidgets.QMessageBox.StandardButton.Yes or force:
            data = self.api.readFile("timeline")
            delList = []
            for key in data:
                if key == self.item.message:
                    delList.append(key)
            for key in delList:
                del data[key]
            self.api.writeFile("timeline", data)
            self.deleteLater()
            self.updateList()

    def enterEvent(self, event):
        self.setStyleSheet(
            "#timeItemWindow{border-radius: 10px;background-color: rgba(0, 0, 0, 25);}"
        )
        self.editButton.show()
        self.deleteButton.show()

    def leaveEvent(self, event):
        self.setStyleSheet("#timeItemWindow{background-color: rgba(0, 0, 0, 0)}")
        self.editButton.hide()
        self.deleteButton.hide()


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.api: API

        self.addItemWindow: addItem.AddItem
        self.todayList: list[TimeItemWindow] = []
        self.futureList: list[TimeItemWindow] = []

    def initUI(self):
        self.mainLayout = QtWidgets.QGridLayout(self)

        self.todayScrollArea = QtWidgets.QScrollArea()
        self.todayScrollArea.setProperty("class", "card")
        self.todayScrollArea.setWidgetResizable(True)

        self.todayWidget = QtWidgets.QWidget()
        self.todayWidget.setObjectName("todayWidget")
        self.todayWidget.setStyleSheet("#todayWidget{background-color: #FFFFFF}")
        self.todayScrollArea.setWidget(self.todayWidget)

        self.todayWidgetLayout = QtWidgets.QVBoxLayout(self.todayWidget)
        self.mainLayout.addWidget(self.todayScrollArea, 0, 0, 1, 1)

        self.futureScrollArea = QtWidgets.QScrollArea()
        self.futureScrollArea.setProperty("class", "card")
        self.futureScrollArea.setWidgetResizable(True)

        self.futureWidget = QtWidgets.QWidget()
        self.futureWidget.setObjectName("futureWidget")
        self.futureWidget.setStyleSheet("#futureWidget{background-color: #FFFFFF}")
        self.futureScrollArea.setWidget(self.futureWidget)

        self.futureWidgetLayout = QtWidgets.QVBoxLayout(self.futureWidget)
        self.mainLayout.addWidget(self.futureScrollArea, 0, 1, 1, 1)

        self.addItemButton = QtWidgets.QPushButton()
        self.addItemButton.setProperty("class", "button")
        self.addItemButton.setText(tran.exec("addSchedule"))

        def addItemFunc():
            def createFunc(itemData: dict):
                data: dict[str, dict] = self.api.readFile("timeline")
                item = TimeItem(**itemData).getDict()
                data[item["message"]] = item
                self.api.writeFile("timeline", data)
                self.updateList()

            self.addItemWindow = addItem.AddItem(
                tran, createFunc, tran.exec("addSchedule")
            )
            self.addItemWindow.show()

        self.addItemButton.clicked.connect(addItemFunc)
        self.mainLayout.addWidget(self.addItemButton, 1, 0, 1, 2)

        # Update List
        self.updateList()

        # Detect List
        self.api.addUpdateFunc(self.detectList, 1)

    def updateList(self):
        for layout in (self.todayWidgetLayout, self.futureWidgetLayout):
            while layout.count() > 0:
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        self.todayList = []
        self.futureList = []
        data: dict = self.api.readFile("timeline")
        for item in data.values():
            item = TimeItem(**item)
            itemWindow = TimeItemWindow(item, self.api, self.updateList)
            if isInToday(item, time.localtime()):
                self.todayWidgetLayout.addWidget(itemWindow)
                self.todayList.append(itemWindow)
            else:
                self.futureWidgetLayout.addWidget(itemWindow)
                self.futureList.append(itemWindow)
        self.todayWidgetLayout.addStretch()
        self.futureWidgetLayout.addStretch()

    def detectList(self):
        nowTime = time.localtime()
        nowTime = nowTime.tm_hour * 3600 + nowTime.tm_min * 60 + nowTime.tm_sec
        delList: list[TimeItemWindow] = []
        for itemWindow in self.todayList:
            item = itemWindow.item
            itemTime = [int(time) for time in item.time.time.split(":")]
            itemTime = itemTime[0] * 3600 + itemTime[1] * 60 + itemTime[2]
            if abs(nowTime - itemTime) == 0:
                self.api.showMessage(
                    f"{item.message} {tran.exec("scheduleIsHere")}",
                    1,
                    clickedFunc=lambda item=item: self.api.showMessage(item.remarks, 1),
                )
                if item.type == "temporary":
                    delList.append(itemWindow)
        for window in delList:
            window.deleteButtonFunc(True)

    @QtCore.Slot(dict)
    def onReceive(self, data: dict):
        global tran
        if not data.get("pluginId", "*") in (self.api.pluginId, "*"):
            return
        content = data.get("content")
        if data["type"] == "methods":
            tran = content["translation"]
        elif data["type"] == "initUI":
            self.initUI()
