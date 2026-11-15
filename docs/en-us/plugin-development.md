# Plugin Development

## Package Layout

A plugin is a `.zip` archive containing at least:

```
your-plugin/
├── config.json      # plugin configuration
├── enter.py         # entry file (set by the `main` field)
└── xxx.py           # optional: sibling submodules
```

## config.json

```json
{
    "id": "example",
    "version": "0.0",
    "main": "enter.py",
    "name": { "zh-cn": "示例", "en-us": "Example" },
    "author": "FelixHajimi",
    "description": { "zh-cn": "示例插件", "en-us": "Example plugin" }
}
```

| Field         | Description                                                                   |
| ------------- | ----------------------------------------------------------------------------- |
| `id`          | unique plugin id, used for API permission checks                              |
| `version`     | plugin version                                                                |
| `main`        | entry file path (relative to the archive root)                                |
| `name`        | display name, **must** be an i18n mapping containing the current language key |
| `author`      | author                                                                        |
| `description` | plugin description; string or i18n mapping                                    |

`name` is read as `config.name[language]`: a missing current-language key raises `KeyError` and the plugin fails to load.

## language.json (optional)

Provide `language.json` at the archive root to register the plugin's own strings:

```json
{
    "zh-cn": { "title": "示例" },
    "en-us": { "title": "Example" }
}
```

The main application reads it and passes it to the `Translation` instance in the `methods` event. See [methods](methods.md).

## Submodules (optional)

Every `.py` at the archive root except `main` and `__init__.py` is registered as `plugin_<id>.<filename>` and executed. Import them like this:

```python
from plugin_example import helper    # helper.py
```

Only the root directory is supported; `.py` files in subdirectories are not registered.

## Entry File

You must define a `Window` class (subclass of `QtWidgets.QWidget`) with `onReceive`:

```python
from qtpy import QtWidgets, QtCore

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.api  # injected by the main application

    def initUI(self):
        # your own convention; build the UI after receiving initUI
        pass

    @QtCore.Slot(dict)
    def onReceive(self, data: dict):
        if data["type"] == "initUI":
            self.initUI()
```

The main application only requires `Window` and `onReceive`. `initUI` is a recommended convention, called by the plugin itself when it receives `initUI`.

## Packaging

Zip the source directory so `config.json` sits at the archive root, then place the zip in `plugin/`.

You can also use `.src/_package.py` for batch packaging: put source directories in `plugin/`, run the script, and it generates same-named zips and removes old ones.

## Load Flow

1. Scan `plugin/*.zip`.
2. Parse `config.json` and build the plugin config; missing fields or wrong types fail.
3. Register root submodules.
4. Execute the entry file named by `main` and instantiate `Window`.
5. Inject `Window.api` and connect `Window.onReceive` to the main signal.
6. Read `language.json` if present, then broadcast the `methods` event to loaded plugins.
7. Add the page to the tab bar and its button to the sidebar.

After all plugins load, broadcast `setting`, then `initUI`.

Any failure is logged under `logs/` and the plugin is skipped, without affecting others.

## See Also

- [Plugin API](plugin-api.md)
- [Events](events.md)
- [UI Style](ui-style.md)
- [FAQ](faq.md)
