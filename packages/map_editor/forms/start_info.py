from PyQt5 import QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog, QGroupBox, QDialogButtonBox, QFormLayout, QVBoxLayout, \
    QLineEdit, QLabel
from forms.default_forms import get_info, create_form
from utils.constants import TILE_TYPES
from utils.qtWindowAPI import add_combobox


class NewMapInfoForm(QDialog):
    send_info = QtCore.pyqtSignal(object)

    def __init__(self, map_dir: str):
        super(NewMapInfoForm, self).__init__()
        self.setWindowTitle("Info for initialization of map")
        self.formGroupBox = QGroupBox("Init info")
        self.nameXEdit = QLineEdit(self)
        self.nameXEdit.setText("5")
        self.nameXEdit.setValidator(QIntValidator())
        self.nameYEdit = QLineEdit(self)
        self.nameYEdit.setText("5")
        self.nameYEdit.setValidator(QIntValidator())
        self.nameTileSizeXEdit = QLineEdit(self)
        self.nameTileSizeXEdit.setText("0.585")
        self.nameTileSizeYEdit = QLineEdit(self)
        self.nameTileSizeYEdit.setText("0.585")
        self.nameMap = QLineEdit(self)
        self.nameMap.setText("map_1")
        self.nameDirEdit = QLineEdit(self)
        self.nameDirEdit.setText(f"{map_dir}/maps/map1")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._get_info)
        self.buttonBox.rejected.connect(self.reject)
        self.comboboxes = {}
        self.info = {"types": {}}
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.formGroupBox)
        main_layout.addWidget(self.buttonBox)
        layout = create_form(self, {"Width": self.nameXEdit, "Height": self.nameYEdit,
                "Tile width": self.nameTileSizeXEdit,
                "Tile height": self.nameTileSizeYEdit, "Map name": self.nameMap,
                "Folder": self.nameDirEdit})
        add_combobox(self, TILE_TYPES, "default_tile", "asphalt", layout)
        self.setLayout(main_layout)

    def _get_info(self):
        get_info(self, {
            'x': self.nameXEdit.text(),
            'y': self.nameYEdit.text(),
            'tile_width': self.nameTileSizeXEdit.text(),
            'tile_height': self.nameTileSizeYEdit.text(),
            'dir_name': self.nameDirEdit.text(),
            'map_name': self.nameMap.text(),
            'default_fill': self.comboboxes["default_tile"].currentText()
        })
