from PySide6 import QtWidgets, QtCore
import time


class API:
    def __init__(self, pluginId: str): ...
    def readFile(self, id: str, encoding: str = "utf-8"): ...


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.api: API

    def updateTime(self):
        self.timeLabel.setText(time.strftime("%H : %M : %S", time.localtime()))
        self.dateLabel.setText(time.strftime("%Y-%m-%d %A", time.localtime()))

    def initUI(self):
        self.setStyleSheet("""
#timeLabel {
    font-size: 64px;
    font-weight: 600;
    color: #1f2937;
}
#dateLabel {
    font-size: 20px;
    color: #6b7280;
}
""")
        self.mainLayout = QtWidgets.QVBoxLayout()

        self.timeLabel = QtWidgets.QLabel()
        self.timeLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.timeLabel.setObjectName("timeLabel")
        self.mainLayout.addWidget(self.timeLabel)

        self.dateLabel = QtWidgets.QLabel()
        self.dateLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.dateLabel.setObjectName("dateLabel")
        self.mainLayout.addWidget(self.dateLabel)

        self.setLayout(self.mainLayout)

        self.updateTimer = QtCore.QTimer()
        self.updateTimer.timeout.connect(self.updateTime)
        self.updateTimer.start(1000)

    @QtCore.Slot(dict)
    def onReceive(self, data: dict):
        if data["type"] == "initUI":
            self.initUI()
