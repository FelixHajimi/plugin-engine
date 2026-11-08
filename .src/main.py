import sys
from PySide6 import QtWidgets, QtCore
from dataclasses import dataclass
import types
import typing
import settingPage
import zipfile
import os
import json
import logging
import time

__version__ = "0.0"


# Data Structures
@dataclass
class SidebarDataKeys:
    text: str | None
    func: typing.Callable | None = lambda: None
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

        def get_dict(self):
            return {
                "description": self.description,
                "allowRead": self.allowRead,
                "allowWrite": self.allowWrite,
            }

    meta: Meta
    content: typing.Any

    def __post_init__(self):
        self.meta = self.Meta(**self.meta)

    def get_dict(self):
        return {"meta": self.meta.get_dict(), "content": self.content}


@dataclass
class PluginWindow:
    api: "API"
    onReceive: typing.Callable


@dataclass
class FuncItem:
    func: typing.Callable
    delay: int
    startTime: float


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
        try:
            with open(f"data/{id}.json", "r", encoding=encoding) as f:
                data = json.load(f)
                data = DataFileFormat(**data)
        except FileNotFoundError as error:
            logging.error(eval(tran.exec("log.error.readFileNotFound")), exc_info=True)
            return None
        except json.JSONDecodeError as error:
            logging.error(eval(tran.exec("log.error.readFileBadJson")), exc_info=True)
            return None

        if self.pluginId in data.meta.allowRead or "*" in data.meta.allowRead:
            return data.content
        else:
            return None

    def writeFile(self, id: str, _object: typing.Any, encoding: str = "utf-8"):
        if "../" in id or "..\\" in id:
            return None
        try:
            with open(f"data/{id}.json", "r", encoding=encoding) as f:
                data = json.load(f)
                data = DataFileFormat(**data)
        except FileNotFoundError as error:
            logging.error(eval(tran.exec("log.error.readFileNotFound")), exc_info=True)
            return None
        except json.JSONDecodeError as error:
            logging.error(eval(tran.exec("log.error.readFileBadJson")), exc_info=True)
            return None

        if self.pluginId in data.meta.allowWrite or "*" in data.meta.allowWrite:
            try:
                tempPath = f"data/temp/{id}.json"
                with open(tempPath, "w", encoding=encoding) as f:
                    data.content = _object
                    json.dump(data.get_dict(), f, ensure_ascii=False)
                os.replace(tempPath, f"data/{id}.json")
            except OSError as error:
                logging.error(
                    eval(tran.exec("log.error.writeFileFailed")), exc_info=True
                )
                return None
            except TypeError as error:
                logging.error(
                    eval(tran.exec("log.error.writeBadObject")), exc_info=True
                )
                return None
        else:
            logging.error(eval(tran.exec("log.error.noWritePermission")), exc_info=True)
            return None

    def addUpdateFunc(self, func: typing.Callable, delay: int):
        globalVariables.updateFuncs.append(FuncItem(func, delay, time.monotonic()))

    def showMessage(
        self,
        text: str,
        level: int = 0,
        delay: int = 3000,
        clickedFunc: typing.Callable = lambda: None,
        customWidget: QtWidgets.QWidget | None = None,
    ):
        messageWidget = QtWidgets.QWidget()
        messageWidget.setStyleSheet("padding: 5px;border-radius: 10px;")
        messageLayout = QtWidgets.QVBoxLayout(messageWidget)

        label = QtWidgets.QLabel()
        label.mousePressEvent = lambda _: clickedFunc()
        if level == 0:
            label.setStyleSheet("background-color: #37ff00")
            label.setText("🔧 " + text)
        elif level == 1:
            label.setStyleSheet("background-color: #0dadf9")
            label.setText("📄 " + text)
        elif level == 2:
            label.setStyleSheet("background-color: #ffe800")
            label.setText("⚠ " + text)
        elif level == 3:
            label.setStyleSheet("background-color: #fe534c")
            label.setText("❌ " + text)
        messageLayout.addWidget(label)

        if customWidget:
            messageLayout.addWidget(customWidget)

        window.messageLayout.addWidget(messageWidget)

        timer = QtCore.QTimer(messageWidget, singleShot=True)
        timer.timeout.connect(messageWidget.deleteLater)
        timer.start(delay)
        messageWidget.enterEvent = lambda _: timer.stop()
        messageWidget.leaveEvent = lambda _: timer.start(delay)


class Translation:
    def __init__(self, languageMap: dict[str, dict[str, typing.Any]], language: str):
        self.languageMap = languageMap
        self.language = language

    def exec(self, key: str, fallback: str = "") -> typing.Any:
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
## Create Files
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

## Log
logFiles = os.listdir("logs")
while len(logFiles) > 10:
    os.remove(f"logs/{logFiles[0]}")
    logFiles = os.listdir("logs")

handlerFormatter = logging.Formatter(
    "[%(levelname)s]<%(pathname)s>(%(asctime)s)\n%(message)s\n"
)

startTimeHandler = logging.FileHandler(
    f"logs/{time.strftime("%Y-%m-%d-%H-%M", time.localtime())}.log", encoding="utf-8"
)
startTimeHandler.setFormatter(handlerFormatter)
startTimeHandler.setLevel(logging.WARN)

lastHandler = logging.FileHandler("logs/last.log", "w", encoding="utf-8")
lastHandler.setFormatter(handlerFormatter)
lastHandler.setLevel(logging.DEBUG)

logger = logging.getLogger()
logger.addHandler(startTimeHandler)
logger.addHandler(lastHandler)
logger.setLevel(logging.DEBUG)

## Setting And Language
with open(f"data/setting.json", "r", encoding="utf-8") as f:
    setting = json.load(f)
    language = setting["content"]["general.language"]["value"]
    languageMap = {
        "zh-cn": {
            "setting": "设置",
            "log.error.pluginBadZip": 'f"插件 {file}: zip 损坏或不是有效压缩包"',
            "log.error.pluginNoAccess": 'f"插件 {file}: 文件不存在或无权读取"',
            "log.error.pluginMissingFile": 'f"插件 {file}: zip 内缺少必需文件(config.json / 入口文件)"',
            "log.error.pluginBadJson": 'f"插件 {file}: 文件编码或 JSON 格式错误"',
            "log.error.pluginBadConfig": 'f"插件 {file}: config.json 字段缺失或类型不符"',
            "log.error.pluginCodeError": 'f"插件 {file}: 插件代码语法错误或缺 Window/onReceive"',
            "log.error.pluginUnknown": 'f"插件 {file}: 未知错误 {type(error).__name__}: {error}"',
            "log.error.readFileNotFound": 'f"数据文件 {id} 不存在"',
            "log.error.readFileBadJson": 'f"数据文件 {id}: JSON 格式错误"',
            "log.error.writeFileFailed": 'f"写入数据文件 {id} 失败: {error}"',
            "log.error.writeBadObject": 'f"数据文件 {id} 内容不可序列化: {type(error).__name__}"',
            "log.error.noWritePermission": 'f"插件 {self.pluginId} 无 {id} 的写权限"',
        },
        "en-us": {
            "setting": "Setting",
            "log.error.pluginBadZip": 'f"Plugin {file}: zip is corrupted or not a valid archive"',
            "log.error.pluginNoAccess": 'f"Plugin {file}: file missing or no read permission"',
            "log.error.pluginMissingFile": 'f"Plugin {file}: required file missing in zip (config.json / entry)"',
            "log.error.pluginBadJson": 'f"Plugin {file}: invalid encoding or JSON format"',
            "log.error.pluginBadConfig": 'f"Plugin {file}: config.json fields missing or wrong type"',
            "log.error.pluginCodeError": 'f"Plugin {file}: syntax error or missing Window/onReceive"',
            "log.error.pluginUnknown": 'f"Plugin {file}: unknown error {type(error).__name__}: {error}"',
            "log.error.readFileNotFound": 'f"Data file {id} does not exist"',
            "log.error.readFileBadJson": 'f"Data file {id}: invalid JSON format"',
            "log.error.writeFileFailed": 'f"Failed to write data file {id}: {error}"',
            "log.error.writeBadObject": 'f"Data file {id} content is not serializable: {type(error).__name__}"',
            "log.error.noWritePermission": 'f"Plugin {self.pluginId} has no write permission to {id}"',
        },
    }

    tran = Translation(languageMap, language)


## Set Global Variables
class GlobalVariables:
    updateFuncs: list[FuncItem] = []


globalVariables = GlobalVariables()


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
        pageWidget.setObjectName("pageWidget")
        pageWidget.setStyleSheet("#pageWidget {background: white;}")

        messageWidget = QtWidgets.QWidget(pageWidget)
        messageWidget.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        self.messageLayout = QtWidgets.QVBoxLayout(messageWidget)
        self.messageLayout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignRight
        )
        pageWidget.resizeEvent = lambda event: messageWidget.resize(event.size())
        pageWidget.changeEvent = lambda _: messageWidget.raise_()

        pageWidget.addTab(settingPage.Setting(), tran.exec("setting"))

        self.mainTimer = QtCore.QTimer()
        self.mainTimer.timeout.connect(self.mainTimerFunc)
        self.mainTimer.start(50)

        # Plugin
        pluginButtons = []
        pluginLanguageMap = {}
        for file in os.listdir("plugin"):
            if not file.endswith(".zip"):
                continue
            try:
                with zipfile.ZipFile(f"plugin/{file}", "r") as content:
                    # Import Plugin
                    config: PluginConfig = PluginConfig(
                        **json.loads(content.read("config.json").decode("utf-8"))
                    )
                    pluginName = f"plugin_{config.id}"
                    plugin = types.ModuleType(pluginName)
                    plugin.__package__ = pluginName
                    plugin.__path__ = []
                    sys.modules[pluginName] = plugin
                    for name in content.namelist():
                        if (
                            name.endswith(".py")
                            and name != config.main
                            and name != "__init__.py"
                            and "/" not in name
                        ):
                            subName = f"{pluginName}.{name[:-3]}"
                            sub = types.ModuleType(subName)
                            sub.__package__ = pluginName
                            sub.__file__ = name
                            sys.modules[subName] = sub
                            exec(content.read(name), sub.__dict__)
                    exec(content.read(config.main), plugin.__dict__)

                    # Plugin Init
                    pluginWindow: PluginWindow = plugin.Window()
                    pluginWindow.api = API(config.id)
                    self.signal.connect(pluginWindow.onReceive)
                    if "language.json" in content.namelist():
                        pluginLanguageMap = json.loads(content.read("language.json"))
                    self.signal.emit(
                        {
                            "type": "methods",
                            "content": {
                                "translation": Translation(
                                    pluginLanguageMap,
                                    setting["content"]["general.language"]["value"],
                                )
                            },
                            "pluginId": config.id,
                        }
                    )

                    pageWidget.addTab(pluginWindow, config.name[language])
                    pluginButtons.append(
                        SidebarDataKeys(
                            config.name[language],
                            lambda _, name=config.name[language]: setPage(
                                name, pageWidget
                            ),
                        )
                    )
            except zipfile.BadZipFile as error:
                logging.error(eval(tran.exec("log.error.pluginBadZip")), exc_info=True)
            except (FileNotFoundError, PermissionError) as error:
                logging.error(
                    eval(tran.exec("log.error.pluginNoAccess")), exc_info=True
                )
            except KeyError as error:
                logging.error(
                    eval(tran.exec("log.error.pluginMissingFile")), exc_info=True
                )
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                logging.error(eval(tran.exec("log.error.pluginBadJson")), exc_info=True)
            except TypeError as error:
                logging.error(
                    eval(tran.exec("log.error.pluginBadConfig")), exc_info=True
                )
            except (SyntaxError, AttributeError) as error:
                logging.error(
                    eval(tran.exec("log.error.pluginCodeError")), exc_info=True
                )
            except Exception as error:
                logging.error(eval(tran.exec("log.error.pluginUnknown")), exc_info=True)

        if pluginButtons:
            pluginButtons.append("-")

        # Emit Data
        self.signal.emit({"type": "setting", "content": setting["content"]})
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
        setPage(setting["content"]["general.firstPage"]["value"], pageWidget)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(pageWidget)

        container = QtWidgets.QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def mainTimerFunc(self):
        nowTime = time.monotonic()
        for funcItem in globalVariables.updateFuncs:
            if nowTime - funcItem.startTime >= funcItem.delay:
                funcItem.func()
                funcItem.startTime = nowTime


app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet("""
/* Button: Basic */
*[class=button] {
    border-radius: 10px;
    background-color: rgba(0, 0, 0, 12);
    padding: 10px;
}
*[class=button]:hover {
    background-color: rgba(0, 0, 0, 25);
}
*[class=button]:pressed {
    background-color: rgba(0, 0, 0, 45);
}

/* Button: Primary */
*[class=button][type=primary] {
    background-color: #0095FF;
    color: #FFFFFF;
}
*[class=button][type=primary]:hover {
    background-color: #33AAFF;
}
*[class=button][type=primary]:pressed {
    background-color: #007ACC;
}

/* Button: Danger */
*[class=button][type=danger] {
    background-color: rgba(255, 59, 48, 15);
    color: #FF3B30;
}
*[class=button][type=danger]:hover {
    background-color: rgba(255, 59, 48, 30);
}
*[class=button][type=danger]:pressed {
    background-color: rgba(255, 59, 48, 45);
}

/* Button: Disabled */
*[class=button]:disabled {
    background-color: rgba(0, 0, 0, 6);
    color: rgba(0, 0, 0, 100);
}

/* Text */
*[class=text][type=title] {
    font-size: 18px;
    font-weight: bold;
    color: #1F1F1F;
}
*[class=text][type=subtitle] {
    font-size: 14px;
    color: #666666;
}
*[class=text][type=body] {
    font-size: 13px;
    color: #333333;
}
*[class=text][type=hint] {
    font-size: 12px;
    color: #999999;
}

/* Input */
*[class=input] {
    border: 1px solid #DDDDDD;
    border-radius: 8px;
    padding: 8px 10px;
    background-color: #FFFFFF;
}
*[class=input]:focus {
    border: 1px solid #0095FF;
}

/* Card container */
*[class=card] {
    background-color: #FFFFFF;
    border: 1px solid #EEEEEE;
    border-radius: 10px;
}
""")
window = Window()
window.show()
sys.exit(app.exec())
