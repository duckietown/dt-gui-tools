import logging
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QMessageBox
from editorState import EditorState
from forms.image_form import SaveImageForm
from forms.quit import quit_message_box
from forms.default_forms import form_yes
from forms.start_info import NewMapInfoForm
from forms.edit_object import EditObject
from utils.maps import change_map_directory
from utils.qtWindowAPI import QtWindowAPI
from utils.window import get_free_ids_by_type
from mapStorage import MapStorage
from mapViewer import MapViewer
from history import Memento, EditorHistory
from utils.debug import DebugLine
from typing import Dict, Any, List
from pathlib import Path
import os
import shutil
from utils.constants import REQUIRED_LAYERS, TILE_KIND, CTRL, \
    TRAFFIC_SIGNS_TYPES_IDS, VIEW_TILE_HEIGHT


class MapAPI:
    """High level API. MapAPI ~ Backend"""
    _qt_api: QtWindowAPI = None
    _map_storage: MapStorage = None
    _map_viewer: MapViewer = None
    _editor_state: EditorState = None
    _debug_line: DebugLine = None
    _history: EditorHistory = None

    def __init__(self, info_json: dict, map_viewer: MapViewer,
                 args: Dict[str, Any]) -> None:
        self._map_storage = MapStorage()
        self._qt_api = QtWindowAPI(args.wkdir)
        self.info_json = info_json
        self._map_viewer = map_viewer
        self._editor_state = EditorState()
        self._history = EditorHistory()
        self.change_obj_info_form = None
        self.save_map_image_form = None
        self.wkdir = args.wkdir
        self.init_info_form = NewMapInfoForm(args.wkdir)
        self.init_info_form.send_info.connect(self.create_map_triggered)

    def open_map_triggered(self, parent: QtWidgets.QWidget) -> None:
        path = self._qt_api.get_dir(parent, "open")
        if path:
            dir_content = os.listdir(path)
            if len(dir_content):
                status = True
                for file_name in REQUIRED_LAYERS:
                    if file_name not in dir_content:
                        self.view_info_form("Info",
                                            f"Can't open directory, no file {file_name}")
                        status = False
                        break
                if status:
                    self._map_viewer.open_map(Path(path), self._map_storage.map.name)
            else:
                self.view_info_form("Info", "Can't open empty directory")
        self.set_move_mode(False)

    def create_map_form(self) -> None:
        self.init_info_form.show()
        self.set_move_mode(False)

    #  Open map
    def create_map_triggered(self, info: Dict[str, Any]) -> None:
        if info["x"] == "" or info["y"] == "":
            self.view_info_form("Info", "One of the map sizes is not specified")
            return
        if info["tile_width"] == "" or info["tile_height"] == "":
            self.view_info_form("Info", "One of the tile sizes is not specified")
            return
        if info["dir_name"] == "":
            self.view_info_form("Info", "Folder not specified to save the map")
            return
        if info["map_name"] == "":
            self.view_info_form("Info", "Name not specified to save the map")
            return
        path = Path(info["dir_name"])
        if path:
            try:
                if os.path.exists(path):
                    shutil.rmtree(path)
                os.makedirs(path)
                self._map_viewer.create_new_map(info, path)
                self.save_map_triggered()
            except OSError as err:
                logging.error(f"Cannot create path {path} for new map. {err.strerror}")

    def to_the_map_corner(self) -> None:
        self._map_viewer.to_the_corner()

    # Delete
    def delete_selected_objects(self) -> None:
        self._map_viewer.delete_selected_objects()
        self._map_viewer.save_viewer_state()

    def save_image_form(self):
        self.save_map_image_form = SaveImageForm(self._map_viewer.map_height *
                                            VIEW_TILE_HEIGHT)
        self.save_map_image_form.send_info.connect(self.save_map_as_png)
        self.save_map_image_form.show()
        self.set_move_mode(False)

    def save_map_as_png(self,  info: Dict[str, Any]) -> None:
        if info["height"] <= 0:
            self.view_info_form("Info",
                                "Image height value must be non-negative number")
            return
        self.to_the_map_corner()
        self.set_move_mode(False)
        path = info["image_name"]
        path = os.path.join(self.wkdir, path)
        if path:
            self._map_viewer.save_to_png(path, info["height"])
            form_yes(self._map_viewer,
                     "Info", f"Picture was saved in {os.path.abspath(path)}.png")
        else:
            self.view_info_form("Info",
                                "No image name entered! Image can't save.")

    #  Save map
    def save_map_triggered(self) -> None:
        self._map_storage.map.to_disk()

    #  Save map as
    def save_map_as_triggered(self, parent: QtWidgets.QWidget) -> bool:
        path = self._qt_api.get_dir(parent, "save")
        self.set_move_mode(False)
        if path:
            change_map_directory(self._map_storage.map, path)
            self.save_map_triggered()
            return True
        return False

    #  Exit
    def exit_triggered(self, _translate, window: QtWidgets.QMainWindow) -> None:
        if self.save_before_exit(_translate, window):
            QtCore.QCoreApplication.instance().quit()

    # Save map before exit
    def save_before_exit(self, _translate,
                         window: QtWidgets.QMainWindow) -> bool:
        if not self._editor_state.debug_mode:
            ret = quit_message_box(_translate, window)
            self.set_move_mode(False)
            if ret == QMessageBox.Cancel:
                return False
            if ret == QMessageBox.Discard:
                return True
            if ret == QMessageBox.Save:
                return self.save_map_as_triggered(window)
        return True

    def item_list_double_clicked(self,  window: QtWidgets.QMainWindow,
                                 item_name: str, item_type: str) -> None:
        # print(item_name, item_type)
        if item_name == "separator":
            pass
        elif item_type not in TILE_KIND:
            type_of_element = self.info_json['info'][item_name]['type']
            try:
                self._map_viewer.add_obj(type_of_element, item_name)
            except:
                self.view_info_form("Info", "Functional not implemented")

    def item_list_clicked(self, window: QtWidgets.QMainWindow,
                                 item_name: str, item_type: str) -> None:
        if item_name == "separator":
            pass
        elif item_type in TILE_KIND:
            window.set_default_fill(item_name)

    def view_info_form(self, header: str, info: str) -> None:
        form_yes(self._map_viewer, header, info)

    #  Copy
    def copy_button_clicked(self):
        self._map_viewer.copy()

    #  Cut
    def cut_button_clicked(self):
        self._map_viewer.cut_out()

    #  Paste
    def insert_button_clicked(self):
        self._map_viewer.paste()

    #  Undo
    def undo_button_clicked(self) -> None:
        m = self._history.undo()
        if m:
            self._map_viewer.restore_state(m)

    def shift_button_clicked(self) -> None:
        m = self._history.shift_undo()
        if m:
            self._map_viewer.restore_state(m)

    def push_state(self, m: Memento) -> None:
        self._history.push(m)

    def clear_editor_history(self) -> None:
        self._history.clear_history()

    #  Brush mode
    def brush_mode(self, brush_button_is_checked: bool) -> None:
        self._editor_state.drawState = 'brush' if brush_button_is_checked else ''

    def selection_update(self, default_fill: str) -> None:
        if self._editor_state.drawState == 'brush' and \
                self._map_viewer.have_selected_tiles():
            self._map_viewer.painting_tiles(default_fill)
            self._map_viewer.save_viewer_state()

    def key_press_event(self, event: QKeyEvent) -> None:
        if event.key() == CTRL and not self._editor_state.is_move:
            self.set_move_mode(True)

    def mouse_press_event(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.MiddleButton:
            if not self._editor_state.is_move:
                self.set_move_mode(True)
            else:
                self.set_move_mode(False)

    def key_release_event(self, event: QKeyEvent) -> None:
        if event.key() == CTRL:
            self.set_move_mode(False)

    def rotate_selected_objects(self) -> None:
        self._map_viewer.rotate_tiles()
        self._map_viewer.rotate_objects()
        self._map_viewer.save_viewer_state()

    def set_debug_mode(self, debug_line: DebugLine) -> None:
        self._editor_state.debug_mode = True
        self._debug_line = debug_line

    def update_debug_info(self, event: Dict[str, Any]) -> None:
        if self._editor_state.debug_mode:
            if event["mode"] == "set_cursor_pos":
                self._debug_line.set_mouse_pos(event)

    def scene_update(self) -> None:
        self._map_viewer.scene_update()

    def is_move_mode(self) -> bool:
        return self._editor_state.is_move

    def set_move_mode(self, val: bool) -> None:
        self._editor_state.set_move(val)

    def change_obj_info(self, obj_conf: Dict[str, Any]) -> None:
        self._map_viewer.change_obj_from_info(obj_conf)

    def change_obj_form(self, layer_name: str, name: str,
                        obj_conf: Dict[str, Any], frame: Dict[str, Any],
                        is_draggable: bool) -> None:
        possible_relative_objects = self._map_viewer.get_possible_relative_objects(name)
        self.change_obj_info_form = EditObject(layer_name, name, obj_conf,
                                               frame, is_draggable,
                                               possible_relative_objects, self)
        self.change_obj_info_form.get_info.connect(self.change_obj_info)
        self.change_obj_info_form.show()

    def get_possible_ids_by_type(self, type_name: str) -> List[int]:
        exist_ids = self._map_viewer.get_ids_by_type(type_name)
        all_ids = TRAFFIC_SIGNS_TYPES_IDS[type_name]
        poss_ids = get_free_ids_by_type(exist_ids, all_ids)
        if len(poss_ids):
            return poss_ids
        else:
            return [all_ids[-1]]


