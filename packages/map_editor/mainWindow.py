import functools
import json
import codecs
from PyQt5.QtGui import QResizeEvent, QKeyEvent
from mapAPI import MapAPI
from mapViewer import MapViewer
from utils.debug import DebugLine
from windowDesign import *
from PyQt5.QtCore import Qt, QEvent
from typing import Dict, Any


_translate = QtCore.QCoreApplication.translate


class DuckWindow(QtWidgets.QMainWindow):
    map_viewer = None
    map_api = None
    info_json = None

    def __init__(self, args, elem_info="doc/info.json"):
        super().__init__()

        #  The brush button / override the closeEvent
        self.brush_button = QtWidgets.QToolButton()
        self.closeEvent = functools.partial(self.quit_program_event)

        # Load element's info
        self.info_json = json.load(codecs.open(elem_info, "r", "utf-8"))

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.map_viewer = MapViewer()
        self.map_api = MapAPI(self.info_json, self.map_viewer, args)
        self.map_viewer.setMinimumSize(540, 540)
        self.ui.horizontalLayout.addWidget(self.map_viewer)
        self.initUi()

        if args.debug:
            self.debug_line = DebugLine()
            self.debug_line.setParent(self)
            self.debug_line.setMaximumHeight(20)
            self.ui.horizontalLayout.addWidget(self.debug_line, Qt.AlignBottom)
            self.map_api.set_debug_mode(self.debug_line)

        self.update_layer_tree()

    def get_translation(self, elem):
        """Gets info about the element based on self.locale
        If local doesn't exist, return locale='en'

        :param self
        :param elem: dict, information about elements (or category), that contains translation
        :return: dict(). Dict with translation based on the self.locale
        """
        if self.locale in elem['lang']:
            return elem['lang'][self.locale]
        else:
            #logger.debug("duck_window.get_translation. No such locale: {}".format(self.locale))
            return elem['lang']['en']

    def initUi(self):
        self.center()
        self.show()

        #  Initialize button objects
        create_map = self.ui.create_new
        open_map = self.ui.open_map
        save_map = self.ui.save_map
        save_map_as = self.ui.save_map_as
        export_png = self.ui.export_png
        # TODO
        #calc_param = self.ui.calc_param
        #about_author = self.ui.about_author
        exit = self.ui.exit
        change_blocks = self.ui.change_blocks
        #change_info = self.ui.change_info TODO
        change_map = self.ui.change_map
        #change_layer = self.ui.change_layer TODO
        #distortion_view = self.ui.distortion_view
        #create_region = self.ui.region_create
        #import_old_format = self.ui.import_old_format
        #environment = self.ui.env

        #  Initialize floating blocks
        block_widget = self.ui.block_widget
        # TODO
        info_widget = self.ui.info_widget
        #map_info_widget = self.ui.map_info_widget
        #layer_info_widget = self.ui.layer_info_widget

        #  Assign actions to buttons
        create_map.triggered.connect(self.create_map_triggered)
        open_map.triggered.connect(self.open_map_triggered)
        save_map.triggered.connect(self.save_map_triggered)
        save_map_as.triggered.connect(self.save_map_as_triggered)
        export_png.triggered.connect(self.save_map_as_png)
        '''
        calc_param.triggered.connect(self.calc_param_triggered)
        about_author.triggered.connect(self.about_author_triggered)
        distortion_view.triggered.connect(self.change_distortion_view_triggered)
        create_region.triggered.connect(self.create_region)
        import_old_format.triggered.connect(self.import_old_format)
        environment.triggered.connect(self.change_env)
        '''
        exit.triggered.connect(self.exit_triggered)

        # TODO
        '''
        change_blocks.toggled.connect(self.change_blocks_toggled)
        change_info.toggled.connect(self.change_info_toggled)
        change_map.toggled.connect(self.change_map_toggled)
        change_layer.toggled.connect(self.toggle_layer_window)
        '''

        block_widget.closeEvent = functools.partial(self.blocks_event)
        info_widget.closeEvent = functools.partial(self.info_event)
        #map_info_widget.closeEvent = functools.partial(self.map_event)
        #layer_info_widget.closeEvent = functools.partial(self.close_layer_window_event)

        self.ui.info_browser.setText(self.info_json["description"])

        #  QToolBar setting
        tool_bar = self.ui.tool_bar

        a1 = QtWidgets.QAction(QtGui.QIcon("img/icons/new.png"), _translate("MainWindow", "New map (Ctrl+N)"), self)
        a2 = QtWidgets.QAction(QtGui.QIcon("img/icons/open.png"), _translate("MainWindow", "Open map (Ctrl+O)"), self)
        a3 = QtWidgets.QAction(QtGui.QIcon("img/icons/save.png"), _translate("MainWindow", "Save map (Ctrl+S)"), self)
        a4 = QtWidgets.QAction(QtGui.QIcon("img/icons/save_as.png"), _translate("MainWindow", "Save map as (Ctrl+Alt+S)"), self)
        a5 = QtWidgets.QAction(QtGui.QIcon("img/icons/png.png"), _translate("MainWindow", "Export to PNG (Ctrl+P)"), self)

        # TODO
        '''
        b1 = QtWidgets.QAction(QtGui.QIcon("img/icons/copy.png"), _translate("MainWindow", "Copy"), self)
        b2 = QtWidgets.QAction(QtGui.QIcon("img/icons/cut.png"), _translate("MainWindow", "Cut"), self)
        b3 = QtWidgets.QAction(QtGui.QIcon("img/icons/insert.png"), _translate("MainWindow", "Paste"), self)
        b4 = QtWidgets.QAction(QtGui.QIcon("img/icons/delete.png"), _translate("MainWindow", "Delete"), self)
        b5 = QtWidgets.QAction(QtGui.QIcon("img/icons/undo.png"), _translate("MainWindow", "Undo"), self)
        b1.setShortcut("Ctrl+C")
        b2.setShortcut("Ctrl+X")
        b3.setShortcut("Ctrl+V")
        b4.setShortcut("Delete")
        b5.setShortcut("Ctrl+Z")
        '''

        c1 = QtWidgets.QAction(QtGui.QIcon("img/icons/rotate.png"), _translate("MainWindow", "Rotate (Ctrl+R)"), self)

        # TODO
        #c2 = QtWidgets.QAction(QtGui.QIcon("img/icons/trim.png"),
        #                       _translate("MainWindow", "Delete extreme empty blocks"), self)
        c1.setShortcut("Ctrl+R")
        #c2.setShortcut("Ctrl+F")

        self.brush_button.setIcon(QtGui.QIcon("img/icons/brush.png"))
        self.brush_button.setCheckable(True)
        self.brush_button.setToolTip("Brush tool (Ctrl+B)")
        self.brush_button.setShortcut("Ctrl+B")

        a1.triggered.connect(self.create_map_triggered)
        a2.triggered.connect(self.open_map_triggered)
        a3.triggered.connect(self.save_map_triggered)
        a4.triggered.connect(self.save_map_as_triggered)
        a5.triggered.connect(self.save_map_as_png)

        # TODO
        '''
        b1.triggered.connect(self.copy_button_clicked)
        b2.triggered.connect(self.cut_button_clicked)
        b3.triggered.connect(self.insert_button_clicked)
        b4.triggered.connect(self.delete_button_clicked)
        b5.triggered.connect(self.undo_button_clicked)
        '''

        c1.triggered.connect(self.rotate_selected_tiles)
        # TODO
        #c2.triggered.connect(self.trimClicked)

        self.brush_button.clicked.connect(self.brush_mode)

        # TODO
        #for elem in [[a1, a2, a3, a4, a5], [b1, b2, b3, b4, b5]]:
        for elem in [[a1, a2, a3, a4, a5]]:
            for act in elem:
                tool_bar.addAction(act)
            tool_bar.addSeparator()
        tool_bar.addWidget(self.brush_button)
        tool_bar.addAction(c1)
        # TODO
        #tool_bar.addAction(c2)

        # TODO
        # Setup Layer Tree menu
        #self.ui.layer_tree.setModel(QtGui.QStandardItemModel())  # set item model for tree

        #  Customize the Blocks menu
        block_list_widget = self.ui.block_list
        block_list_widget.itemClicked.connect(self.item_list_clicked)
        block_list_widget.itemDoubleClicked.connect(self.item_list_double_clicked)

        #  Customize the Map Editor menu
        default_fill = self.ui.default_fill
        delete_fill = self.ui.delete_fill

        #  Fill out the list
        categories = self.info_json['categories']
        information = self.info_json['info']
        for group in categories:
            # add separator
            icon = "img/icons/galka.png"
            widget = QtWidgets.QListWidgetItem(QtGui.QIcon(icon), self.get_translation(group)['name'])
            widget.setData(0x0100, "separator")
            widget.setData(0x0101, group['id'])
            widget.setBackground(QtGui.QColor(169, 169, 169))
            block_list_widget.addItem(widget)
            # add elements
            for elem_id in group['elements']:
                widget = QtWidgets.QListWidgetItem(QtGui.QIcon(information[elem_id]['icon']),
                                                   self.get_translation(information[elem_id])['name'])
                widget.setData(0x0100, elem_id)
                widget.setData(0x0101, group['id'])
                block_list_widget.addItem(widget)
                # add tiles to fill menu
                if group['id'] in ("road", "block"):
                    default_fill.addItem(QtGui.QIcon(information[elem_id]['icon']),
                                         self.get_translation(information[elem_id])['name'], elem_id)
                    delete_fill.addItem(QtGui.QIcon(information[elem_id]['icon']),
                                        self.get_translation(information[elem_id])['name'], elem_id)

        default_fill.setCurrentText(self.get_translation(information["grass"])['name'])
        delete_fill.setCurrentText(self.get_translation(information["grass"])['name'])

        set_fill = self.ui.set_fill
        set_fill.clicked.connect(self.set_default_fill)

    def change_env(self):
        pass

    def center(self):
        pass

    #  Create a new map
    def open_map_triggered(self) -> None:
        self.map_api.open_map_triggered(self)

    def import_old_format(self):
        self.map_api.import_old_format()

    #  Open map
    def create_map_triggered(self) -> None:
        self.map_api.create_map_form()

    def create_region(self):
        pass

    def change_distortion_view_triggered(self):
        pass

    #  Save map
    def save_map_triggered(self):
        self.map_api.save_map_triggered()

    #  Save map as
    def save_map_as_triggered(self):
        self.map_api.save_map_as_triggered(self)

    #  Calculate map characteristics
    def calc_param_triggered(self):
        pass

    #  Help: About
    def about_author_triggered(self):
        pass

    def save_map_as_png(self):
        self.map_api.save_map_as_png(self)

    #  Exit
    def exit_triggered(self) -> None:
        self.map_api.exit_triggered(_translate, self)

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
    def quit_program_event(self, event: QEvent) -> None:
        self.exit_triggered()
        event.ignore()

    #  Handle a click on an item from a list to a list
    def item_list_clicked(self):
        pass

    #  Double click initiates as single click action
    def item_list_double_clicked(self) -> None:
        item_ui_list = self.ui.block_list
        item_name = item_ui_list.currentItem().data(0x0100)
        item_type = item_ui_list.currentItem().data(0x0101)
        self.map_api.item_list_double_clicked(self, item_name, item_type)

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
    def brush_mode(self) -> None:
        self.map_api.brush_mode(self.brush_button.isChecked())

    def selectionUpdate(self) -> None:
        self.map_api.selection_update(self.ui.default_fill.currentData())

    def trimClicked(self):
        pass

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self.map_api.key_press_event(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        self.map_api.key_release_event(event)

    def rotate_selected_tiles(self) -> None:
        self.map_api.rotate_selected_tiles()

    def update_debug_info(self, event: Dict[str, Any]) -> None:
        self.map_api.update_debug_info(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.map_api.scene_update()

    def set_default_fill(self, item_name: str) -> None:
        self.ui.default_fill.setCurrentText(
            self.get_translation(self.info_json['info'][item_name])['name'])

    def is_move_mode(self) -> bool:
        return self.map_api.is_move_mode()

    def change_obj_info(self, layer_name: str, name: str,
                        obj_conf: Dict[str, Any], frame: Dict[str, Any],
                        is_draggable: bool) -> None:
        self.map_api.change_obj_form(layer_name, name, obj_conf, frame,
                                     is_draggable)

    def view_info_form(self, header: str, info: str) -> None:
        self.map_api.view_info_form(header, info)
