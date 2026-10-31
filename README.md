# Plugin Engine

A desktop plugin engine built on PySide6. Turn features into standalone plugins and drop them into the app — no changes to the host program required.

## What It Is

Plugin Engine is a "host + plugin" desktop application framework. The host carries the UI while every feature lives as a plugin that plugs in from a directory. It suits use cases where you want to integrate several small tools or modules into one unified interface.

## Core Features

- **Plugin-based extensibility**: Each feature is an independent plugin package. Drop it into `plugin/` and it is loaded automatically at startup — no need to modify the host program.
- **Plug-and-play UI**: A loaded plugin automatically becomes its own page and appears in the sidebar navigation; click to switch.
- **Host ⇄ plugin communication**: The host sends plugins the language, global settings, and utility methods, and notifies them to initialize their UI; plugins can respond at any time.
- **Plugin data read/write**: Plugins can read and write a unified data-file format for persistence and cross-plugin sharing.
- **Fine-grained permission control**: Each data file can declare which plugins may read and which may write; unauthorized access is rejected outright.
- **Internationalization**: Built-in Chinese and English UI; plugins can register their own language packs that follow the host's language automatically.
- **Declarative settings page**: Declare settings (combo boxes, sliders, color pickers, etc.) in configuration, and the UI is generated and saved automatically — no hand-written widgets.
- **Automatic initialization**: First run creates the plugin, data, and log directories automatically — no manual setup.
- **Built-in logging**: Runtime and error logs are recorded automatically, so problems are traceable.

## Quick Start

```bash
cd .src
pip install PySide6
python main.py
```

The directories are generated on first run. Drop a plugin zip into `plugin/` and it loads.

## Documentation

- [English docs](docs/en-US/)
- [中文文档](docs/zh-CN/)

## License

[MIT License](LICENSE)
