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
import yaml
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

    def _ensure_map_base(self, target_dir: str) -> None:
        """Ensure a usable Duckiematrix map base: main.yaml and assets/.

        - Creates main.yaml if missing
        - Copies template assets/ if missing
        """
        try:
            # 1) main.yaml
            main_yaml_path = os.path.join(target_dir, "main.yaml")
            # Always write a minimal, Duckiematrix-compatible main.yaml
            main_yaml_content = (
                "version: 1.0\n"
                "main:\n"
                "  frames: !include \"frames.yaml\"\n"
                "  tiles: !include \"tiles.yaml\"\n"
                "  tile_maps: !include \"tile_maps.yaml\"\n"
            )
            with open(main_yaml_path, "w", encoding="utf-8") as f:
                f.write(main_yaml_content)
            # 2) assets/
            assets_dir = os.path.join(target_dir, "assets")
            if not os.path.isdir(assets_dir):
                # template assets live under dt-gui-tools/maps/empty_map/assets
                template_assets = Path(__file__).resolve().parents[2] / "maps" / "empty_map" / "assets"
                if os.path.isdir(template_assets):
                    shutil.copytree(str(template_assets), assets_dir)
        except Exception as e:
            logging.exception(f"Failed to ensure map base in {target_dir}: {e}")

    # ###### DT_MAPS COMPATIBILITY: runtime file ensures and includes ######
    # Helper to ensure auxiliary YAMLs (vehicles, cameras, signs) and main.yaml includes.
    # Keep until schemas converge; safe to simplify/remove when dt_maps handles this natively.
    def _ensure_vehicle_runtime_files(self, target_dir: str) -> None:
        """If vehicles or traffic signs are present, ensure needed runtime YAMLs exist
        and main.yaml includes vehicles, cameras, and traffic_signs.

        Files copied from template loop map if missing:
        - vehicles.yaml, cameras.yaml, vehicle_dynamics.yaml, wheels.yaml,
          vehicle_tags.yaml, renderer_mode.yaml, renderer_assignments.yaml,
          rendering_configuration.yaml, lights.yaml, time_of_flights.yaml,
          traffic_signs.yaml
        """
        try:
            # detect vehicles/signs layer presence
            dm = self._map_storage.map
            has_vehicles = False
            has_signs = False
            try:
                vehicles_layer = dm.layers.vehicles
                has_vehicles = len(list(vehicles_layer.items())) > 0
            except Exception:
                has_vehicles = False
            try:
                signs_layer = dm.layers.traffic_signs
                has_signs = len(list(signs_layer.items())) > 0
            except Exception:
                has_signs = False
            # also consider existing YAMLs in target_dir
            vehicles_yaml_exists = os.path.isfile(os.path.join(target_dir, "vehicles.yaml"))
            traffic_signs_yaml_exists = os.path.isfile(os.path.join(target_dir, "traffic_signs.yaml"))
            if not has_vehicles and not vehicles_yaml_exists and not has_signs and not traffic_signs_yaml_exists:
                return
            template_dir = Path(__file__).resolve().parents[2] / "maps" / "loop"
            needed = [
                "vehicles.yaml",
                "cameras.yaml",
                "vehicle_dynamics.yaml",
                "wheels.yaml",
                "vehicle_tags.yaml",
                "renderer_mode.yaml",
                "renderer_assignments.yaml",
                "rendering_configuration.yaml",
                "lights.yaml",
                "time_of_flights.yaml",
                "traffic_signs.yaml",
            ]
            for fname in needed:
                dst = os.path.join(target_dir, fname)
                if not os.path.isfile(dst):
                    src = template_dir / fname
                    if os.path.isfile(src):
                        shutil.copyfile(str(src), dst)
                    else:
                        # create minimal file if template missing
                        with open(dst, "w", encoding="utf-8") as f:
                            if fname.endswith("traffic_signs.yaml"):
                                f.write("traffic_signs:\n")
                            elif fname.endswith("vehicles.yaml"):
                                f.write("vehicles:\n")
                            else:
                                f.write("")
            # ensure main.yaml includes vehicles, cameras, traffic_signs
            main_yaml_path = os.path.join(target_dir, "main.yaml")
            if os.path.isfile(main_yaml_path):
                with open(main_yaml_path, "r", encoding="utf-8") as f:
                    content = f.read()
                lines_to_add = []
                if "vehicles: !include \"vehicles.yaml\"" not in content:
                    lines_to_add.append("  vehicles: !include \"vehicles.yaml\"\n")
                if "cameras: !include \"cameras.yaml\"" not in content:
                    lines_to_add.append("  cameras: !include \"cameras.yaml\"\n")
                if "traffic_signs: !include \"traffic_signs.yaml\"" not in content:
                    lines_to_add.append("  traffic_signs: !include \"traffic_signs.yaml\"\n")
                if lines_to_add:
                    if content.endswith("\n"):
                        content += "".join(lines_to_add)
                    else:
                        content += "\n" + "".join(lines_to_add)
                    with open(main_yaml_path, "w", encoding="utf-8") as f:
                        f.write(content)
        except Exception as e:
            logging.exception(f"Failed to ensure vehicle/sign runtime files in {target_dir}: {e}")
    # ###### END DT_MAPS COMPATIBILITY ######

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
                self._ensure_map_base(str(path))
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
        try:
            dm = self._map_storage.map
            save_dir = getattr(dm, "_path", None)
            save_name = getattr(dm, "_name", None)
            logging.info(f"Saving map to disk. name={save_name} dir={save_dir}")
            print(f"[MapEditor] Saving map to disk. name={save_name} dir={save_dir}")
            if save_dir:
                self._ensure_map_base(save_dir)
                self._ensure_vehicle_runtime_files(save_dir)
            self._map_storage.map.to_disk()
            # try:
            #     self._prefix_sign_types(save_dir)
            # except Exception as e:
            #     logging.warning(f"Could not prefix traffic sign types: {e}")
            # Post-process: remove redundant i/j from tiles.yaml on disk
            try:
                self._strip_tile_indices(save_dir)
            except Exception as e:
                logging.warning(f"Could not strip tile indices: {e}")
            logging.info("Map saved successfully")
            print("[MapEditor] Map saved successfully")
        except Exception as e:
            logging.exception("Failed to save map")
            print(f"[MapEditor] Failed to save map: {e}")

    #  Save map as
    def save_map_as_triggered(self, parent: QtWidgets.QWidget) -> bool:
        path = self._qt_api.get_dir(parent, "save")
        self.set_move_mode(False)
        if path:
            try:
                dm = self._map_storage.map
                old_dir = getattr(dm, "_path", None)
                old_name = getattr(dm, "_name", None)
                logging.info(f"Save As selected directory: {path}")
                print(f"[MapEditor] Save As selected directory: {path}")
                change_map_directory(dm, path)
                new_dir = getattr(dm, "_path", None)
                new_name = getattr(dm, "_name", None)
                logging.info(f"Changed map directory name={new_name} old_dir={old_dir} new_dir={new_dir}")
                print(f"[MapEditor] Changed map directory name={new_name} old_dir={old_dir} new_dir={new_dir}")
                if new_dir:
                    self._ensure_map_base(new_dir)
                self.save_map_triggered()
            except Exception as e:
                logging.exception("Failed during Save As operation")
                print(f"[MapEditor] Failed during Save As: {e}")
            return True
        return False

    def _strip_tile_indices(self, directory: str) -> None:
        """Remove i/j from tiles.yaml; indices are implied by tile name.

        Keeps only the minimal fields (e.g., type) for each tile.
        """
        tiles_path = os.path.join(directory, "tiles.yaml")
        if not os.path.isfile(tiles_path):
            return
        with open(tiles_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        tiles = data.get("tiles", {})
        if not isinstance(tiles, dict):
            return
        for tile_name, conf in list(tiles.items()):
            if isinstance(conf, dict):
                conf.pop("i", None)
                conf.pop("j", None)
        with open(tiles_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False)

    # ###### DT_MAPS COMPATIBILITY sign_* mapping for Duckiematrix ######
    # Update traffic_signs types to sign_{type} for Duckiematrix consumption.
    # Not needed if dt_maps accepts sign_* enum names.
    # def _prefix_sign_types(self, directory: str) -> None:
    #     """Update traffic_signs types to sign_{type} for Duckiematrix consumption."""
    #     ts_path = os.path.join(directory, "traffic_signs.yaml")
    #     if not os.path.isfile(ts_path):
    #         return
    #     with open(ts_path, "r", encoding="utf-8") as f:
    #         data = yaml.safe_load(f) or {}
    #     signs = data.get("traffic_signs", {})
    #     if not isinstance(signs, dict):
    #         return
    #     updated = False
    #     for name, conf in list(signs.items()):
    #         if not isinstance(conf, dict):
    #             continue
    #         t = conf.get("type", None)
    #         if isinstance(t, str) and not t.startswith("sign_"):
    #             conf["type"] = f"sign_{t}"
    #             signs[name] = conf
    #             updated = True
    #     if updated:
    #         data["traffic_signs"] = signs
    #         with open(ts_path, "w", encoding="utf-8") as f:
    #             yaml.safe_dump(data, f, sort_keys=False)
    # ###### END DT_MAPS COMPATIBILITY ######

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


