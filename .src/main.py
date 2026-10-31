import sys
from PySide6 import QtWidgets, QtCore
from dataclasses import dataclass
import types
import typing
import settingPage
import zipfile
import os
import json

__version__ = "0.0"


# Data Structures
@dataclass
class SidebarDataKeys:
    text: str | None
    func: types.FunctionType | None = lambda: None
    group: str | None = None


@dataclass
class PluginConfig:
    id: str
    version: str
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
    content: typing.Any

    def __post_init__(self):
        self.meta = self.Meta(**self.meta)


@dataclass
class PluginWindow:
    api: "API"
    onReceive: types.MethodType


# Program Built-in Methods
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
            btn.setObjectName(f"sidebar_{item.text}")
            if item.group is not None:
                btn.setProperty("group", item.group)
            btn.clicked.connect(item.func)
            layout.addWidget(btn)
    layout.addStretch()


def createFiles(structure: dict, parentPath: str = "."):
    for key in structure:
        if key.startswith("_"):
            continue
        item: dict = structure[key]
        currentPath = os.path.join(parentPath, key)
        if item["_type"] == "folder":
            os.makedirs(currentPath, exist_ok=True)
            createFiles(item, currentPath)
        elif item["_type"] == "file":
            if key not in os.listdir(parentPath):
                with open(currentPath, "w", encoding="utf-8") as write:
                    write.write(item.get("_content", ""))


def setPage(key: str, tabWidget: QtWidgets.QTabWidget):
    for index in range(tabWidget.count()):
        if tabWidget.tabText(index) == key:
            tabWidget.setCurrentIndex(index)


# Plugin Methods
class API:
    def __init__(self, pluginId: str):
        self.pluginId = pluginId

    def readFile(self, id: str, encoding: str = "utf-8"):
        if "../" in id or "..\\" in id:
            return None
        with open(f"data/{id}.json", "r", encoding=encoding) as f:
            data = json.load(f)
            data = DataFileFormat(**data)
        if self.pluginId in data.meta.allowRead or "*" in data.meta.allowRead:
            return data.content
        else:
            return None

    def writeFile(self, id: str, _object: typing.Any, encoding: str = "utf-8"):
        if "../" in id or "..\\" in id:
            return None
        with open(f"data/{id}.json", "r", encoding=encoding) as f:
            data = json.load(f)
            data = DataFileFormat(**data)
        if self.pluginId in data.meta.allowWrite or "*" in data.meta.allowWrite:
            with open(f"data/{id}.json", "w", encoding=encoding) as f:
                data.content = _object
                json.dump(data, f, ensure_ascii=False)
        else:
            return None


class Translation:
    def __init__(self, languageMap: dict[str, dict[str, str]], language: str):
        self.languageMap = languageMap
        self.language = language

    def exec(self, key: str, fallback: str = "") -> str:
        try:
            if self.language not in self.languageMap:
                if "en-us" not in self.languageMap:
                    return fallback
                else:
                    return self.languageMap["en-us"][key]
            else:
                return self.languageMap[self.language][key]
        except KeyError:
            return fallback


# Init
fileStructure = {
    "plugin": {"_type": "folder"},
    "data": {
        "_type": "folder",
        "temp": {"_type": "folder"},
        "setting.json": {
            "_type": "file",
            "content": '{"meta": {"description": "Provide settings for the page","allowRead": ["*"],"allowWrite": []},"content": {}}',
        },
    },
    "logs": {"_type": "folder"},
}
createFiles(fileStructure)
with open(f"data/setting.json", "r", encoding="utf-8") as f:
    setting = json.load(f)
    language = setting["content"]["general.language"]["value"]
    languageMap = {
        "zh-cn": {"setting": "设置"},
        "en-us": {"setting": "Setting"},
    }
    tran = Translation(languageMap, language)


class Window(QtWidgets.QMainWindow):
    signal = QtCore.Signal(dict)

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

*[group=text] {
    background-color: rgba(0, 0, 0, 0);
    font-size: 16px;
}
""")
        pageWidget = QtWidgets.QTabWidget()
        pageWidget.tabBar().hide()
        pageWidget.setStyleSheet("background: white;")

        pageWidget.addTab(settingPage.Setting(), tran.exec("setting"))

        # Plugin
        pluginButtons = []
        for file in os.listdir("plugin"):
            if not file.endswith(".zip"):
                continue
            with zipfile.ZipFile(f"plugin/{file}", "r") as content:
                # Import Plugin
                config: PluginConfig = PluginConfig(
                    **json.loads(content.read("config.json").decode("utf-8"))
                )
                plugin = types.ModuleType("plugin")
                exec(content.read(config.main), plugin.__dict__)
                sys.modules["plugin"] = plugin

                # Plugin Init
                pluginWindow: PluginWindow = plugin.Window()
                pluginWindow.api = API(config.id)
                self.signal.connect(pluginWindow.onReceive)
                if "language.json" in content.namelist():
                    self.signal.emit(
                        {
                            "type": "languageMap",
                            "pluginId": config.id,
                            "content": json.loads(content.read("language.json")),
                        }
                    )

                pageWidget.addTab(pluginWindow, config.name[language])
                pluginButtons.append(
                    SidebarDataKeys(
                        config.name[language],
                        lambda _, name=config.name[language]: setPage(name, pageWidget),
                    )
                )
        if pluginButtons:
            pluginButtons.append("-")

        # Emit Data
        self.signal.emit({"type": "setting", "content": setting["content"]})
        self.signal.emit({"type": "methods", "content": {"translation": Translation}})
        self.signal.emit({"type": "initUI"})

        createSidebar(
            sidebar,
            [
                *pluginButtons,
                SidebarDataKeys(
                    tran.exec("setting"),
                    lambda: setPage(tran.exec("setting"), pageWidget),
                ),
                SidebarDataKeys(f"v{__version__}", group="text"),
            ],
        )
        setPage(setting["content"]["general.fristPage"]["value"], pageWidget)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(pageWidget)

        container = QtWidgets.QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)


app = QtWidgets.QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
