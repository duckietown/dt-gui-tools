# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_design.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1028, 650)
        MainWindow.setMinimumSize(QtCore.QSize(950, 650))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(238, 238, 236))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(238, 238, 236))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(238, 238, 236))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(238, 238, 236))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        MainWindow.setPalette(palette)
        MainWindow.setAutoFillBackground(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(136, 138, 133))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(136, 138, 133))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(136, 138, 133))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(136, 138, 133))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.centralwidget.setPalette(palette)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1028, 22))
        self.menubar.setObjectName("menubar")
        self.file = QtWidgets.QMenu(self.menubar)
        self.file.setObjectName("file")
        self.maps = QtWidgets.QMenu(self.menubar)
        self.maps.setObjectName("maps")
        self.help = QtWidgets.QMenu(self.menubar)
        self.help.setObjectName("help")
        self.settings = QtWidgets.QMenu(self.menubar)
        self.settings.setObjectName("settings")
        self.utils = QtWidgets.QMenu(self.menubar)
        self.utils.setObjectName("utils")
        self.menuDbl = QtWidgets.QMenu(self.menubar)
        self.menuDbl.setObjectName("menuDbl")
        MainWindow.setMenuBar(self.menubar)
        self.tool_bar = QtWidgets.QToolBar(MainWindow)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.tool_bar.setPalette(palette)
        self.tool_bar.setObjectName("tool_bar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.tool_bar)
        self.block_widget = QtWidgets.QDockWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.block_widget.sizePolicy().hasHeightForWidth())
        self.block_widget.setSizePolicy(sizePolicy)
        self.block_widget.setMinimumSize(QtCore.QSize(274, 107))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.block_widget.setPalette(palette)
        self.block_widget.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.block_widget.setAcceptDrops(True)
        self.block_widget.setAutoFillBackground(True)
        self.block_widget.setFloating(False)
        self.block_widget.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
        self.block_widget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea|QtCore.Qt.TopDockWidgetArea)
        self.block_widget.setObjectName("block_widget")
        self.dockWidgetContents = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents.setSizePolicy(sizePolicy)
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.block_list = QtWidgets.QListWidget(self.dockWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.block_list.sizePolicy().hasHeightForWidth())
        self.block_list.setSizePolicy(sizePolicy)
        self.block_list.setObjectName("block_list")
        self.verticalLayout_2.addWidget(self.block_list)
        self.block_widget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.block_widget)
        self.info_widget = QtWidgets.QDockWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.info_widget.sizePolicy().hasHeightForWidth())
        self.info_widget.setSizePolicy(sizePolicy)
        self.info_widget.setMinimumSize(QtCore.QSize(175, 250))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.info_widget.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setItalic(False)
        self.info_widget.setFont(font)
        self.info_widget.setAcceptDrops(False)
        self.info_widget.setAutoFillBackground(True)
        self.info_widget.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
        self.info_widget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea|QtCore.Qt.TopDockWidgetArea)
        self.info_widget.setObjectName("info_widget")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.info_browser = QtWidgets.QTextBrowser(self.dockWidgetContents_2)
        self.info_browser.setAutoFillBackground(False)
        self.info_browser.setObjectName("info_browser")
        self.verticalLayout.addWidget(self.info_browser)
        self.info_widget.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.info_widget)
        self.layer_info_widget = QtWidgets.QDockWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.layer_info_widget.sizePolicy().hasHeightForWidth())
        self.layer_info_widget.setSizePolicy(sizePolicy)
        self.layer_info_widget.setMinimumSize(QtCore.QSize(100, 200))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.layer_info_widget.setPalette(palette)
        self.layer_info_widget.setAutoFillBackground(True)
        self.layer_info_widget.setFloating(False)
        self.layer_info_widget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.layer_info_widget.setObjectName("layer_info_widget")
        self.dockWidgetContents_4 = QtWidgets.QWidget()
        self.dockWidgetContents_4.setObjectName("dockWidgetContents_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.dockWidgetContents_4)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.layer_tree = QtWidgets.QTreeView(self.dockWidgetContents_4)
        self.layer_tree.setObjectName("layer_tree")
        self.verticalLayout_4.addWidget(self.layer_tree)
        self.layer_info_widget.setWidget(self.dockWidgetContents_4)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.layer_info_widget)
        self.map_info_widget = QtWidgets.QDockWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.map_info_widget.sizePolicy().hasHeightForWidth())
        self.map_info_widget.setSizePolicy(sizePolicy)
        self.map_info_widget.setMinimumSize(QtCore.QSize(183, 200))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(211, 215, 207))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.map_info_widget.setPalette(palette)
        self.map_info_widget.setAutoFillBackground(True)
        self.map_info_widget.setFloating(False)
        self.map_info_widget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.map_info_widget.setObjectName("map_info_widget")
        self.dockWidgetContents_3 = QtWidgets.QWidget()
        self.dockWidgetContents_3.setObjectName("dockWidgetContents_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.default_fill_label = QtWidgets.QLabel(self.dockWidgetContents_3)
        self.default_fill_label.setObjectName("default_fill_label")
        self.verticalLayout_3.addWidget(self.default_fill_label)
        self.default_fill = QtWidgets.QComboBox(self.dockWidgetContents_3)
        self.default_fill.setObjectName("default_fill")
        self.verticalLayout_3.addWidget(self.default_fill)
        self.delete_fill_label = QtWidgets.QLabel(self.dockWidgetContents_3)
        self.delete_fill_label.setObjectName("delete_fill_label")
        self.verticalLayout_3.addWidget(self.delete_fill_label)
        self.delete_fill = QtWidgets.QComboBox(self.dockWidgetContents_3)
        self.delete_fill.setObjectName("delete_fill")
        self.verticalLayout_3.addWidget(self.delete_fill)
        self.set_fill = QtWidgets.QPushButton(self.dockWidgetContents_3)
        self.set_fill.setObjectName("set_fill")
        self.verticalLayout_3.addWidget(self.set_fill)
        self.map_info_widget.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.map_info_widget)
        self.open_map = QtWidgets.QAction(MainWindow)
        self.open_map.setObjectName("open_map")
        self.save_map = QtWidgets.QAction(MainWindow)
        self.save_map.setObjectName("save_map")
        self.export_png = QtWidgets.QAction(MainWindow)
        self.export_png.setObjectName("export_png")
        self.calc_param = QtWidgets.QAction(MainWindow)
        self.calc_param.setEnabled(True)
        self.calc_param.setObjectName("calc_param")
        self.calc_materials = QtWidgets.QAction(MainWindow)
        self.calc_materials.setEnabled(True)
        self.calc_materials.setObjectName("calc_materials")
        self.save_map_as = QtWidgets.QAction(MainWindow)
        self.save_map_as.setObjectName("save_map_as")
        self.exit = QtWidgets.QAction(MainWindow)
        self.exit.setObjectName("exit")
        self.change_blocks = QtWidgets.QAction(MainWindow)
        self.change_blocks.setCheckable(True)
        self.change_blocks.setChecked(True)
        self.change_blocks.setMenuRole(QtWidgets.QAction.TextHeuristicRole)
        self.change_blocks.setObjectName("change_blocks")
        self.change_info = QtWidgets.QAction(MainWindow)
        self.change_info.setCheckable(True)
        self.change_info.setChecked(True)
        self.change_info.setObjectName("change_info")
        self.create_new = QtWidgets.QAction(MainWindow)
        self.create_new.setObjectName("create_new")
        self.change_map = QtWidgets.QAction(MainWindow)
        self.change_map.setCheckable(True)
        self.change_map.setChecked(True)
        self.change_map.setObjectName("change_map")
        self.about_author = QtWidgets.QAction(MainWindow)
        self.about_author.setObjectName("about_author")
        self.distortion_view = QtWidgets.QAction(MainWindow)
        self.distortion_view.setObjectName("distortion_view")
        self.region_create = QtWidgets.QAction(MainWindow)
        self.region_create.setObjectName("region_create")
        self.change_layer = QtWidgets.QAction(MainWindow)
        self.change_layer.setCheckable(True)
        self.change_layer.setChecked(True)
        self.change_layer.setObjectName("change_layer")
        self.file.addAction(self.create_new)
        self.file.addAction(self.open_map)
        self.file.addAction(self.save_map)
        self.file.addAction(self.save_map_as)
        self.file.addSeparator()
        self.file.addAction(self.export_png)
        self.file.addSeparator()
        self.file.addAction(self.exit)
        self.maps.addAction(self.calc_param)
        self.maps.addAction(self.calc_materials)
        self.help.addAction(self.about_author)
        self.settings.addAction(self.distortion_view)
        self.utils.addAction(self.region_create)
        self.menuDbl.addAction(self.change_blocks)
        self.menuDbl.addAction(self.change_info)
        self.menuDbl.addAction(self.change_map)
        self.menuDbl.addAction(self.change_layer)
        self.menubar.addAction(self.file.menuAction())
        self.menubar.addAction(self.menuDbl.menuAction())
        self.menubar.addAction(self.maps.menuAction())
        self.menubar.addAction(self.help.menuAction())
        self.menubar.addAction(self.settings.menuAction())
        self.menubar.addAction(self.utils.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Map Builder"))
        self.file.setTitle(_translate("MainWindow", "File"))
        self.maps.setTitle(_translate("MainWindow", "Map Info"))
        self.help.setTitle(_translate("MainWindow", "Help"))
        self.settings.setTitle(_translate("MainWindow", "Settings"))
        self.utils.setTitle(_translate("MainWindow", "Utils"))
        self.menuDbl.setTitle(_translate("MainWindow", "View"))
        self.tool_bar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.block_widget.setWindowTitle(_translate("MainWindow", "Maps, signs, and objects"))
        self.info_widget.setWindowTitle(_translate("MainWindow", "Description"))
        self.layer_info_widget.setWindowTitle(_translate("MainWindow", "Layers"))
        self.map_info_widget.setWindowTitle(_translate("MainWindow", "Map editor"))
        self.default_fill_label.setText(_translate("MainWindow", "Default fill"))
        self.delete_fill_label.setText(_translate("MainWindow", "Fill when deleted"))
        self.set_fill.setText(_translate("MainWindow", "Set"))
        self.open_map.setText(_translate("MainWindow", "Open map"))
        self.open_map.setToolTip(_translate("MainWindow", "Open *.yaml map"))
        self.open_map.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.save_map.setText(_translate("MainWindow", "Save map"))
        self.save_map.setToolTip(_translate("MainWindow", "Save current map"))
        self.save_map.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.export_png.setText(_translate("MainWindow", "Export to PNG"))
        self.export_png.setShortcut(_translate("MainWindow", "Ctrl+P"))
        self.calc_param.setText(_translate("MainWindow", "Calculate map characteristics"))
        self.calc_materials.setText(_translate("MainWindow", "Calculate map materials"))
        self.save_map_as.setText(_translate("MainWindow", "Save map as"))
        self.save_map_as.setShortcut(_translate("MainWindow", "Ctrl+Alt+S"))
        self.exit.setText(_translate("MainWindow", "Exit"))
        self.change_blocks.setText(_translate("MainWindow", "Blocks"))
        self.change_info.setText(_translate("MainWindow", "Object description"))
        self.create_new.setText(_translate("MainWindow", "New map"))
        self.create_new.setToolTip(_translate("MainWindow", "Create new map"))
        self.create_new.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.change_map.setText(_translate("MainWindow", "Map Editor"))
        self.about_author.setText(_translate("MainWindow", "About"))
        self.distortion_view.setText(_translate("MainWindow", "Distortion View"))
        self.region_create.setText(_translate("MainWindow", "Create Region"))
        self.region_create.setShortcut(_translate("MainWindow", "Ctrl+D"))
        self.change_layer.setText(_translate("MainWindow", "Layers"))
