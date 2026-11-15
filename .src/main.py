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

# Program Information
__author__ = "FelixHajimi"
__description__ = "Plugin Engine"
__version__ = "re-0.0"


# Methods
## Data Class
@dataclass
class SidebarButtonData:
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

        def getDict(self):
            return {
                "description": self.description,
                "allowRead": self.allowRead,
                "allowWrite": self.allowWrite,
            }

    meta: Meta
    content: typing.Any

    def __post_init__(self):
        self.meta = self.Meta(**self.meta)

    def getDict(self):
        return {"meta": self.meta.getDict(), "content": self.content}


@dataclass
class PluginWindow:
    api: "API"
    onReceive: typing.Callable


@dataclass
class FuncItem:
    func: typing.Callable
    duration: int
    startTime: float


## Program Built-in Methods
def createSidebar(sidebar: QtWidgets.QWidget, data: list[SidebarButtonData | str]):
    layout = QtWidgets.QVBoxLayout(sidebar)
    for item in data:
        if isinstance(item, str):
            if item == "-":
                line = QtWidgets.QFrame()
                line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
                layout.addWidget(line)
        else:
            btn = QtWidgets.QPushButton()
            btn.setText(item.text)
            btn.setProperty("class", "button")
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


## Plugin Methods
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

    def writeFile(self, id: str, _object, encoding: str = "utf-8"):
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
                    json.dump(data.getDict(), f, ensure_ascii=False)
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

    def addUpdateFunc(self, func: typing.Callable, duration: int):
        GV.updateFuncs.append(FuncItem(func, duration, time.monotonic()))

    def showMessage(
        self,
        text: str,
        level: int = 0,
        duration: int = 3000,
        clickedFunc: typing.Callable | None = None,
        customWidget: QtWidgets.QWidget | None = None,
    ):
        messageList = GV.messageList
        if messageList is None:
            logging.warning(f"message list is not ready, message dropped: {text}")
            return
        messageList.addCard(text, level, duration, clickedFunc, customWidget)


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
            "_content": '{"meta": {"description": "Provide settings for the page","allowRead": ["*"],"allowWrite": []},"content": {}}',
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
    f"logs/{time.strftime('%Y-%m-%d-%H-%M', time.localtime())}.log", encoding="utf-8"
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
    messageList: "MessageList | None" = None


GV = GlobalVariables()


## Message
class MessageCard(QtWidgets.QFrame):
    dismissed = QtCore.Signal(object)

    STYLE_MAP = (
        ("#37FF00", "#1F1F1F", "🔧"),
        ("#0DADF9", "#FFFFFF", "📄"),
        ("#FFE800", "#1F1F1F", "⚠"),
        ("#FE534C", "#FFFFFF", "❌"),
    )
    HPADDING, VPADDING = 12, 8
    closing = False
    fadeInDone = False
    fadeMode = ""

    def __init__(
        self,
        parent: QtWidgets.QWidget,
        text: str,
        level: int,
        clickedFunc: typing.Callable,
        customWidget: QtWidgets.QWidget | None,
        duration: int,
        textWidth: int,
    ):
        super().__init__(parent)
        self.setObjectName("messageCard")
        self.clickedFunc = clickedFunc

        effectiveIndex = min(max(level, 0), len(self.STYLE_MAP) - 1)
        background, foreground, icon = self.STYLE_MAP[effectiveIndex]
        self.setStyleSheet(f"""
#messageCard {{
    background-color: {background};
    border-radius: 10px;
}}
""")
        if clickedFunc is not None:
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        content = f"{icon} {text}"
        self.textLabel = QtWidgets.QLabel(self)
        self.textLabel.setText(content)
        self.textLabel.setWordWrap(True)
        self.textLabel.setStyleSheet(
            f"color: {foreground}; background-color: transparent;"
        )
        self.textLabel.setAttribute(
            QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        metrics = self.textLabel.fontMetrics()
        naturalWidth = metrics.horizontalAdvance(content)
        labelWidth = naturalWidth + 4 if naturalWidth <= textWidth else textWidth
        self.textLabel.setFixedWidth(labelWidth)
        labelHeight = self.textLabel.heightForWidth(labelWidth)
        if labelHeight <= 0:
            labelHeight = metrics.height()
        self.textLabel.setFixedHeight(max(labelHeight, metrics.height()))

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(
            self.HPADDING, self.VPADDING, self.HPADDING, self.VPADDING
        )
        self.mainLayout.setSpacing(6)
        self.mainLayout.addWidget(self.textLabel)

        if customWidget is not None:
            customWidget.setParent(self)
            self.mainLayout.addWidget(customWidget)

        self.adjustSize()

        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.onTimeout)

        self.opacity = QtWidgets.QGraphicsOpacityEffect(self)
        self.opacity.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity)
        self.fade = QtCore.QPropertyAnimation(self.opacity, b"opacity", self)
        self.fade.finished.connect(self.onFadeFinished)

        if duration > 0:
            self.timer.start(duration)

    def onTimeout(self):
        if self.underMouse():
            return
        self.dismiss()

    def onFadeFinished(self):
        if self.fadeMode == "out":
            self.hide()
            self.dismissed.emit(self)

    def fadeTo(self, mode: str, value: float, duration: int):
        self.fadeMode = mode
        self.fade.stop()
        self.fade.setDuration(duration)
        self.fade.setStartValue(self.opacity.opacity())
        self.fade.setEndValue(value)
        self.fade.start()

    def showEvent(self, event):
        super().showEvent(event)
        if not self.fadeInDone and not self.closing:
            self.fadeInDone = True
            self.fadeTo("in", 1.0, 200)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.timer.stop()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if not self.closing and self.timer.interval() > 0:
            self.timer.start()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self.clickedFunc:
            try:
                self.clickedFunc()
            except Exception:
                logging.error("message click callback failed", exc_info=True)
        super().mousePressEvent(event)

    def dismiss(self, animate: bool = True):
        if self.closing:
            return
        self.closing = True
        self.timer.stop()
        if animate:
            self.fadeTo("out", 0.0, 200)
        else:
            self.hide()
            self.dismissed.emit(self)


class MessageList(QtCore.QObject):
    MARGIN = 16
    SPACING = 8
    MAX_COUNT = 5
    MAX_TEXT_WIDTH = 360

    def __init__(self, host: QtWidgets.QWidget):
        super().__init__(host)
        self.host = host
        self.cards: list[MessageCard] = []
        host.installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched is self.host and event.type() in (
            QtCore.QEvent.Type.Resize,
            QtCore.QEvent.Type.Show,
        ):
            self.relayout()
        return False

    def addCard(
        self,
        text: str,
        level: int = 0,
        duration: int = 3000,
        clickedFunc: typing.Callable | None = None,
        customWidget: QtWidgets.QWidget | None = None,
    ):
        while len(self.cards) >= self.MAX_COUNT:
            oldest = self.cards[0]
            if oldest.closing:
                self.cards.pop(0)
                continue
            oldest.dismiss(False)

        card = MessageCard(
            self.host,
            text,
            level,
            clickedFunc,
            customWidget,
            duration,
            self.textWidth(),
        )
        card.dismissed.connect(self.onDismissed)
        self.cards.append(card)
        card.show()
        self.relayout()

    def textWidth(self):
        room = self.host.width() - 2 * self.MARGIN - 2 * MessageCard.HPADDING
        return max(120, min(self.MAX_TEXT_WIDTH, room))

    def onDismissed(self, card: MessageCard):
        if card in self.cards:
            self.cards.remove(card)
        card.deleteLater()
        self.relayout()

    def relayout(self):
        right = self.host.width() - self.MARGIN
        bottom = self.host.height() - self.MARGIN
        y = bottom
        for card in reversed(self.cards):
            y -= card.height()
            card.move(max(self.MARGIN, right - card.width()), y)
            card.raise_()
            y -= self.SPACING


# Main Window
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
*[group=text] {
    background-color: rgba(0, 0, 0, 0);
    font-size: 16px;
}
""")
        pageWidget = QtWidgets.QTabWidget()
        pageWidget.tabBar().hide()
        pageWidget.setObjectName("pageWidget")
        pageWidget.setStyleSheet("#pageWidget {background: white;}")

        self.messageList = MessageList(pageWidget)
        GV.messageList = self.messageList
        pageWidget.currentChanged.connect(lambda *_: self.messageList.relayout())

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
                        SidebarButtonData(
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
                SidebarButtonData(
                    tran.exec("setting"),
                    lambda: setPage(tran.exec("setting"), pageWidget),
                ),
                SidebarButtonData(f"v {__version__}", group="text"),
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
        for funcItem in GV.updateFuncs:
            if nowTime - funcItem.startTime >= funcItem.duration:
                funcItem.func()
                funcItem.startTime = nowTime


if __name__ == "__main__":
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
