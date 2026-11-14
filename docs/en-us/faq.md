# FAQ

## My plugin is not loaded / no page appears

Check the logs under `logs/`. Common causes:

- The zip is corrupted or not a valid archive.
- The package is missing `config.json` or the entry file.
- `config.json` fields are missing or of the wrong type, e.g. `name` is not an i18n mapping.
- `name` lacks the current language key (raises `KeyError`).
- The entry file has a syntax error, or does not define `Window` / `onReceive`.

The main application logs the specific error and skips that plugin.

## How do I debug a plugin that fails to load

1. Open `logs/last.log` or the newest timestamped log.
2. Look for `ERROR` records and locate the plugin.
3. Fix the zip content and restart.

## readFile always returns None

- The data file does not exist or its JSON is malformed.
- `id` contains `../` or `..\` (blocked by path-traversal protection).
- This plugin id is not in `meta.allowRead` and is not `"*"`.

## writeFile fails

- The file does not exist: `writeFile` never creates one.
- This plugin id is not in `meta.allowWrite` and is not `"*"`.
- The object is not serializable.
- A filesystem error.

An interrupted write may leave a temp file under `data/temp/`; this is normal and safe to clean up.

## onReceive receives methods more than once

The signal is a broadcast: it fires on every plugin load, so an earlier plugin also receives events belonging to later plugins. Filter with `data["pluginId"] == self.api.pluginId`.

## showMessage shows nothing

- Called before UI init, so the message was dropped (a warning is logged).
- `duration` of 0 means it stays — it is not a failure to appear.
- Out-of-range `level` is clamped to 0-3, so the color may differ from expectation.

## addUpdateFunc never runs

- `duration` is in seconds; the first run happens `duration` seconds after registration.
- An exception in the callback aborts that tick; wrap it in `try`.

## Submodule import fails

`.py` files at the archive root are registered as `plugin_<id>.<filename>`; import with the full name:

```python
from plugin_example import helper
```

`import helper` and modules in subdirectories do not work.

## How do I make my plugin display in Chinese

- `name` must be an i18n mapping: `{"zh-cn": "示例", "en-us": "Example"}`.
- The main application language is set by the `Language` item on the settings page.
- Plugin strings use `language.json` + `translation`; see [methods](methods.md).

## How do I set the startup page

Enter the target page name in the settings page `FirstPage` field; it must match a tab label exactly (the plugin `config.name` value for the current language). If it does not match or is empty, no switch happens and the first page shows.

## Where are data files by default

Under `.src/data/`, as `data/<id>.json`. `data/temp/` is the temp directory for atomic writes.

## My plugin needs extra Python libraries

Import them inside the entry file. If a library is not installed, the plugin fails to load and logs an error — run `pip install` first.
