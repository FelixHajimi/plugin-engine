# Project Structure

## Repository Layout

```
plugin-engine/
├── .src/                    # main application source
│   ├── main.py              # entry: plugin loading, signal dispatch, sidebar & page architecture
│   └── settingPage.py       # declarative settings page (auto-generated form + auto-save)
├── docs/
│   ├── zh-CN/               # Chinese documentation
│   └── en-US/               # English documentation
├── Example/
│   ├── Plugin/example/      # example plugin source + example.zip
│   └── Data/example.json    # data-file format sample
├── LICENSE
├── README.md
└── README.zh-CN.md
```

## Runtime Directories

Created automatically on first run of `main.py` (under `.src/`):

```
.src/
├── plugin/          # plugin directory, place *.zip here
├── data/
│   ├── setting.json # global settings
│   └── temp/        # temp directory for atomic writes
└── logs/            # logs (timestamped files + last.log)
```

## Module Responsibilities

| File / Directory | Responsibility                                 |
| ---------------- | ---------------------------------------------- |
| `main.py`        | app entry, plugin loading, signal broadcast, UI assembly |
| `settingPage.py` | declarative settings page: generates a form from config and auto-saves |
| `plugin/`        | holds plugin zips to be loaded                 |
| `data/`          | data files, read/written by plugins via the API |
| `logs/`          | runtime logs                                   |
