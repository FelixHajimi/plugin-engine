# 插件 API

插件加载后，主程序把 `API(config.id)` 实例注入到 `Window.api`。

```python
self.api.pluginId   # 本插件 id，可用于权限判断与 methods 事件过滤
```

## readFile

```python
def readFile(self, id: str, encoding: str = "utf-8")
```

读取 `data/<id>.json`，返回 `content` 字段。

- 仅当 `meta.allowRead` 含本插件 id 或 `"*"` 时返回内容，否则返回 `None`。
- `id` 含 `../` 或 `..\` 时返回 `None`（路径穿越防护）。
- 文件不存在或 JSON 损坏时返回 `None`，并写错误日志。

## writeFile

```python
def writeFile(self, id: str, _object, encoding: str = "utf-8")
```

把 `_object` 写入 `data/<id>.json` 的 `content` 字段。

- 仅当 `meta.allowWrite` 含本插件 id 或 `"*"` 时生效，否则返回 `None`。
- `id` 含 `../` 或 `..\` 时返回 `None`。
- 目标文件必须已存在：先读 `meta` 再写回，文件不存在直接失败。
- 临时文件 + `os.replace` 原子写入。
- 对象不可序列化或写入失败返回 `None`，并写错误日志。

## addUpdateFunc

```python
def addUpdateFunc(self, func: typing.Callable, duration: int)
```

注册周期回调，主程序每 50ms 检查一次。

- `duration` 单位为**秒**，首次执行在注册后 `duration` 秒，之后循环。
- 没有注销接口，注册即长期有效。
- 回调异常不会被主程序捕获，请自行 `try`。

## showMessage

```python
def showMessage(
    self,
    text: str,
    level: int = 0,
    duration: int = 3000,
    clickedFunc: typing.Callable | None = None,
    customWidget: QtWidgets.QWidget | None = None,
)
```

在窗口右下角弹出浮动消息卡片。

| 参数           | 说明                                                     |
| -------------- | -------------------------------------------------------- |
| `level`        | `0` 绿(🔧) / `1` 蓝(📄) / `2` 黄(⚠) / `3` 红(❌)，越界截断 |
| `duration`     | 自动消失时间，单位**毫秒**；`0` 表示常驻                  |
| `clickedFunc`  | 点击卡片回调，异常只记日志                                |
| `customWidget` | 附加在卡片内的自定义控件                                  |

- 最多同时 5 张，超出时挤掉最早的一张。
- 鼠标悬停时暂停计时，移出后重新计时。
- 消息列表未就绪时（早于界面初始化）会丢弃并写 warning。

## 返回约定

- 成功：`readFile` 返回 `content`；其余方法无返回值。
- 失败：返回 `None`，同时向 `logs/` 记录具体错误。

## 权限说明

读写授权由数据文件的 `meta.allowRead` / `meta.allowWrite` 控制，详见[数据文件格式](数据文件.md)。
