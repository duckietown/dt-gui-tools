from PyQt5 import QtCore
from PyQt5.QtGui import QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import QDialog, QGroupBox, QDialogButtonBox, QFormLayout, QVBoxLayout, \
    QLineEdit, QLabel
from forms.default_forms import get_info, create_form


class SaveImageForm(QDialog):
    send_info = QtCore.pyqtSignal(object)

    def __init__(self, default_height: int):
        super(SaveImageForm, self).__init__()
        self.setWindowTitle("Info for saving map image")
        self.formGroupBox = QGroupBox("Init info")
        self.image_name = QLineEdit(self)
        self.image_name.setText("image")
        self.height = QLineEdit(self)
        self.height.setText(f"{default_height}")
        self.height.setValidator(QIntValidator())
        self.width = QLabel("*compute automatically")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._get_info)
        self.buttonBox.rejected.connect(self.reject)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.formGroupBox)
        main_layout.addWidget(self.buttonBox)
        create_form(self, {"Image name": self.image_name, "Height": self.height,
                           "Width": self.width
                           })
        self.setLayout(main_layout)

    def _get_info(self):
        get_info(self, {'height': int(self.height.text()) if self.height.text() != "" else -1,
                        'image_name': self.image_name.text()}
                 )
