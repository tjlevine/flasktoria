#!/usr/bin/env python3

import logging
import multiprocessing
import sys
import signal
import time


def load_config():
    from json import load
    with open("config.json") as fin:
        return load(fin)


# this is the entry point for the rest server
def rest_server(wsctl_dict):
    import os
    import connexion
    from flask import render_template
    from flask_cors import CORS

    log = logging.getLogger("flasktoria.rest")
    log.setLevel(logging.DEBUG)
    log.debug("starting rest server (pid is {})".format(os.getpid()))

    app = connexion.App(__name__, specification_dir='./swagger/')

    # enable CORS on all requests
    CORS(app.app)

    app.add_api('swagger.yaml', arguments={'title': 'API to support Project Victoria backend'})

    @app.app.route('/')
    def test():
        CFG = load_config()
        return render_template('websocket_test.html', ws_url=CFG["WS_URL"])
    
    app.run(port=8080)


# this is the entry point for the websocket server
def ws_server(wsctl_dict):
    logging.getLogger("flasktoria.ws").debug("starting ws server")
    import victoria_websocket

    victoria_websocket.ws_main(wsctl_dict)


# this is the main application entry point
if __name__ == '__main__':
    # set all loggers to debug level by default
    logging.basicConfig(level=logging.DEBUG)

    log = logging.getLogger("flasktoria.main")

    # wsctl message queue for communication between ws process and rest process
    mgr = multiprocessing.Manager()
    wsctl_dict = mgr.dict()

    # init and start the websocket process
    ws_process = multiprocessing.Process(target=ws_server, args=(wsctl_dict,))
    ws_process.start()

    # now start the rest server in it's own process
    rest_process = multiprocessing.Process(target=rest_server, args=(wsctl_dict,))
    rest_process.start()

    def sigterm_handler(signum, frame):
        log.info("Got sigterm, exiting")
        ws_process.terminate()
        ws_process.join()
        log.debug("WS process exited")
        rest_process.terminate()
        rest_process.join()
        log.debug("REST process exited")

    # set up a SIGTERM handler for quicker docker stops
    signal.signal(signal.SIGTERM, sigterm_handler)
