# FAQ

## My plugin is not loaded / no page appears

Check the logs under `logs/`. Common causes:

- The zip is corrupted or not a valid archive.
- The package is missing `config.json` or the entry file.
- `config.json` fields are missing or of the wrong type (e.g. `main` does not exist).
- The entry file has a syntax error, or does not define `Window` / `onReceive`.

The main application logs the specific error and skips that plugin, without affecting other plugins.

## How do I debug a plugin that fails to load

1. Open `logs/last.log` or the newest timestamped log file.
2. Look for `ERROR`-level records and locate the plugin.
3. Fix the zip content accordingly and restart.

## readFile always returns None

Possible causes:

- The data file does not exist or its JSON is malformed.
- `id` contains `../` or `..\` (blocked by path-traversal protection).
- The plugin id is not in `meta.allowRead` and is not `"*"`.

## writeFile fails

Possible causes:

- The plugin id is not in `meta.allowWrite` and is not `"*"` (no write permission).
- The object is not serializable.
- A filesystem error.

If a write is interrupted, a temp file may remain under `data/temp/`. This is normal and safe to clean up.

## How do I make my plugin display in Chinese

- The plugin `name` field supports i18n mapping: `{"zh-cn": "示例", "en-us": "Example"}`.
- The main application language is set by the `Language` item in the settings page.

## How do I set the startup page

In the settings page, enter the target page name (matching a tab label) in the `FristPage` field. Leaving it empty shows the first page.

## Where are data files by default

Under `.src/data/`, named `data/<id>.json`. `data/temp/` is the temporary directory for atomic writes.

## My plugin needs extra Python libraries

Import them inside the entry file. If a library is not installed, the plugin fails to load and logs an error — install the dependency with `pip install` first.

## Why does .gitignore exclude so many files

`.gitignore` excludes virtual environments, `logs/`, `__pycache__`, and underscore-prefixed internal files (`_*`). These are private and not published.
