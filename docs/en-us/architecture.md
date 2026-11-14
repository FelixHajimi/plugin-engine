# Project Structure

## Repository Layout

```
plugin-engine/
├── .src/                    # main application source
│   ├── main.py              # entry: plugin loading, signals, message cards, global style
│   ├── settingPage.py       # declarative settings page (auto-generated form + auto-save)
│   ├── _package.py          # packaging script: zips directories under plugin/
│   └── _test.py             # local scratch copy, not part of the runtime
├── docs/
│   ├── zh-cn/               # Chinese documentation
│   └── en-us/               # English documentation
├── Example/
│   ├── Plugin/example/      # example plugin source + example.zip
│   └── Data/example.json    # data-file format sample
├── LICENSE
├── README.md
└── README.zh-cn.md
```

## Runtime Directories

Created automatically on first run (under `.src/`):

```
.src/
├── plugin/          # plugin directory: *.zip and source directories to pack
├── data/
│   ├── setting.json # global settings
│   └── temp/        # temp directory for atomic writes
└── logs/            # logs
```

## Logging

- Each run creates `logs/<YYYY-MM-DD-HH-MM>.log`, recording WARN and above.
- `logs/last.log` records DEBUG and above and is **rewritten on every start**.
- At most 10 files are kept under `logs/` (including `last.log`); the oldest is removed.

## Module Responsibilities

| File / Directory | Responsibility                                              |
| ---------------- | ----------------------------------------------------------- |
| `main.py`        | app entry, plugin loading, signal broadcast, message cards, global style |
| `settingPage.py` | declarative settings page: builds the form from declarations and auto-saves |
| `_package.py`    | packaging script: removes old zips and repacks directories under `plugin/` |
| `plugin/`        | holds plugin zips                                           |
| `data/`          | data files, read/written by plugins via the API             |
| `logs/`          | runtime logs                                                |
