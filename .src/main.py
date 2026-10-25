import sys
from PySide6 import QtWidgets
from dataclasses import dataclass
import types
import home
import setting
import zipfile
import os
import json


@dataclass
class SidebarDataKeys:
    text: str | None
    func: types.FunctionType | None
    group: str | None = None


@dataclass
class PluginConfig:
    id: str
    verstion: str
    main: str
    name: str
    author: str
    description: str


@dataclass
class DataFileFormat:
    @dataclass
    class Meta:
        description: str
        allowRead: list[str]
        allowWrite: list[str]

    meta: Meta
    content: dict


def createSidebar(sidebar: QtWidgets.QWidget, data: list[SidebarDataKeys | str]):
    layout = QtWidgets.QVBoxLayout(sidebar)
    for item in data:
        if type(item) is str:
            if item == "-":
                line = QtWidgets.QFrame()
                line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
                layout.addWidget(line)
        else:
            btn = QtWidgets.QPushButton()
            btn.setText(item.text)
            btn.setObjectName(f"sidebar_{item.group if item.group else item.text}")
            btn.clicked.connect(item.func)
            layout.addWidget(btn)
    layout.addStretch()


def setCurrentKey(key: str, tabWidget: QtWidgets.QTabWidget):
    for index in range(tabWidget.count()):
        if tabWidget.tabText(index) == key:
            tabWidget.setCurrentIndex(index)


class API:
    def __init__(self, pluginId: str):
        self.pluginId = pluginId

    def readFile(self, id: str, encoding: str = "utf-8"):
        with open(f"data/{id}.json", "r", encoding=encoding) as read:
            data = json.load(read)
            data = DataFileFormat(
                meta=DataFileFormat.Meta(**data["meta"]), content=data["content"]
            )
        if self.pluginId in data.meta.allowRead or "*" in data.meta.allowRead:
            return data.content
        else:
            return None


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(1000, 800)
        sidebar = QtWidgets.QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet("""
#sidebar {border-right: 1px solid black;}
QPushButton {border: none;border-radius: 6px;background-color: rgba(0, 0, 0, 12);color: #333;padding: 6px 10px;}
QPushButton:hover {background-color: rgba(0, 0, 0, 25);}
QPushButton:pressed {background-color: rgba(0, 0, 0, 45);}

#sidebar_text {
    background-color: rgba(0, 0, 0, 0);
    font-size: 16px;
}
""")
        pageWidget = QtWidgets.QTabWidget()
        pageWidget.addTab(home.Home(), "Home")
        pageWidget.addTab(setting.Setting(), "Setting")
        pageWidget.tabBar().hide()
        pageWidget.setStyleSheet("background: white;")

        # Plugin
        pluginButtons = []
        for file in os.listdir("plugin"):
            if not file.endswith(".zip"):
                continue
            with zipfile.ZipFile(f"plugin/{file}", "r") as content:
                config: PluginConfig = PluginConfig(
                    **json.loads(content.read("config.json").decode("utf-8"))
                )
                plugin = types.ModuleType("plugin")
                exec(content.read(config.main), plugin.__dict__)
                sys.modules["plugin"] = plugin
                pluginWindow = plugin.Window()
                pluginWindow.api = API(config.id)
                pluginWindow.initUI()
                pageWidget.addTab(pluginWindow, config.name)
                pluginButtons.append(
                    SidebarDataKeys(
                        config.name,
                        lambda _, name=config.name: setCurrentKey(name, pageWidget),
                    )
                )

        createSidebar(
            sidebar,
            [
                SidebarDataKeys("Home", lambda: setCurrentKey("Home", pageWidget)),
                "-",
                SidebarDataKeys("Plugin List", lambda: None, "text"),
                *pluginButtons,
                "-",
                SidebarDataKeys(
                    "Setting", lambda: setCurrentKey("Setting", pageWidget)
                ),
            ],
        )

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(pageWidget)

        container = QtWidgets.QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)


app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet("""
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
window = Window()
window.show()
sys.exit(app.exec())
