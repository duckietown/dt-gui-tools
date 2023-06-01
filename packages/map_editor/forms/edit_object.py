from PyQt5 import QtCore
from typing import Dict, Any, List
from PyQt5.QtWidgets import QDialog, QGroupBox, QDialogButtonBox, QFormLayout, \
    QVBoxLayout, QLineEdit, QLabel, QFrame, QComboBox
from utils.constants import TILES, RELATIVE_TO, FRAME, FORM_DICT, TRAFFIC_SIGNS
from utils.qtWindowAPI import add_combobox, update_combobox


class EditObject(QDialog):
    get_info = QtCore.pyqtSignal(object)
    get_ids = QtCore.pyqtSignal(object)

    def __init__(self, layer_name: str, name: str, config: Dict[str, Any],
                 frame: Dict[str, Any], is_draggable: bool, frames: List[str],
                 map_api):
        super(EditObject, self).__init__()
        self.map_api = map_api
        self.float_formatting = 5
        self.info = {"types": {}}
        self.layer_name = layer_name
        self.info_send = {"name": name, "layer_name": layer_name,
                          "new_config": {}, "is_draggable": is_draggable,
                          FRAME: {},
                          "is_valid": True,
                          "remove": False
                          }
        self.name = name
        self.is_draggable = is_draggable
        self.info_send["new_config"] = config
        self.info_send[FRAME] = frame
        self.frames = frames
        self.setWindowTitle("Edit object")
        self.formGroupBox = QGroupBox(f"Object: {name}")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.addButton("Remove", QDialogButtonBox.ActionRole)
        self.buttonBox.accepted.connect(self.send_info)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.clicked.connect(self.remove_elem)
        self.comboboxes = {}
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
            for frame_key in self.info_send[FRAME]:
                list_for_edit = [frame_key] if frame_key == RELATIVE_TO else self.info_send[FRAME][frame_key]
                for frame_val in list_for_edit:
                    if isinstance(self.info_send[FRAME][frame_key], dict):
                        row_name = f"{frame_key}.{frame_val}"
                        self.info_send[FRAME][frame_key][frame_val] = \
                            (self.info["types"][row_name])(self.info[row_name].text())
                    elif isinstance(self.info[frame_key], QComboBox):
                        self.info_send[FRAME][frame_key] = self.info[frame_key].currentText()
                    else:
                        self.info_send[FRAME][frame_key] = (
                            self.info["types"][frame_key])(
                            self.info[frame_key].text())
            for key in self.info_send["new_config"]:
                if self.info["types"][key] == dict or self.info["types"][key] == list:
                    val = eval(self.info[key].text())
                elif isinstance(self.info[key], QComboBox):
                    val = (self.info["types"][key])(self.info[key].currentText())
                else:
                    val = (self.info["types"][key])(self.info[key].text())
                self.info_send["new_config"][key] = val
        except ValueError:
            self.info_send["is_valid"] = False
        except SyntaxError:
            self.info_send["is_valid"] = False
        self.get_info.emit(self.info_send)
        self.close()

    def create_form(self, config: Dict[str, Any], frame: Dict[str, Any]) -> None:
        layout = QFormLayout()
        for key in config:
            # dropdown lists of types
            if self.layer_name in FORM_DICT and key in FORM_DICT[self.layer_name].keys():
                handler = self.update_ids if self.layer_name == TRAFFIC_SIGNS else None
                add_combobox(self, FORM_DICT[self.layer_name][key], key,
                                  config[key], layout, handler)
            elif key == "id" and self.layer_name == TRAFFIC_SIGNS:
                add_combobox(self, self.get_new_ids(config["type"],
                                                    int(config[key])), key,
                             str(config[key]), layout)
            else:
                # other types
                self.get_qline_edit(key, config[key], layout)
        layout.addWidget(QHLine())
        for frame_key in frame:
            # dropdown lists of objects names
            if frame_key == RELATIVE_TO:
                if self.is_draggable:
                    add_combobox(self, self.frames, frame_key,
                                      frame[frame_key], layout)
                    list_for_edit = []
                else:
                    list_for_edit = [frame_key]
            else:
                list_for_edit = frame[frame_key]
            for frame_val in list_for_edit:
                if not isinstance(frame[frame_key], dict):
                    row_name = frame_key
                    val = frame[frame_key]
                else:
                    row_name = f"{frame_key}.{frame_val}"
                    val = frame[frame_key][frame_val]
                self.get_qline_edit(row_name, val, layout)
        self.formGroupBox.setLayout(layout)

    def get_qline_edit(self, row_name: str, row_val: Any,
                       layout: QFormLayout) -> None:
        edit = QLineEdit(self)
        self.info["types"][row_name] = type(row_val)
        self.info[row_name] = edit
        if isinstance(row_val, float):
            edit.setText(f'{row_val:.{self.float_formatting}f}')
        else:
            edit.setText(str(row_val))
        if self.layer_name == TILES and (row_name == "i" or row_name == "j")\
                or not self.is_draggable:
            edit.setDisabled(True)
        layout.addRow(QLabel(row_name), edit)

    def update_ids(self):
        combobox = self.comboboxes["id"]
        tags_type = self.comboboxes["type"].currentText()
        possible_ids = list(map(str, self.get_new_ids(tags_type)))
        curr_text = str(self.comboboxes["id"].currentText())
        update_combobox(combobox, possible_ids, curr_text)

    def get_new_ids(self, tags_type: str, old_id: int = None) -> List[int]:
        ids = self.map_api.get_possible_ids_by_type(tags_type)
        if old_id and old_id not in ids:
            ids.insert(0, old_id)
        return ids


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
