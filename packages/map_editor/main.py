# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon

from mainWindow import DuckWindow
from argparse import ArgumentParser
from utils.logger import init_logger
from utils.window import get_available_translations

logger = init_logger()

LANG_DIR = './resources/lang/qm'


def init_translator(app, path):
    translator = QTranslator(app)
    translator.load(path)
    app.installTranslator(translator)


def main(args):
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon("./img/icons/duckie.ico"))

    # Install translator
    init_translator(app, args.locale_path)

    # Create main window
    window = DuckWindow(args)

    window.show()
    app.exec_()


if __name__ == '__main__':
    available_locales = get_available_translations(LANG_DIR)
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action="store_true", default=True,  help="Debug mode")
    parser.add_argument('-l', '--locale', choices=available_locales, default='en', help="App locale")
    parser.add_argument('-w', '--wkdir', default=".", help="Current dir for display")

    args = parser.parse_args()
    args.locale_path = available_locales[args.locale]

    main(args)
