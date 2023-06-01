from typing import Dict, Any
from PyQt5.QtWidgets import QMessageBox, QFormLayout, QLabel


def form_yes(parent, title, text):
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.Yes)
    box.setDefaultButton(QMessageBox.Yes)
    return box.exec()


def get_info(widget, info: Dict[str, Any]) -> None:
    widget.send_info.emit(info)
    widget.close()


def create_form(widget, rows: Dict[str, Any]) -> QFormLayout:
    layout = QFormLayout()
    for row_name in rows:
        layout.addRow(QLabel(row_name), rows[row_name])
    widget.formGroupBox.setLayout(layout)
    return layout
