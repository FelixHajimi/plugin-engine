# 插件 API

插件加载后，主程序会注入 `Window.api`，类型为 `API(config.id)`。

## readFile

```python
def readFile(self, id: str, encoding: str = "utf-8")
```

读取 `data/<id>.json`，返回 `content` 字段。

- 仅当 `meta.allowRead` 包含本插件 id 或 `"*"` 时返回内容，否则返回 `None`。
- `id` 含 `../` 或 `..\` 时返回 `None`（路径穿越防护）。
- 文件不存在或 JSON 损坏时返回 `None`，并写入错误日志。

## writeFile

```python
def writeFile(self, id: str, _object: typing.Any, encoding: str = "utf-8")
```

写入 `data/<id>.json`，`_object` 会被放入 `content` 字段后序列化保存。

- 仅当 `meta.allowWrite` 包含本插件 id 或 `"*"` 时生效，否则返回 `None`。
- `id` 含 `../` 或 `..\` 时返回 `None`（路径穿越防护）。
- 采用临时文件 + `os.replace` 原子写入，避免写入中断导致文件损坏。
- 对象不可序列化或写入失败时返回 `None`，并写入错误日志。

## 返回约定

- 成功：`readFile` 返回 `content`；`writeFile` 无返回值。
- 失败：均返回 `None`，同时向 `logs/` 记录具体错误。

## 权限说明

读写授权由数据文件的 `meta.allowRead` / `meta.allowWrite` 控制，详见[数据文件格式](数据文件.md)。
