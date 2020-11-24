# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtQml import *

class Authentication(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._isAuth = False

    adminUsername = str("admin")
    adminPassword = str("admin")

    def setAuth(self, value):
        self._isAuth = value

    @Slot(result=bool)
    def isAuth(self):
        return self._isAuth


    @Slot(str, str)
    def authenticate(self, username, password):
        if (username == self.adminUsername) and (password == self.adminPassword):
            isAuth = True
        else:
            isAuth = False
        self.setAuth(isAuth)


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    qmlRegisterType(Authentication, 'Authentication', 1, 0, 'Authentication')
    engine = QQmlApplicationEngine()
    engine.load(os.path.join(os.path.dirname(__file__), "main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
