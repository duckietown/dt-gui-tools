class CoordinatesTransformer:
    """coordinate of mouse, pressevent, moveevent, offset,"""
    def __init__(self, scale: float, size_map: int, grid_width: float, grid_height: float, tile_width: float, tile_height: float):
        self.scale: float = scale
        self.size_map: int = size_map
        self.grid_width: float = grid_width
        self.grid_height: float = grid_height
        self.tile_height: float = tile_height
        self.tile_width: float = tile_width

    def get_x_from_view(self, x_view: float,
                        offset_x: float = 0.0,
                        obj_width: float = 0.0) -> float:
        return (x_view + obj_width / 2 - offset_x) / self.scale / (self.grid_width + 1) * self.tile_width

    def get_y_from_view(self, y_view: float,
                        offset_y: float = 0.0,
                        obj_height: float = 0.0) -> float:
        return (self.size_map - (y_view + obj_height / 2 - offset_y)
                / self.scale / (self.grid_height + 1)) * self.tile_height

    def get_x_to_view(self, x_real: float, obj_width: float = 0.0) -> float:
        return x_real * self.scale * (self.grid_width + 1) / self.tile_width - obj_width / 2

    def get_y_to_view(self, y_real: float, obj_height: float = 0.0) -> float:
        return (self.size_map - y_real / self.tile_height - 1) * self.scale * (self.grid_height + 1) + 2.5 * obj_height

    def set_scale(self, new_scale: float) -> None:
        self.scale = new_scale

    def set_size_map(self, new_size_map: int) -> None:
        self.size_map = new_size_map

    def set_grid_size(self, new_grid_size: tuple) -> None:
        self.grid_width = new_grid_size[0]
        self.grid_height = new_grid_size[1]

    def set_tile_size(self, new_tile_size: tuple) -> None:
        self.tile_width = new_tile_size[0]
        self.tile_height = new_tile_size[1]
