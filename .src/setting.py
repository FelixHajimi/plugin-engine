from PySide6 import QtWidgets, QtCore, QtGui
import typing


def createSettings(
    layout: QtWidgets.QFormLayout, data: dict[str, typing.Any], language: str
):
    for key in data:
        if key.startswith("_"):
            continue

        item = data[key]
        if item["_type"] == "item":
            newItemLayout = QtWidgets.QHBoxLayout()
            newItem = QtWidgets.QWidget()
            newItem.setLayout(newItemLayout)
            if item["_valueType"] == "language":
                newWidget = QtWidgets.QComboBox()
                newWidget.setObjectName(item["_id"])
                newWidget.addItems(item["_valueList"])
                newWidget.setCurrentText(item["_default"])
                newItemLayout.addWidget(newWidget)
            elif item["_valueType"] == "combobox":
                newWidget = QtWidgets.QComboBox()
                newWidget.setObjectName(item["_id"])
                newWidget.addItems(item["_valueList"][language])
                newWidget.setCurrentText(item["_default"][language])
                newItemLayout.addWidget(newWidget)
            elif item["_valueType"] == "checkbox":
                newWidget = QtWidgets.QCheckBox()
                newWidget.setObjectName(item["_id"])
                newWidget.setChecked(item["_default"][language])
                newItemLayout.addWidget(newWidget)
            elif item["_valueType"] == "slider":
                newWidget = QtWidgets.QSlider()
                newWidget.setObjectName(item["_id"])
                newWidget.setOrientation(QtCore.Qt.Orientation.Horizontal)
                newWidget.setMinimum(item["_min"])
                newWidget.setMaximum(item["_max"])
                newWidget.setValue(item["_default"])
                newItemLayout.addWidget(newWidget)
                newSubWidget = QtWidgets.QLabel()
                newSubWidget.setText(
                    item["_prefix"][language]
                    + str(newWidget.value())
                    + item["_suffix"][language]
                    + f"({item["_min"]}-{item["_max"]})"
                )
                newWidget.valueChanged.connect(
                    lambda _, item=item, newWidget=newWidget, newWidgetLabel=newSubWidget: newWidgetLabel.setText(
                        item["_prefix"][language]
                        + str(newWidget.value())
                        + item["_suffix"][language]
                        + f"({item["_min"]}-{item["_max"]})"
                    )
                )
                newItemLayout.addWidget(newSubWidget)
            elif item["_valueType"] == "spinbox":
                newWidget = QtWidgets.QSpinBox()
                newWidget.setObjectName(item["_id"])
                newWidget.setMinimum(item["_min"])
                newWidget.setMaximum(item["_max"])
                newWidget.setValue(item["_default"])
                newItemLayout.addWidget(newWidget)
                newSubWidget = QtWidgets.QLabel()
                newSubWidget.setText(
                    item["_prefix"][language]
                    + str(newWidget.value())
                    + item["_suffix"][language]
                    + f"({item["_min"]}-{item["_max"]})"
                )
                newWidget.valueChanged.connect(
                    lambda _, item=item, newWidget=newWidget, newWidgetLabel=newSubWidget: newWidgetLabel.setText(
                        item["_prefix"][language]
                        + str(newWidget.value())
                        + item["_suffix"][language]
                        + f"({item["_min"]}-{item["_max"]})"
                    )
                )
                newItemLayout.addWidget(newSubWidget)
            elif item["_valueType"] == "lineedit":
                newWidget = QtWidgets.QLineEdit()
                newWidget.setObjectName(item["_id"])
                newWidget.setPlaceholderText(item["_placeholder"][language])
                newWidget.setText(item["_default"][language])
                newItemLayout.addWidget(newWidget)
            elif item["_valueType"] == "filepicker":
                newWidget = QtWidgets.QLineEdit()
                newWidget.setObjectName(item["_id"])
                newWidget.setText(item["_default"])
                newItemLayout.addWidget(newWidget)
                newSubWidget = QtWidgets.QPushButton()
                newSubWidget.setText("...")

                def openDialog(_, item=item, newWidget=newWidget):
                    dialog = QtWidgets.QFileDialog(None, item["_label"][language])
                    dialog.setNameFilter(item["_filter"][language])
                    if dialog.exec():
                        newWidget.setText(dialog.selectedFiles()[0])

                newSubWidget.clicked.connect(openDialog)
                newItemLayout.addWidget(newSubWidget)
            elif item["_valueType"] == "colorpicker":
                newWidget = QtWidgets.QLineEdit()
                newWidget.setObjectName(item["_id"])
                newWidget.setText(item["_default"])
                newItemLayout.addWidget(newWidget)
                newSubWidget = QtWidgets.QPushButton()
                newSubWidget.setStyleSheet(
                    f"border: 1px solid black;background-color: {item["_default"]};"
                )
                newWidget.textChanged.connect(
                    lambda _, newSubWidget=newSubWidget, newWidget=newWidget: (
                        newSubWidget.setStyleSheet(
                            f"border: 1px solid black;background-color: {newWidget.text()};"
                        )
                        if QtGui.QColor(newWidget.text()).isValid()
                        else 0
                    )
                )

                def openDialog(_, newSubWidget=newSubWidget, newWidget=newWidget):
                    dialog = QtWidgets.QColorDialog(None)
                    dialog.setCurrentColor(newWidget.text())
                    if dialog.exec():
                        newWidget.setText(dialog.selectedColor().name())
                        newSubWidget.setStyleSheet(
                            f"border: 1px solid black;background-color:{dialog.selectedColor().name()};"
                        )

                newSubWidget.clicked.connect(openDialog)
                newItemLayout.addWidget(newSubWidget)
            layout.addRow(f"{item["_label"][language]}: ", newItem)
        elif item["_type"] == "group":
            newGroupLayout = QtWidgets.QFormLayout()
            newGroup = QtWidgets.QGroupBox()
            newGroup.setLayout(newGroupLayout)
            newGroup.setTitle(item["_label"][language])
            createSettings(newGroupLayout, item, language)
            layout.addWidget(newGroup)


class Setting(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
/* Global */
QWidget {
    font-family: "Microsoft YaHei", sans-serif;
    font-size: 14px;
    color: #202124;
}
QGroupBox {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    margin-top: 14px;
    padding: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left:12px;
    top: 2px;
    background-color: white;
    padding: 0 6px;
    font-weight: 600;
    font-size:15px;
}
QLabel {
    color: #444444;
}

/* QComboBox */
QComboBox {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 5px 8px;
    min-height: 24px;
    background: #ffffff;
}
QComboBox:hover {
    border-color: #a9b2bc;
}
QComboBox:focus {
    border-color: #3b82f6;
}
QComboBox::drop-down {
    border: none;
    width:22px;
}

/* QCheckBox */
QCheckBox::indicator {
    width:18px;
    height:18px;
    border:1px solid #d1d5db;
    border-radius:4px;
    background:#fff;
}
QCheckBox::indicator:checked {
    background-color:#3b82f6;
    border-color:#3b82f6;
}

/* QSlider */
QSlider::groove:horizontal {
    height: 5px;
    background: #e5e7eb;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    width:14px;
    height:14px;
    margin:-4px 0;
    border-radius:7px;
    background:#3b82f6;
}

/* QSpinBox */
QSpinBox {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding:5px 6px;
    min-height:24px;
}
QSpinBox:hover {
    border-color: #a9b2bc;
}
QSpinBox:focus {
    border-color: #3b82f6;
}

/* QLineEdit */
QLineEdit {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding:5px 7px;
    min-height:24px;
    background:#fff;
}
QLineEdit:hover {
    border-color: #a9b2bc;
}
QLineEdit:focus {
    border-color: #3b82f6;
}

/* QPushButton */
QPushButton{
    border: 1px solid #d1d5db;
    border-radius:6px;
    padding:4px 10px;
    background: #f9fafb;
}
QPushButton:hover{
    background:#f3f4f6;
    border-color:#a9b2bc;
}
""")

        mainLayout = QtWidgets.QFormLayout()
        mainLayout.setContentsMargins(40, 40, 40, 40)
        mainLayout.setSpacing(16)
        language = "English(en-us)"
        data = {
            "_type": "group",
            "General": {
                "_type": "group",
                "_label": {"简体中文(zh-cn)": "常规", "English(en-us)": "General"},
                "Language": {
                    "_type": "item",
                    "_id": "general.language",
                    "_valueType": "language",
                    "_default": "English(en-us)",
                    "_valueList": ["简体中文(zh-cn)", "English(en-us)"],
                    "_label": {"简体中文(zh-cn)": "语言", "English(en-us)": "Language"},
                },
                "Theme": {
                    "_type": "item",
                    "_id": "general.theme",
                    "_valueType": "combobox",
                    "_default": {
                        "English(en-us)": "Follow System",
                        "简体中文(zh-cn)": "跟随系统",
                    },
                    "_valueList": {
                        "简体中文(zh-cn)": ["浅色", "深色", "跟随系统"],
                        "English(en-us)": ["Light", "Dark", "Follow System"],
                    },
                    "_label": {"简体中文(zh-cn)": "主题", "English(en-us)": "Theme"},
                },
            },
        }

        createSettings(mainLayout, data, language)
        self.setLayout(mainLayout)
