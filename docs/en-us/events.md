# Events

The main application broadcasts events to plugins via a Qt signal. Plugins receive them in `Window.onReceive(data)`, distinguished by `data["type"]`.

## Event Types

| type      | Triggered when                    | content                          | Description              |
| --------- | --------------------------------- | -------------------------------- | ------------------------ |
| `methods` | each plugin finishes loading      | `{ "translation": Translation }` | utilities, see [methods](methods.md) |
| `setting` | after all plugins load            | `setting.json` content           | distribute global settings |
| `initUI`  | after `setting`, once             | —                                | notify the plugin to build its UI |

The `methods` event also carries a top-level `pluginId` field identifying which plugin this broadcast belongs to.

## Broadcast Nature of methods

The signal is a broadcast: it is emitted once per plugin load, and **every connected plugin receives it**. So when plugin B loads, plugin A (already loaded) receives another `methods` whose `translation` belongs to B and whose `pluginId` is B.

Filter by `pluginId` and keep only your own:

```python
if data["type"] == "methods" and data["pluginId"] == self.api.pluginId:
    self.translation = data["content"]["translation"]
```

## setting content

`content` is keyed by setting id, each value being `{"type": ..., "value": ...}`:

```json
{
  "general.language": { "type": "currentText", "value": "zh-cn" },
  "general.firstPage": { "type": "text", "value": "" }
}
```

Current language: `data["content"]["general.language"]["value"]`.

## Receiving Example

```python
@QtCore.Slot(dict)
def onReceive(self, data: dict):
    if data["type"] == "methods":
        if data["pluginId"] == self.api.pluginId:
            self.tran = data["content"]["translation"]
    elif data["type"] == "setting":
        self.setting = data["content"]
    elif data["type"] == "initUI":
        self.initUI()
```
