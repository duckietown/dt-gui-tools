from PyQt5 import QtCore
from typing import Dict, Any
from PyQt5.QtWidgets import QDialog, QGroupBox, QDialogButtonBox, QFormLayout, QVBoxLayout, \
    QLineEdit, QLabel, QFrame


class EditObject(QDialog):
    get_info = QtCore.pyqtSignal(object)

    def __init__(self, layer_name: str, name: str, config: Dict[str, Any],
                 frame: Dict[str, Any], is_draggable: bool):
        super(EditObject, self).__init__()
        self.info = {"types": {}}
        self.info_send = {"name": name, "layer_name": layer_name,
                          "new_config": {}, "is_draggable": is_draggable,
                          "frame": {},
                          "is_valid": True,
                          "remove": False
                          }
        self.name = name
        self.is_draggable = is_draggable
        self.info_send["new_config"] = config
        self.info_send["frame"] = frame
        self.setWindowTitle("Edit object")
        self.formGroupBox = QGroupBox(f"Object: {name}")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.addButton("Remove", QDialogButtonBox.ActionRole)
        self.buttonBox.accepted.connect(self.send_info)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.clicked.connect(self.remove_elem)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.formGroupBox)
        main_layout.addWidget(self.buttonBox)
        self.create_form(config, frame)
        self.setLayout(main_layout)

    def remove_elem(self, e):
        if e.text() == "Remove":
            self.info_send["remove"] = True
            self.get_info.emit(self.info_send)
            self.close()

    def send_info(self) -> None:
        try:
            #TODO
            for frame_key in self.info_send["frame"]:
                if frame_key == "relative_to":
                    list_for_edit = [frame_key]
                else:
                    list_for_edit = self.info_send["frame"][frame_key]
                for frame_val in list_for_edit:
                    if isinstance(self.info_send["frame"][frame_key], dict):
                        row_name = f"{frame_key}.{frame_val}"
                        self.info_send["frame"][frame_key][frame_val] = \
                            (self.info["types"][row_name])(self.info[row_name].text())
                    else:
                        self.info_send["frame"][frame_key] = (
                            self.info["types"][frame_key])(
                            self.info[frame_key].text())
            for key in self.info_send["new_config"]:
                self.info_send["new_config"][key] = (self.info["types"][key])(self.info[key].text())
        except ValueError:
            self.info_send["is_valid"] = False
        self.get_info.emit(self.info_send)
        self.close()

    def create_form(self, config: Dict[str, Any], frame: Dict[str, Any]) -> None:
        layout = QFormLayout()
        for key in config:
            # tree level
            edit = QLineEdit(self)
            self.info[key] = edit
            self.info["types"][key] = type(config[key])
            edit.setText(str(config[key]))
            layout.addRow(QLabel(key), edit)
        layout.addWidget(QHLine())
        # TODO
        for frame_key in frame:
            if frame_key == "relative_to":
                list_for_edit = [frame_key]
            else:
                list_for_edit = frame[frame_key]
            for frame_val in list_for_edit:
                edit = QLineEdit(self)
                if not isinstance(frame[frame_key], dict):
                    row_name = frame_key
                    val = frame[frame_key]
                else:
                    row_name = f"{frame_key}.{frame_val}"
                    val = frame[frame_key][frame_val]
                self.info["types"][row_name] = type(val)
                self.info[row_name] = edit
                edit.setText(str(val))
                if not self.is_draggable:
                    edit.setDisabled(True)
                layout.addRow(QLabel(row_name), edit)
        self.formGroupBox.setLayout(layout)


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
