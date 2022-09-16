import logging
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QMessageBox
from editorState import EditorState
from forms.quit import quit_message_box
from forms.default_forms import form_yes
from forms.start_info import NewMapInfoForm
from forms.edit_object import EditObject
from utils.maps import change_map_directory
from utils.qtWindowAPI import QtWindowAPI
from mapStorage import MapStorage
from mapViewer import MapViewer
from utils.debug import DebugLine
from typing import Dict, Any
from pathlib import Path
import os
import shutil


TILE_TYPES = ('block', 'road')
CTRL = 16777249


class MapAPI:
    """High level API. MapAPI ~ Backend"""
    _qt_api: QtWindowAPI = None
    _map_storage: MapStorage = None
    _map_viewer: MapViewer = None
    _editor_state: EditorState = None
    _debug_line: DebugLine = None

    def __init__(self, info_json: dict, map_viewer: MapViewer, args) -> None:
        self._map_storage = MapStorage()
        self._qt_api = QtWindowAPI(args.wkdir)
        self.info_json = info_json
        self._map_viewer = map_viewer
        self._editor_state = EditorState()
        self.change_obj_info_form = None
        self.init_info_form = NewMapInfoForm(args.wkdir)
        self.init_info_form.send_info.connect(self.create_map_triggered)

    def open_map_triggered(self, parent: QtWidgets.QWidget) -> None:
        path = self._qt_api.get_dir(parent, "open")
        if path:
            self._map_viewer.open_map(Path(path), self._map_storage.map.name)
        self.set_move_mode(False)

    def import_old_format(self):
        print('import old format')

    def create_map_form(self) -> None:
        self.init_info_form.show()
        self.set_move_mode(False)

    #  Open map
    def create_map_triggered(self, info: Dict[str, Any]) -> None:
        path = Path(info["dir_name"])
        if path:
            try:
                if os.path.exists(path):
                    shutil.rmtree(path)
                os.makedirs(path)
                self._map_viewer.create_new_map(info, path)
            except OSError as err:
                logging.error(f"Cannot create path {path} for new map. {err.strerror}")

    def create_region(self):
        print('create_region')

    def change_distortion_view_triggered(self):
        pass

    def save_map_as_png(self, parent: QtWidgets.QWidget) -> None:
        path = self._qt_api.create_file_name(parent)
        self.set_move_mode(False)
        if path:
            self._map_viewer.save_to_png(path)

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

    #  Calculate map characteristics
    def calc_param_triggered(self):
        print('calc_param_triggered')

    #  Help: About
    def about_author_triggered(self):
        print('about_author_triggered')

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

    #  Hide Block menu
    def change_blocks_toggled(self):
        pass

    #  Change button state
    def blocks_event(self, event):
        pass

    #  Hide information menu
    def change_info_toggled(self):
        pass

    #  Change button state
    def info_event(self, event):
        pass

    #  Hide the menu about map properties
    def change_map_toggled(self):
        pass

    #  Change button state
    def map_event(self, event):
        pass

    # Layer window

    def toggle_layer_window(self):
        pass

    def close_layer_window_event(self, event):
        pass

    def layer_tree_clicked(self):
        pass

    def layer_tree_double_clicked(self):
        pass

    def update_layer_tree(self):
        pass

    #  Program exit event
    def quit_program_event(self, event):
        pass

    #  Handle a click on an item from a list to a list
    def item_list_clicked(self):
        pass

    #  Double click initiates as single click action
    def item_list_double_clicked(self, window: QtWidgets.QMainWindow, item_name: str, item_type: str) -> None:
        #print(item_name, item_type)
        if item_name == "separator":
            pass
        elif item_type in TILE_TYPES:
            window.set_default_fill(item_name)
        else:
            type_of_element = self.info_json['info'][item_name]['type']
            try:    
                self._map_viewer.add_obj(type_of_element, item_name)
            except KeyError:
                self.view_info_form("Info", "Functional not implemented")

    def view_info_form(self, header: str, info: str) -> None:
        form_yes(self._map_viewer, header, info)

    #  Reset to default values
    def set_default_fill(self):
        pass

    #  Copy
    def copy_button_clicked(self):
        pass

    #  Cut
    def cut_button_clicked(self):
        pass

    #  Paste
    def insert_button_clicked(self):
        pass

    #  Delete
    def delete_button_clicked(self):
        pass

    #  Undo
    def undo_button_clicked(self):
        pass

    #  Brush mode
    def brush_mode(self, brush_button_is_checked: bool) -> None:
        if brush_button_is_checked:
            self._editor_state.drawState = 'brush'
        else:
            self._editor_state.drawState = ''

    def trimClicked(self):
        pass

    def selection_update(self, default_fill: str) -> None:
        if self._editor_state.drawState == 'brush':
            self._map_viewer.painting_tiles(default_fill)

    def key_press_event(self, event: QKeyEvent) -> None:
        if event.key() == CTRL and not self._editor_state.is_move:
            self.set_move_mode(True)

    def key_release_event(self, event: QKeyEvent) -> None:
        if event.key() == CTRL:
            self.set_move_mode(False)

    def rotate_selected_tiles(self) -> None:
        self._map_viewer.rotate_tiles()

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
        self.change_obj_info_form = EditObject(layer_name, name, obj_conf,
                                               frame, is_draggable)
        self.change_obj_info_form.get_info.connect(self.change_obj_info)
        self.change_obj_info_form.show()

