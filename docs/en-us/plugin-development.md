# Plugin Development

## Package Layout

A plugin is a `.zip` archive containing at least:

```
your-plugin/
├── config.json      # plugin configuration
└── enter.py         # entry file (set by the `main` field in config.json)
```

## config.json

```json
{
  "id": "example",
  "version": "0.0",
  "main": "enter.py",
  "name": "Example",
  "author": "FelixHajimi",
  "description": "Example plugin"
}
```

| Field         | Description                                                        |
| ------------- | ------------------------------------------------------------------ |
| `id`          | unique plugin id, used for API permission checks                   |
| `version`     | plugin version                                                     |
| `main`        | entry file path (relative to the archive root)                     |
| `name`        | display name, supports i18n mapping (e.g. `{"zh-cn": "...", "en-us": "..."}`) |
| `author`      | author                                                             |
| `description` | plugin description                                                 |

You may optionally include a `language.json` in the package, whose keys match the main application's `Translation` language keys (`zh-cn` / `en-us`), to register the plugin's own language pack.

## Entry File

The entry file must define a `Window` class (subclass of `QtWidgets.QWidget`) and implement `initUI` and `onReceive`:

```python
from PySide6 import QtWidgets, QtCore

class API:
    def __init__(self, pluginId: str): ...
    def readFile(self, id: str, encoding: str = "utf-8"): ...

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.api: API

    def initUI(self):
        # initialize the UI (called after the plugin is loaded)
        pass

    @QtCore.Slot(dict)
    def onReceive(self, data: dict):
        # handle data broadcast by the main application
        pass
```

## Packaging

Zip your plugin source directory so that `config.json` sits at the archive root, then place the zip in the `plugin/` directory.

## Load Flow

1. The main application scans `plugin/*.zip`.
2. It reads `config.json` and validates the required fields.
3. It reads and executes the entry file pointed to by `main`, then instantiates `Window`.
4. It injects `Window.api`.
5. It connects `Window.onReceive` to the main-application signal.
6. If the package contains `language.json`, it broadcasts the `languageMap` event.
7. It adds the plugin page to the tab bar and its button to the sidebar.

If any step fails, the error is recorded in `logs/` and the plugin is skipped.

## See Also

- [Plugin API](plugin-api.md)
- [Events](events.md)
- [FAQ](faq.md)
