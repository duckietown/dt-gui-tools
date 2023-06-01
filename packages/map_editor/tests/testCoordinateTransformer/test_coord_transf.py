import unittest
import json
from coordinatesTransformer import CoordinatesTransformer


class MyTestCase(unittest.TestCase):

    def test_x_to_view(self):
        with open("./tests/testCoordinateTransformer/test_x_to_view.json",
                  "r") as file:
            self.test_cases = json.load(file)
        for test_name in self.test_cases:
            with self.subTest(test_name=test_name):
                case = self.test_cases[test_name]
                coord_trans = CoordinatesTransformer(case['scale'],
                                                     case['size_map'],
                                                     case['grid_width'],
                                                     case['grid_height'],
                                                     case['tile_width'],
                                                     case['tile_height'])
                ret = coord_trans.get_x_to_view(case['x'])
                self.assertLess(abs((ret - case['ret'])), 0.001)

    def test_y_to_view(self):
        with open("./tests/testCoordinateTransformer/test_y_to_view.json",
                  "r") as file:
            self.test_cases = json.load(file)
        for test_name in self.test_cases:
            with self.subTest(test_name=test_name):
                case = self.test_cases[test_name]
                coord_trans = CoordinatesTransformer(case['scale'],
                                                     case['size_map'],
                                                     case['grid_width'],
                                                     case['grid_height'],
                                                     case['tile_width'],
                                                     case['tile_height'])
                ret = coord_trans.get_x_to_view(case['y'])
                self.assertLess(abs((ret - case['ret'])), 0.001)

    def test_x_from_view(self):
        with open("./tests/testCoordinateTransformer/test_x_from_view.json",
                  "r") as file:
            self.test_cases = json.load(file)
        for test_name in self.test_cases:
            with self.subTest(test_name=test_name):
                case = self.test_cases[test_name]
                coord_trans = CoordinatesTransformer(case['scale'],
                                                     case['size_map'],
                                                     case['grid_width'],
                                                     case['grid_height'],
                                                     case['tile_width'],
                                                     case['tile_height'])
                ret = coord_trans.get_x_from_view(case['x'],
                                                  case['offset_x'],
                                                  case['obj_width'])
                self.assertLess(abs((ret - case['ret'])), 0.001)

    def test_y_from_view(self):
        with open("./tests/testCoordinateTransformer/test_y_from_view.json",
                  "r") as file:
            self.test_cases = json.load(file)
        for test_name in self.test_cases:
            with self.subTest(test_name=test_name):
                case = self.test_cases[test_name]
                coord_trans = CoordinatesTransformer(case['scale'],
                                                     case['size_map'],
                                                     case['grid_width'],
                                                     case['grid_height'],
                                                     case['tile_width'],
                                                     case['tile_height'])
                ret = coord_trans.get_y_from_view(case['y'],
                                                  case['offset_y'],
                                                  case['obj_height'])
                self.assertLess(abs((ret - case['ret'])), 0.001)


if __name__ == '__main__':
    unittest.main()
