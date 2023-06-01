TILES = "tiles"
FRAMES = "frames"
FRAME = "frame"
TILE_MAPS = "tile_maps"
TILE_SIZE = "tile_size"
WATCHTOWERS = "watchtowers"
TRAFFIC_SIGNS = "traffic_signs"
GROUND_TAGS = "ground_tags"
VEHICLES = "vehicles"
CITIZENS = "citizens"
NEW_CONFIG = "new_config"
RELATIVE_TO = "relative_to"
LAYER_NAME = "layer_name"
OBJECTS_TYPES = [WATCHTOWERS, CITIZENS, VEHICLES, GROUND_TAGS]
NOT_DRAGGABLE = [TILES]
LAYERS_WITH_TYPES = [TRAFFIC_SIGNS, TILES]
KNOWN_LAYERS = [FRAMES, TILES, TILE_MAPS, WATCHTOWERS, CITIZENS,
                TRAFFIC_SIGNS, GROUND_TAGS, VEHICLES]
REQUIRED_LAYERS = [f"{TILES}.yaml", f"{FRAMES}.yaml", f"{TILE_MAPS}.yaml"]
TILE_KIND = ('block', 'road')
TILE_TYPES = ("straight", "curve", "3way", "4way", "asphalt", "grass", "floor")
TRAFFIC_SIGNS_TYPES = ("stop", "yield", "no_right_turn", "no_left_turn",
                       "do_not_enter", "oneway_right", "oneway_left",
                        "four_way_intersect", "right_t_intersect",
                        "left_t_intersect", "t_intersection", "pedestrian",
                        "t_light_ahead", "duck_crossing", "parking")
WATCHTOWERS_CONFIGURATION = ("WT18", "WT19")
VEHICLES_CONFIGURATION = ("DB18", "DB19", "DB20", "DB21M", "DB21J", "DB21R")
CITIZENS_COLORS = ("yellow", "red", "green", "grey")
VEHICLES_COLORS = ("blue", "red", "green", "grey")
FORM_DICT = {
    TILES: {"type": TILE_TYPES},
    TRAFFIC_SIGNS: {"type": TRAFFIC_SIGNS_TYPES},
    CITIZENS: {"color": CITIZENS_COLORS},
    VEHICLES: {"color": VEHICLES_COLORS, "configuration": VEHICLES_CONFIGURATION},
    WATCHTOWERS: {"configuration": WATCHTOWERS_CONFIGURATION}
}
CTRL = 16777249
VIEW_TILE_HEIGHT = 150

TRAFFIC_SIGNS_TYPES_IDS = \
 {'stop': [1, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
           36, 37, 38, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172,
           173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186,
           187, 188, 189, 190, 191, 192, 193, 194, 195, 196],
  'yield': [2, 39], 'no_right_turn': [3, 40], 'no_left_turn': [4, 41],
  'do_not_enter': [5, 69], 'oneway_right': [6, 42], 'oneway_left': [7, 43],
  'four_way_intersect': [8, 13, 14, 15, 16, 17, 18, 19, 44, 45, 46, 47, 48, 49,
                         50, 51, 52, 53, 54, 55, 56, 197, 198, 199, 231, 232,
                         233, 234, 262, 263, 264],
  'right_t_intersect': [9, 57, 58, 59, 60, 132, 133, 134, 135, 136, 137, 138,
                        139, 140, 141, 235, 238, 241, 244, 260, 261],
  'left_t_intersect': [10, 61, 62, 63, 64, 152, 153, 154, 155, 156, 157, 158,
                       159, 160, 161, 237, 240, 242, 245, 248, 249],
  't_intersection': [11, 65, 66, 67, 68, 142, 143, 144, 145, 146, 147, 148, 149,
                     150, 151, 236, 239, 243, 246, 247],
  'pedestrian': [12, 70, 71, 72, 73],
  't_light_ahead': [74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88,
                    89, 90, 91, 92, 93, 94, 200, 201, 202, 203, 204, 205, 206,
                    207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218,
                    219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230],
  'duck_crossing': [95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107,
                    108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
                    120, 121, 122, 123, 124],
  'parking': [125, 126, 127, 128, 129, 130, 131]}
