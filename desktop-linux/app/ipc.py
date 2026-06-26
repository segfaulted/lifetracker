import sys
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

SOCKET_NAME = "tasktracker_tray_client_ipc"

class IPCManager(QObject):
    toggle_requested = pyqtSignal(str)  # Emits "tasks" or "meds"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.server = None

    @staticmethod
    def send_toggle_command(target: str) -> bool:
        """
        Attempts to connect to an existing server instance and send a toggle command.
        Returns True if successful (meaning another instance was running), False otherwise.
        """
        socket = QLocalSocket()
        socket.connectToServer(SOCKET_NAME)
        if socket.waitForConnected(500):
            socket.write(f"toggle-{target}".encode('utf-8'))
            socket.waitForBytesWritten(500)
            socket.disconnectFromServer()
            return True
        return False

    def start_server(self) -> bool:
        """
        Starts the QLocalServer. Cleans up any orphaned socket files if necessary.
        Returns True if successful, False if it failed to listen.
        """
        # Clean up any leftover socket file from a crash
        QLocalServer.removeServer(SOCKET_NAME)
        
        self.server = QLocalServer(self)
        self.server.newConnection.connect(self._handle_new_connection)
        
        if not self.server.listen(SOCKET_NAME):
            print(f"[IPC] Failed to start local server: {self.server.errorString()}", file=sys.stderr)
            return False
            
        print(f"[IPC] Listening for toggle signals on local socket: '{SOCKET_NAME}'")
        return True

    def _handle_new_connection(self):
        socket = self.server.nextPendingConnection()
        if socket:
            socket.readyRead.connect(lambda: self._read_socket(socket))

    def _read_socket(self, socket: QLocalSocket):
        if socket.bytesAvailable() > 0:
            data = socket.readAll().data().decode('utf-8', errors='ignore')
            if "toggle-tasks" in data:
                self.toggle_requested.emit("tasks")
            elif "toggle-meds" in data:
                self.toggle_requested.emit("meds")
            elif "toggle" in data:
                self.toggle_requested.emit("tasks")
            socket.disconnectFromServer()
