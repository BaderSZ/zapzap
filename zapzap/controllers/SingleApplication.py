from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSignal, Qt, QTextStream

from PyQt6.QtNetwork import QLocalServer, QLocalSocket
import sys


class SingleApplication(QApplication):
    messageReceived = pyqtSignal(str)

    def __init__(self, appid, *argv):
        super(SingleApplication, self).__init__(*argv)
        self._appid = appid
        self._activationWindow = None
        self._activateOnMessage = False
        self._outSocket = QLocalSocket()
        self._outSocket.connectToServer(self._appid)
        self._isRunning = self._outSocket.waitForConnected()
        self._outStream = None
        self._inSocket = None
        self._inStream = None
        self._server = None
        self.window = None

        if self._isRunning:
            self._outStream = QTextStream(self._outSocket)
            sys.exit(0)
        else:
            error = self._outSocket.error()
            if error == QLocalSocket.LocalSocketError.ConnectionRefusedError:
                self.close()
                QLocalServer.removeServer(self._appid)
            self._outSocket = None
            self._server = QLocalServer()
            self._server.listen(self._appid)
            self._server.newConnection.connect(self._onNewConnection)

    def close(self):
        if self._inSocket:
            self._inSocket.disconnectFromServer()
        if self._outSocket:
            self._outSocket.disconnectFromServer()
        if self._server:
            self._server.close()

    def isRunning(self):
        return self._isRunning

    def appid(self):
        return self._appid

    def activationWindow(self):
        return self._activationWindow

    def setActivationWindow(self, activationWindow, activateOnMessage=True):
        self._activationWindow = activationWindow
        self._activateOnMessage = activateOnMessage

    def activateWindow(self):
        if not self._activationWindow:
            return
        self._activationWindow.setWindowState(
            self._activationWindow.windowState() & ~Qt.WindowState.WindowMinimized)
        self._activationWindow.raise_()
        self._activationWindow.activateWindow()

    def sendMessage(self, msg):
        if not self._outStream:
            return False
        # noinspection PyUnresolvedReferences
        self._outStream << msg << '\n'
        self._outStream.flush()
        return self._outSocket.waitForBytesWritten()

    def _onNewConnection(self):
        self.window.show()
        self.alert(self.window)
        self.activateWindow()
        """if self._inSocket:
            self._inSocket.readyRead.disconnect(self._onReadyRead)
        self._inSocket = self._server.nextPendingConnection()
        if not self._inSocket:
            return
        self._inStream = QTextStream(self._inSocket)
        self._inSocket.readyRead.connect(self._onReadyRead)
        if self._activateOnMessage:
            self.activateWindow()"""
        
    def _onReadyRead(self):
        while True:
            msg = self._inStream.readLine()
            if not msg:
                break
            self.messageReceived.emit(msg)

    def setWindow(self, window):
        self.window = window