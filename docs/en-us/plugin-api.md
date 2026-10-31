# Plugin API

After a plugin is loaded, the main application injects `Window.api`, an `API(config.id)` instance.

## readFile

```python
def readFile(self, id: str, encoding: str = "utf-8")
```

Reads `data/<id>.json` and returns the `content` field.

- Returns the content only if `meta.allowRead` contains the plugin id or `"*"`; otherwise returns `None`.
- Returns `None` if `id` contains `../` or `..\` (path-traversal protection).
- Returns `None` if the file is missing or the JSON is malformed, and logs the error.

## writeFile

```python
def writeFile(self, id: str, _object: typing.Any, encoding: str = "utf-8")
```

Writes `data/<id>.json`. `_object` is placed into the `content` field and serialized.

- Takes effect only if `meta.allowWrite` contains the plugin id or `"*"`; otherwise returns `None`.
- Returns `None` if `id` contains `../` or `..\` (path-traversal protection).
- Uses a temp file plus `os.replace` for atomic writes, avoiding file corruption on interruption.
- Returns `None` and logs the error if the object is not serializable or the write fails.

## Return Conventions

- Success: `readFile` returns `content`; `writeFile` returns nothing.
- Failure: both return `None`, and the specific error is logged under `logs/`.

## Permissions

Read/write authorization is controlled by the data file's `meta.allowRead` / `meta.allowWrite`. See [Data File Format](data-file.md).
