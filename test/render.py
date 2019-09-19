import threading
import webbrowser
import logging
import cityflow
import json
import time
from flask import Flask, render_template, session, request, send_from_directory
from flask_socketio import SocketIO, emit

class Engine(cityflow.Engine):
    rendered=False
    def servre_launch(self):
        self.socketio.run(self.app, host=self.host, port=self.port)

    def server_init(self, host = "0.0.0.0", port = 8080):
        self.host = host
        self.port = port

        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'secret!'

        self.app.add_url_rule(rule="/", view_func=self.index)
        self.app.add_url_rule(rule="/statics/<path:path>", view_func=self.library)

        self.socketio = SocketIO(self.app)
        self.socketio.on_event('connect', self.handler_connected)
        self.socketio.on_event('roadnet_finish', self.handler_roadnet_finish)
        self.socketio.on_event('update_finish', self.handler_update_finish)

        self.sem = threading.Semaphore(0)
        self.render_sem = threading.Semaphore(0)
        self.server_thread = threading.Thread(target=self.servre_launch)
        self.server_thread.start()
        webbrowser.open("http://%s:%d/"%(host, port))
        print("wait for connect")
        self.sem.acquire()
        print("stage 1")

    def index(self):
        return render_template('render.html', ws_addr="http://%s:%d" % (self.host, self.port))

    def handler_connected(self):
        print("Accepted a connection")
        emit('load_roadnet', json.loads(self.roadnet_string()))
        # emit('render', self.get_log())
        print("roadnet sent")

    def handler_roadnet_finish(self):
        print("roadnet drawn")
        print(self.get_log())
        self.sem.release()
        self.render_sem.acquire()
        emit('render', self.get_log())
        print("update sent")

    def handler_update_finish(self):
        print("update finish")
        self.sem.release()
        self.render_sem.acquire()
        emit('render', self.get_log())
        print("update sent")

    def render(self):
        print("call render")
        self.render_sem.release()
        self.sem.acquire()

    def library(self, path):
        return send_from_directory('statics/', path)


if __name__ == '__main__':
    eng = Engine(config_file="config/config.json", thread_num=4)
    eng.server_init()

    for i in range(10000):
        eng.next_step()
        eng.render()
        print("rendered",i)
        time.sleep(0.05)