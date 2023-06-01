from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtWidgets


#  MessageBox to exit
def quit_message_box(_translate, window: QtWidgets.QMainWindow):
    reply = QMessageBox(window)
    reply.setIcon(QMessageBox.Question)
    reply.setWindowTitle(_translate("MainWindow", "Exit"))
    reply.setText(_translate("MainWindow", "Exit"))
    reply.setInformativeText(_translate("MainWindow", "Save and exit?"))
    reply.setStandardButtons(
        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
    reply.setDefaultButton(QMessageBox.Save)
    ret = reply.exec()
    return ret
