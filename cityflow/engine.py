from . import _cityflow
import threading
import webbrowser
import json
import time
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import os

STATICS_PATH = os.path.join(os.path.dirname(__file__), "render", "statics")
TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "render", "templates")

class Engine(_cityflow.Engine):
    rendered=False
    connect_num=0
    def __init__(self, config_file, thread_num, render_host = "0.0.0.0", render_port = 8080):
        super(Engine, self).__init__(config_file = config_file, thread_num = thread_num)
        self.host = render_host
        self.port = render_port

    def servre_launch(self):
        self.socketio.run(self.app, host=self.host, port=self.port)

    def server_init(self):

        self.app = Flask(__name__, template_folder=TEMPLATES_PATH)

        self.app.add_url_rule(rule="/", view_func=self.index)
        self.app.add_url_rule(rule="/statics/<path:path>", view_func=self.get_static_file)

        self.socketio = SocketIO(self.app)
        self.socketio.on_event('connect', self.handler_connected)
        self.socketio.on_event('disconnect', self.handler_disconnect)
        self.socketio.on_event('roadnet_finish', self.handler_roadnet_finish)
        self.socketio.on_event('update_finish', self.handler_update_finish)

        self.sem = threading.Semaphore(0)
        self.render_sem = threading.Semaphore(0)
        self.server_thread = threading.Thread(target=self.servre_launch)
        self.server_thread.setDaemon(True)
        self.server_thread.start()
        time.sleep(5) # wait for existing connections
        if self.connect_num <= 0:
            webbrowser.open("http://%s:%d/"%(self.host, self.port))
        print("wait for connect")
        self.sem.acquire()

    def index(self):
        return render_template('render.html', ws_addr="http://%s:%d" % (self.host, self.port))

    def handler_connected(self):
        print("Accepted a connection")
        self.connect_num += 1
        emit('load_roadnet', json.loads(self.roadnet_string()))

    def handler_roadnet_finish(self):
        self.sem.release()
        self.render_sem.acquire()
        emit('render', self.get_log())

    def handler_update_finish(self):
        self.sem.release()
        self.render_sem.acquire()
        emit('render', self.get_log())

    def handler_disconnect(self):
        self.connect_num -= 1
        print("disconnect")

    def render(self):
        if not self.rendered:
            self.rendered = True
            self.server_init()
        self.render_sem.release()
        self.sem.acquire()

    def get_static_file(self, path):
        return send_from_directory(STATICS_PATH, path)