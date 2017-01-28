#!/usr/bin/env python3

import logging
import multiprocessing


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
    #logging.basicConfig(level=logging.DEBUG)

    # wsctl message queue for communication between ws process and rest process
    mgr = multiprocessing.Manager()
    wsctl_dict = mgr.dict()

    logging.debug('Setting key "test" in wsctl_dict to "it\'s bad"')
    wsctl_dict['test'] = "it's bad"

    # init and start the websocket process
    ws_process = multiprocessing.Process(target=ws_server, args=(wsctl_dict,))
    ws_process.start()

    # now start the rest server in the current process
    rest_server(wsctl_dict)
