# Settings Page

The settings page is generated from the `self.data` declaration in `settingPage.py`; no hand-written widgets. Restart after editing the declaration.

## Declaration Structure

```python
self.data = {
    "_type": "group",
    "General": {
        "_type": "group",
        "_label": {"zh-cn": "常规", "en-us": "General"},
        "FirstPage": {
            "_type": "item",
            "_id": "general.firstPage",
            "_valueType": "lineedit",
            "_default": {"zh-cn": "", "en-us": ""},
            "_placeholder": {"zh-cn": "启动界面", "en-us": "FirstPage"},
            "_label": {"zh-cn": "启动界面", "en-us": "FirstPage"},
        },
    },
}
```

- Keys starting with `_` are attributes; other keys are groups or items and may nest freely.
- `group` renders as a `QGroupBox`; `item` renders as one row of "label + widget".
- `_id` is the unique setting id, used as the widget `objectName` and the key in `setting.json`.

## Widget Types

| `_valueType`  | Widget          | Extra fields                                        |
| ------------- | --------------- | --------------------------------------------------- |
| `language`    | combo box       | `_valueList` (string array), `_default` (string)    |
| `combobox`    | combo box       | `_valueList`, `_default` (both i18n maps)           |
| `checkbox`    | check box       | `_default` (i18n boolean)                           |
| `slider`      | slider          | `_min`, `_max`, `_default`, `_prefix`, `_suffix`    |
| `spinbox`     | spin box        | same as `slider`                                    |
| `lineedit`    | line edit       | `_default`, `_placeholder` (i18n)                   |
| `filepicker`  | line edit + browse | `_default` (string), `_filter` (i18n filter string) |
| `colorpicker` | line edit + picker | `_default` (color string)                        |

`slider` / `spinbox` show "prefix + current value + suffix (min-max)" to the right.

## Saved Format

Auto-saved every second into `setting.json`'s `content`:

| Widget type                            | Saved as                                |
| -------------------------------------- | --------------------------------------- |
| `language`, `combobox`                 | `{"type": "currentText", "value": ...}` |
| `checkbox`                             | `{"type": "checked", "value": ...}`     |
| `slider`, `spinbox`                    | `{"type": "value", "value": ...}`       |
| `lineedit`, `filepicker`, `colorpicker`| `{"type": "text", "value": ...}`        |

Saving goes through `data/temp/setting.json` with an atomic replace.

## Built-in Items

| id                  | Type     | Purpose                                              |
| ------------------- | -------- | ---------------------------------------------------- |
| `general.language`  | combo    | UI language, `zh-cn` / `en-us`                       |
| `general.firstPage` | line edit| startup page name, must match a tab label; empty shows the first page |

## Limitation

The settings page is declared by the main application only; plugins cannot add items to it.
