# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "\\..\\..\\")
from flask import Flask
from loach.api import douyin, kuaishou
from loach.schedule import scheduler
from loach.setting import config
import logging.config

logging.config.dictConfig(config["LOGGING_CONFIG"])

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    # load extensions

    # load blueprints
    app.register_blueprint(douyin)
    app.register_blueprint(kuaishou)

    return app


scheduler.start()
app = create_app(config)
app.run(host='0.0.0.0', port=8080)

