from . import _cityflow

from flask import Flask
from flask_socketio import SocketIO

class Engine(_cityflow.Engine):
    rendered=False
    def server_init(self):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)
        self.socketio.on_event("message", self.handle_message)
        self.socketio.run(self.app)
        # TODO
    def render(self):
        # TODO
        if not self.rendered:
            self.server_init()
        print("output")

    @staticmethod
    def handle_message(msg):
        print("received message: " + msg)