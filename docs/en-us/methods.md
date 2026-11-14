# methods Event: Main Application Utilities

The `methods` event delivers main-application utilities to plugins:

```json
{
  "type": "methods",
  "pluginId": "example",
  "content": { "translation": Translation }
}
```

`pluginId` identifies which plugin this broadcast belongs to; filter by it.

## Translation Class

### Interface

```python
class Translation:
    languageMap: dict[str, dict[str, typing.Any]]
    language: str
    def __init__(self, languageMap: dict, language: str) -> None: ...
    def exec(self, key: str, fallback: str = "") -> typing.Any: ...
```

`languageMap` is the content of this plugin's `language.json`; `language` is the main application's current language (e.g. `zh-cn`).

### Key Points

1. `translation` is an **already-instantiated object**. Call `exec` directly; do not instantiate it again.
2. `exec` lookup: current language first, then fall back to `en-us`, then return `fallback`.
3. The return type is `Any`: values in the language map may be strings, lists, etc., not necessarily `str`.
4. Without `language.json`, `languageMap` keeps whatever was read last (empty or a previous plugin's pack), so `exec` may return another plugin's strings.
5. `methods` is a broadcast: earlier plugins also receive later plugins' events. Filter by `pluginId`.
