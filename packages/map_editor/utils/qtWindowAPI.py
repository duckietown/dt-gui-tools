from typing import List, Any
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QComboBox, QFormLayout, \
    QLabel


class QtWindowAPI:
    def __init__(self, cur_dir: str):
        self.dir = cur_dir

    def get_dir(self, parent: QtWidgets.QWidget, info: str = "") -> str:
        return QFileDialog.getExistingDirectory(parent, f"Select a folder to {info} the map",
                                                self.dir,
                                                options=QFileDialog.DontUseNativeDialog | QFileDialog.ShowDirsOnly)


def add_combobox(parent, list_items: List[Any], key: str, cur_text: str,
                 layout: QFormLayout, handler=None) -> None:
    parent.info["types"][key] = type(list_items[0])
    combobox = QComboBox()
    combobox.addItems(list(map(str, list_items)))
    combobox.setCurrentText(cur_text)
    parent.info[key] = combobox
    if handler:
        combobox.currentTextChanged.connect(handler)
    parent.comboboxes[key] = combobox
    layout.addRow(QLabel(key), combobox)


def update_combobox(combobox: QComboBox, new_items: List[Any],
                    cur_text: str) -> None:
    combobox.clear()
    combobox.addItems(new_items)
    combobox.setCurrentText(cur_text)
