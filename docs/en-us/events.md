# Events

At startup the main application broadcasts events to all plugins via a Qt signal. Plugins receive them in `Window.onReceive(data)`, distinguished by `data["type"]`.

## Event Types

| type          | content                          | description                      |
| ------------- | -------------------------------- | -------------------------------- |
| `languageMap` | plugin `language.json` content   | register plugin language pack    |
| `setting`     | `setting.json` content           | distribute global settings       |
| `methods`     | `{ "translation": Translation }` | expose main-application utilities |
| `initUI`      | —                                | notify plugin to initialize the UI |

## Receiving Example

```python
@QtCore.Slot(dict)
def onReceive(self, data: dict):
    if data["type"] == "initUI":
        self.initUI()
    elif data["type"] == "setting":
        # use global settings
        pass
```

## Notes

- `initUI` is the key initialization event; build your UI when you receive it.
- `languageMap` is broadcast only when the plugin package contains `language.json`.
