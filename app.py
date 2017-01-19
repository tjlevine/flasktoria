#!/usr/bin/env python3

import connexion
import logging
import flask_socketio
import threading
import time
import websocket

if __name__ == '__main__':
    con_logger = logging.getLogger('connexion.app')
    con_logger.setLevel(logging.DEBUG)
    con_logger.addHandler(logging.StreamHandler())

    app = connexion.App(__name__, specification_dir='./swagger/', server='gevent')
    app.add_api('swagger.yaml', arguments={'title': 'API to support Project Victoria backend'})
    socketio = flask_socketio.SocketIO()
    socketio.init_app(app.app)
    socketio.start_background_task(websocket.emit_loop, socketio)
    app.run(port=8080)
