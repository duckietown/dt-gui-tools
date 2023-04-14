# -*- coding: utf-8 -*-
from copy import deepcopy
from importlib import import_module
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect, QPoint, Qt
from PyQt5.QtGui import QKeyEvent
from dt_maps.types.tiles import Tile, Frame
from dt_maps import MapLayer
from classes.Commands.AddObjCommand import AddObjCommand
from classes.Commands.AddRelativeToObj import AddRelativeToObj
from classes.Commands.DeepCopyLayerCommand import DeepCopyLayerCommand
from classes.Commands.DeleteObjCommand import DeleteObjCommand
from classes.Commands.GetLayerCommand import GetLayerCommand
from classes.Commands.SetTileSizeCommand import SetTileSizeCommand
from classes.Commands.GetDefaultLayerConf import GetDefaultLayerConf
from classes.Commands.ChangeObjCommand import ChangeObjCommand
from classes.Commands.CheckConfigCommand import CheckConfigCommand
from classes.Commands.MoveObjCommand import MoveObjCommand
from classes.Commands.RotateObjCommand import RotateCommand
from classes.Commands.ChangeTypeCommand import ChangeTypeCommand
from classes.Commands.MoveTileCommand import MoveTileCommand
from classes.Commands.ChangeIDCommand import ChangeIDCommand
from classes.layers import BasicLayerHandler, DynamicLayer
from classes.map_objects import DraggableImage, ImageObject
from classes.MapDescription import MapDescription
from typing import Dict, Any, Optional, Union, Tuple, List
from coordinatesTransformer import CoordinatesTransformer
from history import Memento
from buffer import Buffer
from painter import Painter
from utils.maps import default_map_storage, get_map_height, get_map_width, \
    change_map_name, convert_layer_name_to_class_name
from utils.constants import LAYERS_WITH_TYPES, OBJECTS_TYPES, FRAMES, FRAME, \
    TILES, TILE_MAPS, TILE_SIZE, NOT_DRAGGABLE, LAYER_NAME, NEW_CONFIG, \
    KNOWN_LAYERS, WATCHTOWERS, VEHICLES, TRAFFIC_SIGNS
from utils.window import get_id_by_type
from pathlib import Path
from dt_maps.Map import REGISTER
from frameTree import FrameTreeStorage


def needsavestate(func):
    def save(*args, **kwargs):
        func(*args, **kwargs)
        self = args[0]
        m = self.save_state()
        self.parentWidget().parent().push_state(m)

    return save


class MapViewer(QtWidgets.QGraphicsView, QtWidgets.QWidget):
    map = None
    map_height = 10
    objects = {}
    handlers = None
    scale = 1
    tile_selection = [0] * 4
    lmbPressed = False
    mouse_start_x, mouse_start_y = 0, 0
    mouse_cur_x, mouse_cur_y = 0, 0
    offset_x = 0
    offset_y = 0
    is_to_png = False
    tile_width: float = 0.585
    tile_height: float = 0.585
    grid_scale: float = 100
    grid_height: float = tile_height * grid_scale
    grid_width: float = tile_width * grid_scale
    tile_map: str = "map_1"
    buffer: Buffer = None

    def __init__(self, work_dir: str) -> None:
        QtWidgets.QGraphicsView.__init__(self)
        self.setScene(QtWidgets.QGraphicsScene())
        # load default map
        self.map = default_map_storage(f"{work_dir}/maps/empty_map")
        self.map_frame_tree = FrameTreeStorage()
        self.init_handlers()
        self.set_map_viewer_sizes()
        self.coordinates_transformer = CoordinatesTransformer(self.scale,
                                                              self.map_height,
                                                              self.grid_width,
                                                              self.grid_height,
                                                              self.tile_width,
                                                              self.tile_height)
        self.painter = Painter()
        self.init_all_map_objects()
        self.set_map_size()
        self.setMouseTracking(True)
        self.buffer = Buffer()

    def init_all_map_objects(self) -> None:
        frames = self.get_layer("frames")
        for layer_name in REGISTER:
            layer = self.get_layer(layer_name)
            if layer and layer_name != "frames":
                for object_name in layer:
                    layer_object = layer[object_name]
                    if object_name not in frames:
                        self.add_frame_on_map(object_name)
                    self.add_obj_image(layer_name, object_name, layer_object)

    def init_handlers(self) -> None:
        # import handlers for module layers
        handlers_list = []
        module = import_module("layers")
        register_layers = REGISTER.keys()
        layers_names = list(self.map.map.layers.__dict__.keys())
        for key in register_layers:
            if key not in layers_names:
                layers_names.append(key)
        for layer_name in layers_names:
            if layer_name in KNOWN_LAYERS:
                # dynamically import handlers for known layers
                class_name = convert_layer_name_to_class_name(layer_name)
                handler_layer_name = f"{class_name}LayerHandler"
                attribute = getattr(module, handler_layer_name)
                handlers_list.append(
                    attribute(layer_name=layer_name))
            else:
                # get unknown layer config from .yaml
                try:
                    keys = list(self.map.map.layers[layer_name].keys())
                except KeyError:
                    continue
                conf = {}
                if len(keys) > 0:
                    # set default conf with empty values
                    conf = deepcopy(self.map.map.layers[layer_name][keys[0]])
                # create dynamic layer
                dynamic_layer = DynamicLayer(conf=conf,
                                             layer_name=layer_name,
                                             map=self.map.map)
                # register new dynamic layer in map.layers
                REGISTER[layer_name] = dynamic_layer
                # added basic layer handler
                handler = BasicLayerHandler(default_conf=conf,
                                            layer_name=layer_name)
                handlers_list.append(handler)
        for i in range(len(handlers_list) - 1):
            handlers_list[i].set_next(handlers_list[i + 1])
        self.handlers = handlers_list[0]

    @needsavestate
    def save_viewer_state(self) -> None:
        pass

    def set_map_viewer_sizes(self, tile_width: float = 0,
                             tile_height: float = 0) -> None:
        if not (tile_width and tile_height):
            try:
                tile_map_obj = self.get_layer(TILE_MAPS)[self.tile_map]
                self.set_tile_size(tile_map_obj[TILE_SIZE]['x'],
                                   tile_map_obj[TILE_SIZE]['y'])
            except TypeError:
                pass
        else:
            self.set_tile_size(tile_width, tile_height)
        self.grid_width = self.tile_width * self.grid_scale
        self.grid_height = self.tile_height * self.grid_scale

    def set_tile_map(self) -> None:
        tile_maps = self.get_layer(TILE_MAPS)
        self.tile_map = [elem for elem in tile_maps][0]

    def set_relative_to(self, object_name: str, value: str) -> None:
        self.handlers.handle(
            command=AddRelativeToObj(object_name, value))

    def get_ids_by_type(self, type_name: str) -> List[int]:
        return [sign.id for sign in self.get_layer(TRAFFIC_SIGNS).values() if (sign.type.value == type_name)]

    def set_object_id(self, layer_name: str, object_name: str, obj_id: int, obj_type: str) -> None:
        if layer_name in (WATCHTOWERS, VEHICLES):
            obj_id = str(obj_id)
        elif layer_name == TRAFFIC_SIGNS:
            traffic_signs_ids = [sign.id for sign in self.get_layer(TRAFFIC_SIGNS).values()]
            new_id = get_id_by_type(obj_type, traffic_signs_ids)
            obj_id = new_id if new_id else obj_id
        self.handlers.handle(
            command=ChangeIDCommand(layer_name, object_name, obj_id))

    @needsavestate
    def add_obj(self, type_of_element: str, item_name: str = None) -> None:
        layer_name = f"{type_of_element}s"
        object_name, obj_id = self.generate_object_name_and_id(self.tile_map, layer_name)
        self.add_obj_on_map(layer_name, object_name)
        self.set_relative_to(object_name, self.tile_map)
        self.set_object_id(layer_name, object_name, obj_id, item_name)
        self.add_obj_image(layer_name, object_name, item_name=item_name)
        self.scaled_obj(self.get_image_object(object_name),
                        {'scale': self.scale})

    def generate_object_name_and_id(self, map_name: str, layer_name: str) -> Tuple[str, int]:
        i = 1
        while True:
            object_name: str = f"{map_name}/{layer_name[:-1]}{i}"
            if object_name not in self.objects:
                break
            i += 1
        return object_name, i

    def add_obj_image(self, layer_name: str, object_name: str,
                      layer_object=None, item_name: str = None) -> None:
        new_obj = None
        img_name = layer_name
        if layer_name in self.map.map.layers and layer_name not in KNOWN_LAYERS:
            new_obj = DraggableImage(f"./img/objects/unknown.png", self,
                                     object_name, layer_name)
        elif layer_name in LAYERS_WITH_TYPES and layer_object:
            img_name = layer_object.type.value
        elif item_name:
            img_name = item_name
        if layer_name in NOT_DRAGGABLE:
            new_obj = ImageObject(
                f"./img/{layer_name}/{img_name}.png", self,
                object_name, layer_name, (self.grid_width, self.grid_height))
        elif layer_name in LAYERS_WITH_TYPES:
            new_obj = DraggableImage(f"./img/{layer_name}/{img_name}.png", self,
                                     object_name, layer_name)
        elif layer_name in OBJECTS_TYPES:
            new_obj = DraggableImage(f"./img/objects/{img_name}.png", self,
                                     object_name, layer_name)
        if new_obj:
            frame_obj = self.get_frame_object(object_name)
            self.rotate_obj(new_obj, frame_obj.pose.yaw)
            coordinates = self.get_final_pos(object_name,
                                                 frame_obj.pose.x,
                                                 frame_obj.pose.y)
            view_coordinates = (
                self.get_x_to_view(coordinates[0], new_obj.width()),
                self.get_y_to_view(coordinates[1]), new_obj.height()
            )
            self.move_obj(new_obj, {"new_coordinates": view_coordinates})
            self.objects[object_name] = new_obj
            if new_obj.layer_name in LAYERS_WITH_TYPES:
                self.handlers.handle(ChangeTypeCommand(new_obj.layer_name,
                                                       object_name, img_name))
            self.map_frame_tree.tree.add(object_name, frame_obj.relative_to)
        self.change_object_handler(self.scaled_obj, {"scale": self.scale})

    def get_final_pos(self, frame_name: str, x: float, y: float) -> Tuple[float, float]:
        frames = self.get_layer("frames")
        frame_obj = frames[frame_name]
        while frame_obj.relative_to != self.tile_map:
            frame_obj = frames[frame_obj.relative_to]
            x += frame_obj.pose.x
            y += frame_obj.pose.y
        return x, y

    def get_relative_map_pos(self, frame_name: str,
                             new_qt_pos: Tuple[float, float],
                             obj_width: float = 0,
                             obj_height: float = 0) -> Tuple[float, float]:
        map_obj = self.get_layer(FRAMES)[frame_name]
        real_pose = self.get_final_pos(frame_name, map_obj["pose"]["x"],
                                       map_obj["pose"]["y"])
        diff_x = self.get_x_from_view(new_qt_pos[0], obj_width=obj_width,
                                      offset=self.offset_x) - real_pose[0]
        diff_y = self.get_y_from_view(new_qt_pos[1], obj_height=obj_height,
                                      offset=self.offset_y) - real_pose[1]
        map_x = map_obj["pose"]["x"] + diff_x
        map_y = map_obj["pose"]["y"] + diff_y
        return map_x, map_y

    def add_obj_on_map(self, layer_name: str, object_name: str) -> None:
        self.add_frame_on_map(object_name)
        self.handlers.handle(command=AddObjCommand(layer_name, object_name))

    def add_frame_on_map(self, frame_name: str) -> None:
        self.handlers.handle(command=AddObjCommand(FRAMES, frame_name))

    def delete_obj_on_map(self, obj: ImageObject) -> None:
        self.handlers.handle(command=DeleteObjCommand(FRAMES, obj.name))
        self.handlers.handle(command=DeleteObjCommand(obj.layer_name,
                                                      obj.name))

    def move_tile(self, tile_name: str, tile_id: Tuple[int, int]) -> None:
        self.handlers.handle(MoveTileCommand(tile_name, tile_id))

    def set_tile_size_command(self, tile_map: str,
                              tile_size: Tuple[float, float]) -> None:
        self.handlers.handle(SetTileSizeCommand(tile_map, tile_size))

    def delete_objects(self) -> None:
        for obj_name in self.objects:
            obj = self.get_image_object(obj_name)
            obj.delete_object()
        self.objects.clear()
        self.map_frame_tree.tree.clear_graph()

    def move_obj(self, obj: ImageObject, args: Dict[str, Any]) -> None:
        if "new_coordinates" in args:
            new_coordinates = args["new_coordinates"]
            obj.move_object(new_coordinates)
        elif "delta_coordinates" in args:
            delta_coord = args["delta_coordinates"]
            obj.move_object((obj.pos().x() + delta_coord[0],
                             obj.pos().y() + delta_coord[1]))

    @needsavestate
    def move_obj_on_map(self, frame_name: str,
                        new_pos: Tuple[float, float],
                        obj_width: float = 0,
                        obj_height: float = 0) -> None:
        predecessor = self.map_frame_tree.tree.predecessor(frame_name)
        if predecessor == self.tile_map:  # not relative object
            map_x = self.get_x_from_view(new_pos[0], obj_width=obj_width,
                                         offset=self.offset_x)
            map_y = self.get_y_from_view(new_pos[1], obj_height=obj_height,
                                         offset=self.offset_y)
        else:  # relative object
            map_x, map_y = self.get_relative_map_pos(frame_name, new_pos,
                                                     obj_width, obj_height)
        self.move_obj_command(frame_name, (map_x, map_y))

    def move_selected_objects(self, qt_offset_x: float, qt_offset_y: float) -> None:
        obj_for_move = set()
        sel_objects = self.get_selected_objects()
        for obj in sel_objects:
            successors = self.map_frame_tree.tree.all_successors(obj.name)
            successors.append(obj.name)
            obj_for_move.update(successors)
        for successor_name in obj_for_move:
            successor = self.get_image_object(successor_name)
            successor.change_position((successor.pos().x() + qt_offset_x,
                                       successor.pos().y() + qt_offset_y))

    @needsavestate
    def move_selected_objects_on_map(self, diff_pos) -> None:
        obj_for_move = []
        for_move = set([obj.name for obj in self.get_selected_objects()])
        successors = set()
        for name in for_move:
            successors.update(self.map_frame_tree.tree.all_successors(name))
        for name in for_move:
            if name not in successors:
                obj_for_move.append(name)
        for successor_name in obj_for_move:
            diff_x = -self.get_x_from_view(diff_pos.x())
            diff_y = -self.get_y_from_view(diff_pos.y() + self.map_height * (self.grid_height + 1) * self.scale)
            frame = self.get_frame_object(successor_name)
            map_x = frame["pose"]["x"] + diff_x
            map_y = frame["pose"]["y"] + diff_y
            self.move_obj_command(successor_name, (map_x, map_y))

    def get_possible_relative_objects(self, frame_name: str) -> List[str]:
        objects = self.objects if self.get_image_object(frame_name).is_draggable else None
        relative_objects = [self.tile_map]
        successors = set(self.map_frame_tree.tree.all_successors(frame_name))
        if objects:
            for name in objects:
                if objects[name].is_draggable() and name != frame_name and \
                        name not in successors:
                    relative_objects.append(name)
        return relative_objects

    def move_obj_command(self, frame_name: str,
                         new_coord: Tuple[float, float]) -> None:
        self.handlers.handle(command=MoveObjCommand(frame_name, new_coord))

    def get_layer_deepcopy(self, layer_name: str) -> Dict[str, Any]:
        return self.handlers.handle(command=DeepCopyLayerCommand(layer_name))

    def rotate_obj(self, obj: ImageObject, new_angle: float) -> None:
        obj.rotate_object(new_angle)
        self.scene_update()

    def rotate_obj_on_map(self, frame_name: str, new_angle: float) -> None:
        self.handlers.handle(command=RotateCommand(frame_name, new_angle))

    def scaled_obj(self, obj: ImageObject, args: Dict[str, Any]) -> None:
        scale = args["scale"]
        obj.scale_object(scale)
        obj_width = obj.width() if obj.is_draggable() else 0
        obj_height = obj.height() if obj.is_draggable() else 0
        frame_obj_coord = self.get_frame_object(obj.name)["pose"]
        view_coord = self.get_final_pos(obj.name, frame_obj_coord["x"], frame_obj_coord["y"])
        new_coordinates = (
            self.get_x_to_view(
                view_coord[0], obj_width) + self.offset_x,
            self.get_y_to_view(
                view_coord[1], obj_height) + self.offset_y)
        self.move_obj(obj, {"new_coordinates": new_coordinates})

    def set_png_mode(self, obj: ImageObject, args: Dict[str, Any]) -> None:
        mode = args["mode"]
        obj.set_is_to_png(mode)

    def set_map_size(self, height: int = 0) -> None:
        self.map_height = height if height else get_map_height(self.get_layer(TILES))
        self.coordinates_transformer.set_size_map(self.map_height)

    def rotate_with_button(self, args: Dict[str, Any]) -> None:
        tile_name = args["tile_name"]
        obj = self.get_image_object(tile_name)
        self.rotate_obj(obj, obj.yaw + 90)
        self.rotate_obj_on_map(tile_name, obj.yaw)

    def is_selected_tile(self, tile: Tile, is_dict: bool = False) -> bool:
        tile_i, tile_j = (tile["i"], tile["j"]) if is_dict else (tile.i, tile.j)
        return ((tile_i + 1) * self.tile_width >= self.tile_selection[0] and
                tile_i * self.tile_width <= self.tile_selection[2] and
                (tile_j + 1) * self.tile_height >= self.tile_selection[3] and
                tile_j * self.tile_height <= self.tile_selection[1])

    def get_x_to_view(self, x: float, obj_width: float = 0) -> float:
        return self.coordinates_transformer.get_x_to_view(x, obj_width)

    def get_y_to_view(self, y: float, obj_height: float = 0) -> float:
        return self.coordinates_transformer.get_y_to_view(y, obj_height)

    def get_x_from_view(self, x: float, obj_width: float = 0, offset: float = 0) -> float:
        return self.coordinates_transformer.get_x_from_view(x,
                                                            obj_width=obj_width,
                                                            offset_x=offset)

    def get_y_from_view(self, y: float, obj_height: float = 0, offset: float = 0) -> float:
        return self.coordinates_transformer.get_y_from_view(y,
                                                            obj_height=obj_height,
                                                            offset_y=offset)

    def get_layer(self, layer_name: str) -> Optional[MapLayer]:
        return self.handlers.handle(command=GetLayerCommand(layer_name))

    def get_image_object(self, obj_name: str) -> Optional[ImageObject]:
        return self.objects.get(obj_name)

    def get_frame_object(self, frame_name: str) -> Frame:
        return self.get_layer(FRAMES)[frame_name]

    def get_default_layer_conf(self, layer_name: str) -> Dict[str, Any]:
        return self.handlers.handle(GetDefaultLayerConf(layer_name))

    def get_object_conf(self, layer_name: str, name: str) -> Dict[str, Any]:
        layer = self.get_layer(layer_name).copy()
        obj = layer[name]
        default_layer_conf = self.get_default_layer_conf(layer_name).copy()
        if not default_layer_conf:
            default_layer_conf = {}
        for key in default_layer_conf:
            try:
                default_layer_conf[key] = obj[key].value
            except AttributeError:
                default_layer_conf[key] = obj[key]
        return default_layer_conf

    def change_obj_info(self, layer_name: str, obj_name: str) -> None:
        obj = self.get_image_object(obj_name)
        self.parentWidget().parent().change_obj_info(layer_name, obj_name,
                                                     self.get_object_conf(layer_name, obj_name),
                                                     self.get_object_conf(FRAMES, obj.name), obj.is_draggable())

    @needsavestate
    def change_obj_from_info(self, conf: Dict[str, Any]) -> None:
        print(conf)
        obj = self.get_image_object(conf["name"])
        if conf["is_valid"]:
            if conf["remove"]:
                self.delete_object(obj)
            else:
                if self.check_layer_config(FRAMES,
                                           conf[FRAME]):
                    self.change_obj_from_config(FRAMES,
                                                conf["name"],
                                                conf[FRAME])
                    # rotate object
                    obj.rotate_object(conf[FRAME]["pose"]["yaw"])
                    self.handlers.handle(RotateCommand(conf["name"],
                                                       conf[FRAME]["pose"][
                                                           "yaw"]))
                    if conf["is_draggable"]:
                        # move obj on window
                        pos_x = self.get_x_to_view(
                            conf[FRAME]["pose"]["x"],
                            obj.width()) + self.offset_x
                        pos_y = self.get_y_to_view(
                            conf[FRAME]["pose"]["y"],
                            obj.height()) + self.offset_y
                        self.move_obj(obj, {"new_coordinates": (pos_x, pos_y)})
                        # move obj on map
                        map_x = self.get_x_from_view((pos_x, pos_y)[0],
                                                     obj_width=obj.width(),
                                                     offset=self.offset_x)
                        map_y = self.get_y_from_view((pos_x, pos_y)[1],
                                                     obj_height=obj.height(),
                                                     offset=self.offset_y)
                        self.move_obj_command(conf["name"], (map_x, map_y))
                else:
                    self.parentWidget().parent().view_info_form("Error",
                                                                "Invalid object frame values entered!")
                # check correct values
                if self.check_layer_config(conf[LAYER_NAME], conf[NEW_CONFIG]):
                    self.change_obj_from_config(conf[LAYER_NAME],
                                                conf["name"],
                                                conf[NEW_CONFIG])
                    self.objects.__delitem__(obj.name)
                    obj.delete_object()
                    layer = self.get_layer(conf[LAYER_NAME])
                    self.add_obj_image(conf[LAYER_NAME], conf["name"], layer[conf["name"]])
                else:
                    self.parentWidget().parent().view_info_form("Error",
                                                                "Invalid object configuration entered!")
        else:
            self.parentWidget().parent().view_info_form("Error",
                                                        "Invalid values entered!")

    def check_layer_config(self, layer_name: str, new_config: Dict[str, Any]) -> bool:
        return self.handlers.handle(CheckConfigCommand(layer_name, new_config))

    def change_obj_from_config(self, layer_name: str, obj_name: str,
                               new_config: Dict[str, Any]) -> None:
        self.handlers.handle(ChangeObjCommand(layer_name, obj_name,
                                              new_config))

    def delete_object(self, obj: ImageObject) -> None:
        successors = set(self.map_frame_tree.tree.all_successors(obj.name))
        frames = self.get_layer(FRAMES)
        neighbors = []
        for successor in successors:
            if frames[successor].relative_to == obj.name:
                neighbors.append(successor)
        self.map_frame_tree.tree.remove_node(obj.name)
        for neighbour_name in neighbors:
            neighbor_coord = self.get_frame_object(neighbour_name)["pose"]
            abs_coordinates = self.get_final_pos(neighbour_name,
                                                 neighbor_coord["x"],
                                                 neighbor_coord["y"])
            self.move_obj_command(neighbour_name, abs_coordinates)
            self.set_relative_to(neighbour_name, self.tile_map)
            self.map_frame_tree.tree.add(neighbour_name, self.tile_map)
        self.delete_obj_on_map(obj)
        self.objects.__delitem__(obj.name)
        obj.delete_object()

    def change_tiles_handler(self, handler_func, args: Dict[str, Any]) -> None:
        tiles = self.get_layer(TILES)
        for tile_name in tiles:
            tile = tiles[tile_name]
            if self.is_selected_tile(tile):
                args["tile_name"] = tile_name
                args["tile"] = tile
                handler_func(args)

    def change_object_handler(self, handler_func, args: Dict[str, Any]) -> None:
        for obj_name in self.objects:
            handler_func(self.get_image_object(obj_name), args)

    def painting_tiles(self, default_fill: str) -> None:
        self.change_tiles_handler(self.change_tile_type,
                                  {"default_fill": default_fill})

    def rotate_tiles(self) -> None:
        self.change_tiles_handler(self.rotate_with_button, {})
        
    def rotate_object_with_button(self, obj: ImageObject,
                                  args: Dict[str, Any]) -> None:
        if obj.is_draggable() and obj.is_select:
            new_angle = obj.yaw + 90
            self.rotate_obj(obj, new_angle)
            self.rotate_obj_on_map(obj.name, new_angle)

    def rotate_objects(self) -> None:
        self.change_object_handler(self.rotate_object_with_button, {})

    def highlight_select_tile(self, args: Dict[str, Any]) -> None:
        tile = self.get_image_object(args["tile_name"])
        self.painter.draw_rect((tile.pos().x() - 1, tile.pos().y() - 1),
                               self.scale, args["painter"],
                               self.grid_width, self.grid_height)

    def change_tile_type(self, args: Dict[str, Any]) -> None:
        new_tile_type = args["default_fill"]
        tile_name = args["tile_name"]
        img_path = f"./img/tiles/{new_tile_type}.png"
        mutable_obj = self.get_image_object(tile_name)
        if mutable_obj:
            mutable_obj.change_image(img_path)
        self.handlers.handle(command=ChangeTypeCommand(TILES, tile_name,
                                                       new_tile_type))
        self.rotate_obj_on_map(tile_name, 0)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        sf = 1.5 ** (event.angleDelta().y() / 240)
        if self.scale * sf < 0.1:
            return
        elif self.scale * sf > 5:
            return
        else:
            self.scale *= sf
        self.coordinates_transformer.set_scale(self.scale)
        self.set_offset()
        self.change_object_handler(self.scaled_obj, {"scale": self.scale})
        self.scene_update()

    def scene_update(self) -> None:
        self.scene().update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self.parentWidget().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        self.parentWidget().keyReleaseEvent(event)

    def is_move_mode(self) -> bool:
        return self.parentWidget().parent().is_move_mode()

    def move_map(self, x: float, y: float) -> None:
        delta_pos = (x - self.mouse_cur_x, y - self.mouse_cur_y)
        self.change_object_handler(self.move_obj,
                                   {"delta_coordinates": delta_pos})

    def to_the_corner(self) -> None:
        left_upper_tile = self.get_image_object(
            f"{self.tile_map}/tile_0_{self.map_height - 1}")
        delta_pos = (-left_upper_tile.pos().x() + 2,
                     -left_upper_tile.pos().y() + 2)
        self.change_object_handler(self.move_obj,
                                   {"delta_coordinates": delta_pos})
        self.set_offset()

    def get_event_coordinates(self, event: Union[Tuple[float, float], QtGui.QMouseEvent]) -> \
            [float, float, QtGui.QMouseEvent]:
        if isinstance(event, tuple):
            start_pos = event[1]
            event = event[0]
            x, y = event.x() + start_pos[0], event.y() + start_pos[1]
        else:
            x, y = event.x(), event.y()
        return x, y, event

    def mousePressEvent(self, event: Union[Tuple[float, float],
                                           QtGui.QMouseEvent]) -> None:
        # cursor on object
        x, y, event = self.get_event_coordinates(event)
        if event.buttons() == QtCore.Qt.LeftButton or event.buttons() == QtCore.Qt.MiddleButton:
            self.lmbPressed = True
            self.set_offset()
            self.mouse_cur_x = self.mouse_start_x = x
            self.mouse_cur_y = self.mouse_start_y = y
            self.parentWidget().mousePressEvent(event)

    def mouseMoveEvent(self, event: Union[Tuple[float, float],
                                          QtGui.QMouseEvent]) -> None:
        # cursor on object
        x, y, event = self.get_event_coordinates(event)
        if self.lmbPressed:
            if self.is_move_mode():
                self.move_map(x, y)
            else:
                self.select_tiles()
        self.scene_update()
        self.set_offset()
        self.mouse_cur_x = x
        self.mouse_cur_y = y
        self.update_debug_info((self.mouse_cur_x, self.mouse_cur_y))

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if not self.is_move_mode():
            self.lmbPressed = False
        if event.button() == QtCore.Qt.LeftButton or event.buttons() == QtCore.Qt.MiddleButton:
            self.set_offset()
            if not self.is_move_mode():
                self.select_tiles()
                self.select_objects()
                self.parentWidget().parent().selectionUpdate()
            self.scene_update()
            self.parentWidget().mousePressEvent(event)

    def set_offset(self) -> None:
        left_upper_tile = self.get_image_object(f"{self.tile_map}/tile_0_{self.map_height - 1}")
        self.offset_x = left_upper_tile.pos().x()
        self.offset_y = left_upper_tile.pos().y()

    def update_debug_info(self, pos: Tuple[float, float]) -> None:
        map_pos = (
            self.get_x_from_view(pos[0], offset=self.offset_x),
            self.get_y_from_view(pos[1], offset=self.offset_y)
        )
        self.parentWidget().parent().update_debug_info(
            {"mode": "set_cursor_pos", "pos": pos, "map_pose": map_pos})

    def drawBackground(self, painter: QtGui.QPainter,
                       rect: QtCore.QRectF) -> None:
        self.painter.fill_background(painter, 'Gray', self.size().width(),
                                     self.size().height())
        if not self.is_to_png:
            self.change_tiles_handler(self.highlight_select_tile,
                                      {"painter": painter})
        self.scene_update()

    def get_raw_selection(self) -> [float, float, float, float]:
        return [self.get_x_from_view(
            min(self.mouse_start_x, self.mouse_cur_x), offset=self.offset_x),
            self.get_y_from_view(
                min(self.mouse_start_y, self.mouse_cur_y), offset=self.offset_y),
            self.get_x_from_view(
                max(self.mouse_start_x, self.mouse_cur_x), offset=self.offset_x),
            self.get_y_from_view(
                max(self.mouse_start_y, self.mouse_cur_y), offset=self.offset_y),
        ]

    def select_tiles(self) -> None:
        raw_selection = self.get_raw_selection()
        if self.get_layer(TILES):
            self.tile_selection = [
                v
                for i, v in enumerate(raw_selection)
            ]

    def have_selected_tiles(self) -> bool:
        tiles = self.get_layer(TILES)
        for tile_name in tiles:
            tile = tiles[tile_name]
            if self.is_selected_tile(tile):
                return True
        return False

    def select_objects(self) -> None:
        raw_selection = [
            min(self.mouse_start_x, self.mouse_cur_x),
            min(self.mouse_start_y, self.mouse_cur_y),
            max(self.mouse_start_x, self.mouse_cur_x),
            max(self.mouse_start_y, self.mouse_cur_y)
        ]
        for map_object in self.objects:
            map_object = self.objects[map_object]
            map_object.is_select = False
            if map_object.is_draggable() and raw_selection[0] <= map_object.x() <= raw_selection[2] and \
                    raw_selection[1] <= map_object.y() <= raw_selection[3]:
                map_object.is_select = True

    def get_selected_objects(self) -> List[ImageObject]:
        objects = []
        for map_object in self.objects:
            map_object = self.objects[map_object]
            if map_object.is_draggable() and map_object.is_select:
                objects.append(map_object)
        return objects

    def delete_selected_objects(self) -> None:
        delete_list = self.get_selected_objects()
        for obj in delete_list:
            self.delete_object(obj)

    def save_to_png(self, file_name: str, height: int) -> None:
        # add smoothing and scaling of objects
        temp_scale = height / ((self.grid_height + 1) * get_map_height(self.get_layer(TILES)))
        self.coordinates_transformer.set_scale(temp_scale)
        self.change_object_handler(self.set_png_mode, {"mode": True})
        self.change_object_handler(self.scaled_obj, {"scale": temp_scale})
        self.is_to_png = True
        # delete selection on objects
        self.mouse_cur_x = self.mouse_start_x = 0
        self.mouse_cur_y = self.mouse_start_y = 0
        self.select_objects()
        self.scene_update()
        # save in png
        pixmap = self.grab(QRect(QPoint(self.offset_x - 1, self.offset_y - 1),
                                 QPoint((self.grid_width + 1) * get_map_width(self.get_layer(TILES)) * temp_scale + self.offset_x - 2,
                                        (self.grid_height + 1) * get_map_height(self.get_layer(TILES)) * temp_scale + self.offset_y - 2)))
        pixmap.save(f"{file_name}.png")
        self.is_to_png = False
        # remove smoothing and scaling of objects
        self.coordinates_transformer.set_scale(self.scale)
        self.change_object_handler(self.set_png_mode, {"mode": False})
        self.change_object_handler(self.scaled_obj, {"scale": self.scale})
        self.scene_update()

    def create_new_map(self, info: Dict[str, Any], path: Path) -> None:
        self.tile_map = info["map_name"]
        change_map_name(self.map.map, info["map_name"])
        self.grid_width = float(info['tile_width']) * self.grid_scale
        self.grid_height = float(info['tile_height']) * self.grid_scale
        self.scale = 1
        self.coordinates_transformer.set_scale(self.scale)
        self.open_map(path, info["map_name"], True, (int(info['x']), int(info['y'])),
                      (float(info['tile_width']), float(info['tile_height'])),
                      info["default_fill"])
        self.set_coordinates_transformer_data()

    def set_coordinates_transformer_data(self) -> None:
        self.coordinates_transformer.set_scale(self.scale)
        self.coordinates_transformer.set_grid_size(
            (self.grid_width, self.grid_height))
        self.coordinates_transformer.set_tile_size((self.tile_width,
                                                    self.tile_height))

    def set_tile_size(self, tile_width: float, tile_height: float) -> None:
        self.tile_width, self.tile_height = [tile_width, tile_height]

    def create_default_map_content(self, size: Tuple[int, int],
                                   tile_size: Tuple[float, float],
                                   default_fill: str) -> None:
        width, height = size
        self.set_map_viewer_sizes(tile_size[0], tile_size[1])
        self.add_frame_on_map(self.tile_map)
        self.add_obj_on_map(TILE_MAPS, self.tile_map)
        self.set_tile_size_command(self.tile_map, tile_size)
        for i in range(width):
            for j in range(height):
                new_tile_name = f"{self.tile_map}/tile_{i}_{j}"
                self.add_obj_on_map(TILES, new_tile_name)
                self.set_relative_to(new_tile_name, self.map.map.name)
                self.change_tile_type({"default_fill": default_fill,
                                       "tile_name": new_tile_name})
                self.move_obj_command(new_tile_name,
                                      (float(i) * self.tile_width,
                                       float(j) * self.tile_height))
                self.move_tile(new_tile_name, (i, j))

    def open_map(self, path: Path, map_name: str, is_new_map: bool = False,
                 size: Tuple[int, int] = (0, 0),
                 tile_size: Tuple[float, float] = (0, 0),
                 default_fill: str = "") -> None:
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.delete_objects()
        self.parentWidget().parent().clear_editor_history()
        self.map.load_map(MapDescription(path, map_name))
        self.init_handlers()
        if is_new_map:
            self.create_default_map_content(size, tile_size, default_fill)
        else:
            self.set_tile_map()
            self.set_map_viewer_sizes()
        self.set_coordinates_transformer_data()
        self.init_all_map_objects()
        self.change_object_handler(self.scaled_obj, {"scale": self.scale})
        self.set_map_size()
        self.save_viewer_state()
        self.parentWidget().parent().to_the_map_corner()
        self.scene_update()
        QApplication.restoreOverrideCursor()

    def save_state(self) -> Memento:
        # custom deepcopy
        layers = {name: self.get_layer_deepcopy(name) for name in self.map.map.layers}
        return Memento({"layers": layers, "map_height": self.map_height,
                        "tile_width": self.tile_width, "tile_height": self.tile_height,
                        "grid_scale": self.grid_scale, "grid_height": self.grid_height,
                        "grid_width": self.grid_width, "tile_map": self.tile_map})

    def restore_state(self, m: Memento) -> None:
        QApplication.setOverrideCursor(Qt.WaitCursor)
        state = m.get_state()
        if state:
            layers = state["layers"]
            self.delete_objects()
            # removing all elements from the original layers
            for layer in self.map.map.layers:
                items = [item for item in self.map.map.layers[layer]]
                for item in items:
                    del self.map.map.layers[layer][item]
            # fill the original now empty layers with the copied data
            for layer_name in layers:
                layer = deepcopy(layers[layer_name])
                if not layer:
                    layer = {}
                items = [item for item in layer]
                for item in items:
                    self.map.map.layers[layer_name][item] = layer[item]
            # initialize map objects from layers
            self.init_all_map_objects()
            self.scene_update()
        QApplication.restoreOverrideCursor()

    def copy(self) -> None:
        # save layer name, map object from him layer and save him frame
        copied_objects = {}
        layers = {name: self.get_layer_deepcopy(name) for name in
                  self.map.map.layers}
        for map_object in self.objects.values():
            if map_object.is_select or (map_object.layer_name == TILES and self.is_selected_tile(layers[map_object.layer_name][map_object.name], is_dict=True)):
                layer_object = layers[map_object.layer_name][map_object.name]
                object_frame = layers[FRAMES][map_object.name]
                copied_objects[map_object.name] = [map_object.layer_name,
                                                   layer_object, object_frame]
        self.buffer.save_buffer(copied_objects)

    def find_left_low_tile(self, objects: list) -> Tuple[int, int]:
        j = self.map_height
        i = get_map_width(self.get_layer(TILES))
        for map_object_info in objects:
            if map_object_info["i"] <= i and map_object_info["j"] <= j:
                i = map_object_info["i"]
                j = map_object_info["j"]
        return i, j

    def find_left_low_frame(self, objects: list) -> Tuple[float, float]:
        j = self.map_height * self.tile_height
        i = get_map_width(self.get_layer(TILES)) * self.tile_width
        for map_object_info in objects:
            if map_object_info["pose"]["x"] <= i and map_object_info["pose"]["y"] <= j:
                i = map_object_info["pose"]["x"]
                j = map_object_info["pose"]["y"]
        return i, j

    def find_selected_tiles(self):
        tiles = self.get_layer(TILES)
        selected_tiles = []
        for tile_name in tiles:
            tile = tiles[tile_name]
            if self.is_selected_tile(tile):
                selected_tiles.append(tile)
        return selected_tiles

    def find_diff_for_pasting(self, objects: dict):
        # find the bottom left tile to figure out where to paste
        # the copied objects
        copied_tiles = []
        copied_objects = []
        for obj in objects.values():
            if obj[0] == TILES:
                copied_tiles.append(obj[1])
            copied_objects.append(obj[2])
        # find left bottom tile
        i, j = (self.find_left_low_tile(copied_tiles))
        selected_tiles = self.find_selected_tiles()
        pressed_tile_i, pressed_tile_j = (
            self.find_left_low_tile(selected_tiles))
        diff_i = pressed_tile_i - i
        diff_j = pressed_tile_j - j
        # find left bottom object coordinates
        x, y = (self.find_left_low_frame(copied_objects))
        # find difference  pasting coordinates for objects
        diff_x = pressed_tile_i * self.tile_width - x
        diff_y = pressed_tile_j * self.tile_height - y
        return diff_i, diff_j, diff_x, diff_y

    @needsavestate
    def paste(self) -> None:
        objects = self.buffer.get_buffer()
        if objects and len(objects.keys()):
            diff_i, diff_j, diff_x, diff_y = (self.find_diff_for_pasting(objects))
            map_width = get_map_width(self.get_layer(TILES))
            # restore objects
            for obj_name, map_object_info in objects.items():
                map_object_info = deepcopy(map_object_info)
                layer_name = map_object_info[0]
                # restore tiles
                if layer_name == TILES:
                    tile = map_object_info[1]
                    if not (0 <= tile["i"] + diff_i < map_width and 0 <= tile["j"] + diff_j < self.map_height):
                        continue
                    changeable_tile = f"{self.map.map.name}/tile_{tile['i'] + diff_i}_{tile['j'] + diff_j}"
                    self.change_tile_type({"default_fill": tile["type"], "tile_name": changeable_tile})
                    self.rotate_obj(self.objects[changeable_tile], map_object_info[2]["pose"]["yaw"])
                    self.rotate_obj_on_map(changeable_tile, map_object_info[2]["pose"]["yaw"])
                # restore objects
                else:
                    new_obj_name, _ = self.generate_object_name_and_id(self.tile_map, layer_name)
                    if map_object_info[2]["relative_to"] != self.tile_map:
                        map_object_info[2]["relative_to"] = self.tile_map
                        map_object_info[2]["pose"]["x"] = diff_x
                        map_object_info[2]["pose"]["y"] = diff_y
                    else:
                        map_object_info[2]["pose"]["x"] += diff_x
                        map_object_info[2]["pose"]["y"] += diff_y
                    # check and change object coordinates
                    if map_object_info[2]["pose"]["x"] < 0:
                        map_object_info[2]["pose"]["x"] = 0
                    elif map_object_info[2]["pose"]["x"] > map_width * self.tile_width:
                        map_object_info[2]["pose"]["x"] = map_width * self.tile_width
                    if map_object_info[2]["pose"]["y"] < 0:
                        map_object_info[2]["pose"]["y"] = 0
                    elif map_object_info[2]["pose"]["y"] > self.map_height * self.tile_height:
                        map_object_info[2]["pose"]["y"] = self.map_height * self.tile_height
                    # add object from copied info
                    self.add_obj_on_map(layer_name, new_obj_name)
                    self.change_obj_from_config(layer_name,
                                                new_obj_name,
                                                map_object_info[1])
                    self.change_obj_from_config(FRAMES,
                                                new_obj_name,
                                                map_object_info[2])
                    if layer_name in LAYERS_WITH_TYPES:
                        self.add_obj_image(layer_name, new_obj_name, item_name=map_object_info[1]["type"])
                    else:
                        self.add_obj_image(layer_name, new_obj_name)

    @needsavestate
    def cut_out(self) -> None:
        self.copy()
        # brushing selected tiles on asphalt type
        self.painting_tiles("asphalt")
        # delete selected_objects
        self.delete_selected_objects()
