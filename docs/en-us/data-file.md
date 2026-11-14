# Data File Format

Data files live in the `data/` directory as JSON with permission metadata.

## Structure

```json
{
  "meta": {
    "description": "Example data file",
    "allowRead": ["*"],
    "allowWrite": ["*"]
  },
  "content": { "main": "data" }
}
```

## Fields

| Field              | Type                     | Description                                  |
| ------------------ | ------------------------ | -------------------------------------------- |
| `meta.description` | string / i18n object     | description only; not used for authorization |
| `meta.allowRead`   | string[]                 | plugin ids allowed to read; `"*"` grants all |
| `meta.allowWrite`  | string[]                 | plugin ids allowed to write; `"*"` grants all|
| `content`          | any                      | business data, read/written via the API      |

## Reading and Writing

- `readFile(id)` returns `content`.
- `writeFile(id, obj)` replaces `content` with `obj` and saves; the file must already exist.
- Writes go through a `data/temp/` temp file plus `os.replace`, so an interruption cannot corrupt the original.
- Temp files may remain in `data/temp/` after a restart; they are safe to clean up.

## Permission Rules

- A plugin has a permission if its id is in the list, or `"*"` is present.
- Without permission, `readFile` / `writeFile` return `None` and log an error.

## Global Settings File

`data/setting.json` is special: `meta.allowRead` is `["*"]` and `allowWrite` is empty — plugins may read but not write it. `content` stores the current value of each setting:

```json
{
  "content": {
    "general.language": { "type": "currentText", "value": "zh-cn" },
    "general.firstPage": { "type": "text", "value": "" }
  }
}
```

The settings page saves automatically every second, also via an atomic `data/temp/` write. See [Settings Page](settings-page.md) for how items are declared.
