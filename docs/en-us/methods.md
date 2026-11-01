# methods Event: Main Program Utility Classes

The `methods` event exposes utilities to plugins

```json
{ "translation": Translation }
```

## Translation Class

### Interface Definition

```python
class Translation:
    languageMap: dict[str, dict[str, str]]
    language: str
    def __init__(self, languageMap: dict[str, dict[str, str]], language: str): ...
    def exec(self, key: str, fallback: str = "") -> str: ...
```

### Key Points

1. `translation` is an **already‑instantiated object**. Call `exec` directly; do not instantiate it again.
2. `exec` lookup rules: use current language first, fall back to `en‑us` on missing entry, return `fallback` if still missing.
3. Additional utilities may be added to the `content` dictionary in future updates. Plugins should perform null checks and must not assume fixed fields always exist.
