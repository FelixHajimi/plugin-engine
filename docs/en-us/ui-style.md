# UI Style

The main application provides global styles via `app.setStyleSheet`. Set `class` / `type` properties on widgets to use them — no custom QSS needed.

## Buttons

```python
btn = QtWidgets.QPushButton("OK")
btn.setProperty("class", "button")          # required: base button
btn.setProperty("type", "primary")          # optional: primary / danger
```

| Property                             | Effect                                  |
| ------------------------------------ | --------------------------------------- |
| `class=button`                       | rounded, light gray background, padding |
| `class=button` `type=primary`        | blue background, white text, hover/pressed |
| `class=button` `type=danger`         | red text on light red background        |
| `:disabled`                          | grayed out                              |

## Text

```python
label = QtWidgets.QLabel("Title")
label.setProperty("class", "text")
label.setProperty("type", "title")
```

| `type`     | Size / color          |
| ---------- | --------------------- |
| `title`    | 18px, bold, `#1F1F1F` |
| `subtitle` | 14px, `#666666`       |
| `body`     | 13px, `#333333`       |
| `hint`     | 12px, `#999999`       |

## Input and Containers

| Property         | Effect                                          |
| ---------------- | ----------------------------------------------- |
| `class=input`    | input-like widgets: rounded border, blue focus  |
| `class=card`     | card container: white, light border, rounded    |

## Sidebar

`group=text` marks a plain-text sidebar entry (no background, 16px), matching `SidebarButtonData(group="text")`.

## Repolishing After Runtime Changes

After changing `class` / `type` at runtime, reapply the style:

```python
btn.setProperty("type", "danger")
btn.style().unpolish(btn)
btn.style().polish(btn)
```

## Message Cards

Use `api.showMessage` for floating messages; colors and animation are built in. See [Plugin API](plugin-api.md).
