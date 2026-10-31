# Data File Format

Data files live in the `data/` directory and are JSON with permission metadata.

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

| Field              | Type     | Description                                            |
| ------------------ | -------- | ------------------------------------------------------ |
| `meta.description` | string   | file description                                       |
| `meta.allowRead`   | string[] | plugin ids allowed to read; `"*"` grants all           |
| `meta.allowWrite`  | string[] | plugin ids allowed to write; `"*"` grants all          |
| `content`          | any      | business data, read/written by plugins through the API |

## Permission Rules

- A plugin has a permission if its id is in the corresponding list, or `"*"` is present.
- Without permission, `readFile` / `writeFile` return `None` and log an error.

## Global Settings File

`data/setting.json` is a special settings file. Its `content` stores the current value of each setting:

```json
{
  "content": {
    "general.language": {
      "type": "currentText",
      "value": "zh-cn"
    }
  }
}
```

Settings are declared by the [settings page](../architecture.md) and saved automatically.
