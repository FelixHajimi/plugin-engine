# Plugin API

After loading, the main application injects an `API(config.id)` instance into `Window.api`.

```python
self.api.pluginId   # this plugin's id, for permission checks and methods filtering
```

## readFile

```python
def readFile(self, id: str, encoding: str = "utf-8")
```

Reads `data/<id>.json` and returns the `content` field.

- Returns the content only if `meta.allowRead` contains this plugin id or `"*"`; otherwise returns `None`.
- Returns `None` if `id` contains `../` or `..\` (path-traversal protection).
- Returns `None` if the file is missing or the JSON is malformed, and logs the error.

## writeFile

```python
def writeFile(self, id: str, _object, encoding: str = "utf-8")
```

Writes `_object` into the `content` field of `data/<id>.json`.

- Takes effect only if `meta.allowWrite` contains this plugin id or `"*"`; otherwise returns `None`.
- Returns `None` if `id` contains `../` or `..\`.
- The target file must already exist: it reads `meta` first and writes back. A missing file fails.
- Uses a temp file plus `os.replace` for atomic writes.
- Returns `None` and logs the error if the object is not serializable or the write fails.

## addUpdateFunc

```python
def addUpdateFunc(self, func: typing.Callable, duration: int)
```

Registers a periodic callback; the main application checks every 50ms.

- `duration` is in **seconds**; the first run happens `duration` seconds after registration, then repeats.
- There is no unregister API — once registered, it stays active.
- Exceptions from the callback are not caught by the main application; wrap it in `try`.

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

Shows a floating message card at the bottom-right of the window.

| Parameter      | Description                                                        |
| -------------- | ------------------------------------------------------------------ |
| `level`        | `0` green (🔧) / `1` blue (📄) / `2` yellow (⚠) / `3` red (❌); out-of-range is clamped |
| `duration`     | auto-dismiss delay in **milliseconds**; `0` means it stays         |
| `clickedFunc`  | click callback; exceptions are only logged                         |
| `customWidget` | extra widget embedded in the card                                  |

- At most 5 cards at once; the oldest is pushed out.
- Hovering pauses the timer; leaving restarts it.
- If the message list is not ready (before UI init), the message is dropped and a warning is logged.

## Return Conventions

- Success: `readFile` returns `content`; other methods return nothing.
- Failure: returns `None`, and the specific error is logged under `logs/`.

## Permissions

Read/write authorization is controlled by the data file's `meta.allowRead` / `meta.allowWrite`. See [Data File Format](data-file.md).
