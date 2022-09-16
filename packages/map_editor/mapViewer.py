# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtGui import QKeyEvent
from dt_maps.types.tiles import Tile
from dt_maps import MapLayer
from classes.Commands.AddObjCommand import AddObjCommand
from classes.Commands.DeleteObjCommand import DeleteObjCommand
from classes.Commands.GetLayerCommand import GetLayerCommand
from classes.Commands.SetTileSizeCommand import SetTileSizeCommand
from classes.Commands.GetDefaultLayerConf import GetDefaultLayerConf
from classes.Commands.ChangeObjCommand import ChangeObjCommand
from classes.Commands.CheckConfigCommand import CheckConfigCommand
from classes.map_objects import DraggableImage, ImageObject
from typing import Dict, Any, Optional, Union, Tuple
from layers import TileLayerHandler, WatchtowersLayerHandler, \
    FramesLayerHandler, TileMapsLayerHandler, CitizensHandler, \
    TrafficSignsHandler, GroundTagsHandler, VehiclesHandler
from coordinatesTransformer import CoordinatesTransformer
from painter import Painter
from classes.Commands.MoveObjCommand import MoveObjCommand
from classes.Commands.RotateObjCommand import RotateCommand
from classes.Commands.ChangeTypeCommand import ChangeTypeCommand
from classes.Commands.MoveTileCommand import MoveTileCommand
from utils.maps import default_map_storage, get_map_height, get_map_width, \
    REGISTER
from utils.constants import LAYERS_WITH_TYPES, OBJECTS_TYPES, FRAMES, FRAME, \
    TILES, \
    TILE_MAPS, TILE_SIZE, NOT_DRAGGABLE
from classes.MapDescription import MapDescription
from pathlib import Path


class MapViewer(QtWidgets.QGraphicsView, QtWidgets.QWidget):
    map = None
    tile_sprites: Dict[str, QtGui.QImage] = {'empty': QtGui.QImage()}
    tiles = None
    map_height = 10
    objects = {}
    handlers = None

    scale = 1
    tile_selection = [0] * 4
    rmbPressed = False
    lmbPressed = False
    rmbPrevPos = [0, 0]
    mouse_start_x, mouse_start_y = 0, 0
    mouse_cur_x, mouse_cur_y = 0, 0
    offset_x = 0
    offset_y = 0
    lmbClicked = QtCore.pyqtSignal(int, int)  # click coordinates as an index of the clicked tile
    is_to_png = False
    tile_width: float = 0.585
    tile_height: float = 0.585
    grid_scale: float = 100
    grid_height: float = tile_height * grid_scale
    grid_width: float = tile_width * grid_scale
    tile_map: str = "map_1"

    def __init__(self):
        QtWidgets.QGraphicsView.__init__(self)

        self.setScene(QtWidgets.QGraphicsScene())
        self.map = default_map_storage()
        self.init_handlers()
        self.set_map_viewer_sizes()
        self.coordinates_transformer = CoordinatesTransformer(self.scale,
                                                              self.map_height,
                                                              self.grid_width,
                                                              self.grid_height,
                                                              self.tile_width,
                                                              self.tile_height)
        self.painter = Painter()
        self.init_objects()
        self.set_map_size()
        self.setMouseTracking(True)

    def init_objects(self) -> None:
        for layer_name in REGISTER:
            layer = self.get_layer(layer_name)
            if layer_name not in LAYERS_WITH_TYPES and \
            layer_name not in OBJECTS_TYPES or not layer:
                continue
            for object_name in layer:
                layer_object = layer[object_name]
                self.add_obj_image(layer_name, object_name, layer_object)

    def init_handlers(self) -> None:
        self.tiles = TileLayerHandler()
        watchtowers = WatchtowersLayerHandler()
        frames = FramesLayerHandler()
        tile_maps = TileMapsLayerHandler()
        citizens = CitizensHandler()
        traffic_signs = TrafficSignsHandler()
        ground_tags = GroundTagsHandler()
        vehicles = VehiclesHandler()
        # self.decorations = DecorationsHandler()

        handlers_list = [self.tiles, watchtowers, frames,
                         tile_maps, citizens, traffic_signs,
                         vehicles, ground_tags]
        for i in range(len(handlers_list) - 1):
            handlers_list[i].set_next(handlers_list[i + 1])
        self.handlers = self.tiles

    def set_map_viewer_sizes(self, tile_width: float = 0, tile_height: float = 0) -> None:
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

    def set_tile_map(self):
        tile_maps = self.get_layer(TILE_MAPS)
        self.tile_map = [elem for elem in tile_maps][0]

    def add_obj(self, type_of_element: str, item_name: str = None) -> None:
        i = 1
        layer_name = f"{type_of_element}s"
        while True:
            object_name: str = f"{self.tile_map}/{type_of_element}{i}"
            if object_name not in self.objects:
                self.add_obj_on_map(layer_name, object_name)
                self.add_obj_image(layer_name, object_name, item_name=item_name)
                self.scaled_obj(self.get_object(object_name),
                                {'scale': self.scale})
                break
            i += 1

    def add_obj_image(self, layer_name: str, object_name: str,
                      layer_object=None, item_name: str = None) -> None:
        new_obj = None
        img_name = layer_name
        if layer_name in LAYERS_WITH_TYPES and layer_object:
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
            frame_obj = self.get_layer(FRAMES)[object_name]
            self.rotate_obj(new_obj, frame_obj.pose.yaw)
            new_coordinates = (
                self.get_x_to_view(frame_obj.pose.x, new_obj.width()),
                self.get_y_to_view(frame_obj.pose.y), new_obj.height()
            )
            self.set_obj_map_pos(new_obj, (frame_obj.pose.x, frame_obj.pose.y))
            self.move_obj(new_obj, {"new_coordinates": new_coordinates})
            self.objects[object_name] = new_obj
            if new_obj.layer_name in LAYERS_WITH_TYPES:
                self.handlers.handle(ChangeTypeCommand(new_obj.layer_name, object_name, img_name))
        self.change_object_handler(self.scaled_obj, {"scale": self.scale})


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

    def delete_objects(self):
        for obj_name in self.objects:
            obj = self.get_object(obj_name)
            obj.delete_object()
        self.objects.clear()

    def move_obj(self, obj: ImageObject, args: Dict[str, Any]) -> None:
        if "new_coordinates" in args:
            new_coordinates = args["new_coordinates"]
            obj.move_object(new_coordinates)
        elif "delta_coordinates" in args:
            delta_coord = args["delta_coordinates"]
            obj.move_object((obj.pos().x() + delta_coord[0],
                             obj.pos().y() + delta_coord[1]))

    def set_obj_map_pos(self, obj: ImageObject, new_pos: Tuple[float, float]) -> None:
        obj.set_obj_map_pos(new_pos)

    def move_obj_on_map(self, frame_name: str,
                        new_pos: Tuple[float, float],
                        obj_width: float = 0,
                        obj_height: float = 0) -> None:
        map_x = self.get_x_from_view(new_pos[0], obj_width=obj_width,
                                     offset=self.offset_x)
        map_y = self.get_y_from_view(new_pos[1], obj_height=obj_height,
                                     offset=self.offset_y)
        obj = self.get_object(frame_name)
        self.set_obj_map_pos(obj, (map_x, map_y))
        self.move_obj_command(frame_name, (map_x, map_y))

    def move_obj_command(self, frame_name: str,
                         new_coord: Tuple[float, float]) -> None:
        self.handlers.handle(command=MoveObjCommand(frame_name, new_coord))

    def rotate_obj(self, obj: ImageObject, new_angle: float) -> None:
        obj.rotate_object(new_angle)
        self.scene_update()

    def rotate_obj_on_map(self, frame_name: str, new_angle: float) -> None:
        self.handlers.handle(command=RotateCommand(frame_name, new_angle))

    def scaled_obj(self, obj: ImageObject, args: Dict[str, Any]) -> None:
        scale = args["scale"]
        obj.scale_object(scale)
        if obj.is_draggable():
            new_coordinates = (
                self.get_x_to_view(
                    obj.obj_map_pos[0], obj.width()) + self.offset_x,
                self.get_y_to_view(
                    obj.obj_map_pos[1], obj.height()) + self.offset_y)
        else:
            new_coordinates = (
                self.get_x_to_view(
                    obj.obj_map_pos[0]) + self.offset_x,
                self.get_y_to_view(
                    obj.obj_map_pos[1]) + self.offset_y)
        self.move_obj(obj, {"new_coordinates": new_coordinates})

    def set_map_size(self, height: int = 0) -> None:
        if not height:
            self.map_height = get_map_height(self.get_layer(TILES))
        else:
            self.map_height = height
        self.coordinates_transformer.set_size_map(self.map_height)

    def rotate_with_button(self, args: Dict[str, Any]) -> None:
        tile_name = args["tile_name"]
        obj = self.get_object(tile_name)
        self.rotate_obj(obj, obj.yaw + 90)
        self.rotate_obj_on_map(tile_name, obj.yaw)

    def is_selected_tile(self, tile: Tile) -> bool:
        return ((tile.i + 1) * self.tile_width >= self.tile_selection[0] and
                tile.i * self.tile_width <= self.tile_selection[2] and
                (tile.j + 1) * self.tile_height >= self.tile_selection[3] and
                tile.j * self.tile_height <= self.tile_selection[1])

    def get_x_to_view(self, x: float, obj_width: float = 0):
        return self.coordinates_transformer.get_x_to_view(x, obj_width)

    def get_y_to_view(self, y: float, obj_height: float = 0):
        return self.coordinates_transformer.get_y_to_view(y, obj_height)

    def get_x_from_view(self, x: float, obj_width: float = 0, offset: float = 0):
        return self.coordinates_transformer.get_x_from_view(x,
                                                            obj_width=obj_width,
                                                            offset_x=offset)

    def get_y_from_view(self, y: float, obj_height: float = 0, offset: float = 0):
        return self.coordinates_transformer.get_y_from_view(y,
                                                            obj_height=obj_height,
                                                            offset_y=offset)

    def get_layer(self, layer_name: str) -> Optional[MapLayer]:
        return self.handlers.handle(command=GetLayerCommand(layer_name))

    def get_object(self, obj_name: str) -> Optional[ImageObject]:
        return self.objects[obj_name]

    def get_default_layer_conf(self, layer_name: str) -> Dict[str, Any]:
        return self.handlers.handle(GetDefaultLayerConf(layer_name))

    def get_object_conf(self, layer_name: str, name: str) -> Dict[str, Any]:
        layer = self.get_layer(layer_name)
        obj = layer[name]
        default_layer_conf = self.get_default_layer_conf(layer_name)
        for key in default_layer_conf:
            try:
                default_layer_conf[key] = obj[key].value
            except AttributeError:
                default_layer_conf[key] = obj[key]
        return default_layer_conf

    def change_obj_info(self, layer_name: str, obj_name: str) -> None:
        obj = self.get_object(obj_name)
        self.parentWidget().parent().change_obj_info(layer_name, obj_name,
                                                     self.get_object_conf(layer_name, obj_name),
                                                     self.get_object_conf(FRAMES, obj.name), obj.is_draggable())
    
    def change_obj_from_info(self, conf: Dict[str, Any]) -> None:
        print(conf)
        obj = self.get_object(conf["name"])
        if conf["is_valid"]:
            if conf["remove"]:
                self.delete_object(obj)
                obj.delete_object()
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
                    # move object if draggable
                    if conf["is_draggable"]:
                        # check correct values
                        pos_x = self.get_x_to_view(
                            conf[FRAME]["pose"]["x"],
                            obj.width()) + self.offset_x
                        pos_y = self.get_y_to_view(
                            conf[FRAME]["pose"]["y"],
                            obj.height()) + self.offset_y
                        self.move_obj(obj, {"new_coordinates": (pos_x, pos_y)})
                        self.move_obj_on_map(obj.name, (pos_x, pos_y),
                                             obj_width=obj.width(),
                                             obj_height=obj.height())
                else:
                    self.parentWidget().parent().view_info_form("Error",
                                                                "Invalid object frame values entered!")
                # check correct values
                if self.check_layer_config(conf["layer_name"], conf["new_config"]):
                    self.change_obj_from_config(conf["layer_name"],
                                                conf["name"],
                                                conf["new_config"])
                    name = obj.name
                    self.objects.__delitem__(obj.name)
                    obj.delete_object()
                    layer = self.get_layer(conf["layer_name"])
                    self.add_obj_image(conf["layer_name"], name, layer[name])
                else:
                    self.parentWidget().parent().view_info_form("Error",
                                                                "Invalid object configuration entered!")
        else:
            self.parentWidget().parent().view_info_form("Error",
                                                        "Invalid values entered!")

    def check_layer_config(self, layer_name: str, new_config: Dict[str, Any]):
        return self.handlers.handle(CheckConfigCommand(layer_name, new_config))

    def change_obj_from_config(self, layer_name: str, obj_name: str,
                               new_config: Dict[str, Any]):
        self.handlers.handle(ChangeObjCommand(layer_name, obj_name,
                                              new_config))

    def delete_object(self, obj: ImageObject) -> None:
        self.delete_obj_on_map(obj)
        self.objects.__delitem__(obj.name)

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
            handler_func(self.get_object(obj_name), args)

    def painting_tiles(self, default_fill: str) -> None:
        self.change_tiles_handler(self.change_tile_type,
                                  {"default_fill": default_fill})

    def rotate_tiles(self) -> None:
        self.change_tiles_handler(self.rotate_with_button, {})

    def highlight_select_tile(self, args: Dict[str, Any]):
        tile = self.get_object(args["tile_name"])
        self.painter.draw_rect((tile.pos().x() - 1, tile.pos().y() - 1),
                               self.scale, args["painter"],
                               self.grid_width, self.grid_height,
                               )

    def change_tile_type(self, args: Dict[str, Any]) -> None:
        new_tile_type = args["default_fill"]
        tile_name = args["tile_name"]
        img_path = f"./img/tiles/{new_tile_type}.png"
        mutable_obj = self.get_object(tile_name)
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
        delta_pos = (x - self.mouse_cur_x,
                     y - self.mouse_cur_y)
        self.change_object_handler(self.move_obj,
                                   {"delta_coordinates": delta_pos})

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
        if event.buttons() == QtCore.Qt.LeftButton:
            self.lmbPressed = True
            self.set_offset()
            self.mouse_cur_x = self.mouse_start_x = x
            self.mouse_cur_y = self.mouse_start_y = y

    def mouseMoveEvent(self, event: Union[Tuple[float, float], QtGui.QMouseEvent]) -> None:
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
        if event.button() == QtCore.Qt.LeftButton:
            self.lmbPressed = False
            self.set_offset()
            if not self.is_move_mode():
                self.select_tiles()
            self.parentWidget().parent().selectionUpdate()
            self.scene_update()
        else:
            self.rmbPressed = False

    def set_offset(self) -> None:
        left_upper_tile = self.get_object(f"{self.tile_map}/tile_0_{self.map_height - 1}")
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

        self.painter.fill_background(painter, 'lightGray', self.size().width(),
                                     self.size().height())
        if not self.is_to_png:
            self.change_tiles_handler(self.highlight_select_tile,
                                      {"painter": painter})
        self.scene_update()

    def select_tiles(self) -> None:
        raw_selection = [
            self.get_x_from_view(
                min(self.mouse_start_x, self.mouse_cur_x), offset=self.offset_x),
            self.get_y_from_view(
                min(self.mouse_start_y, self.mouse_cur_y), offset=self.offset_y),
            self.get_x_from_view(
                max(self.mouse_start_x, self.mouse_cur_x), offset=self.offset_x),
            self.get_y_from_view(
                max(self.mouse_start_y, self.mouse_cur_y), offset=self.offset_y),
        ]

        if self.get_layer(TILES):
            self.tile_selection = [
                v
                for i, v in enumerate(raw_selection)
            ]

    def save_to_png(self, file_name: str) -> None:
        self.coordinates_transformer.set_scale(1)
        self.change_object_handler(self.scaled_obj, {"scale": 1})
        self.is_to_png = True
        self.scene_update()
        pixmap = self.grab(QRect(QPoint(self.offset_x, self.offset_y),
                                 QPoint((self.grid_width + 1) * get_map_width(self.get_layer(TILES)) + self.offset_x,
                                        (self.grid_height + 1) * get_map_height(self.get_layer(TILES)) + self.offset_y)))
        pixmap.save(f"{file_name}.png")
        self.is_to_png = False
        self.coordinates_transformer.set_scale(self.scale)
        self.change_object_handler(self.scaled_obj, {"scale": self.scale})
        self.scene_update()

    def create_new_map(self, info: Dict[str, Any], path: Path) -> None:
        width, height = int(info['x']), int(info['y'])
        tile_width = float(info['tile_width'])
        tile_height = float(info['tile_height'])
        self.grid_width = tile_width * self.grid_scale
        self.grid_height = tile_height * self.grid_scale
        self.scale = 1
        self.coordinates_transformer.set_scale(self.scale)
        self.open_map(path, self.map.map.name, True, (width, height),
                      (tile_width, tile_height))
        self.set_coordinates_transformer_data()

    def set_coordinates_transformer_data(self):
        self.coordinates_transformer.set_scale(self.scale)
        self.coordinates_transformer.set_grid_size(
            (self.grid_width, self.grid_height))
        self.coordinates_transformer.set_tile_size((self.tile_width,
                                                    self.tile_height))

    def set_tile_size(self, tile_width: float, tile_height: float) -> None:
        self.tile_width, self.tile_height = [tile_width, tile_height]

    def create_default_map_content(self, size: Tuple[int, int],
                                   tile_size: Tuple[float, float]) -> None:
        width, height = size
        self.set_map_viewer_sizes(tile_size[0], tile_size[1])
        self.tile_map = "map_1"
        self.add_frame_on_map(self.tile_map)
        self.add_obj_on_map(TILE_MAPS, self.tile_map)
        self.set_tile_size_command(self.tile_map, tile_size)
        for i in range(width):
            for j in range(height):
                new_tile_name = f"{self.tile_map}/tile_{i}_{j}"
                self.add_obj_on_map(TILES, new_tile_name)
                self.move_obj_command(new_tile_name,
                                      (float(i) * self.tile_width,
                                       float(j) * self.tile_height))
                self.move_tile(new_tile_name, (i, j))

    def open_map(self, path: Path, map_name: str, is_new_map: bool = False,
                 size: Tuple[int, int] = (0, 0),
                 tile_size: Tuple[float, float] = (0, 0)) -> None:
        self.delete_objects()
        self.map.load_map(MapDescription(path, map_name))
        self.set_tile_map()
        self.init_handlers()
        if is_new_map:
            self.create_default_map_content(size, tile_size)
        else:
            self.set_map_viewer_sizes()
        self.set_coordinates_transformer_data()
        self.init_objects()
        self.change_object_handler(self.scaled_obj, {"scale": self.scale})
        self.set_map_size()
        self.scene_update()
