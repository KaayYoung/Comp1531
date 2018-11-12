from flask import Flask
import config as Config

import os
import re

class Server(Flask):
    def __init__(self, name):
        super().__init__(name)
        self.config["SECRET_KEY"] = Config.config["SECRET_KEY"]
        self.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + Config.DB
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.url_map.strict_slashes = False

    def start(self):
        """Sets up server"""
        if (os.environ.get("WERKZEUG_RUN_MAIN") and os.environ.get("WERKZEUG_RUN_MAIN") == "true") or (os.environ.get("WERKZEUG_RUN_MAIN") == None and Config.debug == False):
            self.import_blueprints()

    def import_blueprints(self):
        """Imports all blueprints"""
        print(' * Importing blueprints')
        for file in os.listdir(os.fsencode(Config.basedir+'/app/controllers/')):
            filename = os.fsdecode(file)
            if filename.endswith(".py") and not re.match('^(\.|__|db)',filename):
                # View Controllers
                exec('from app.controllers.{0} import {0}_blueprint'.format(filename[:-3]))
                # Registers Views
                exec('self.register_blueprint({0}_blueprint)'.format(filename[:-3]))
                print('      {0}'.format(filename))

    # def check_login(self, username, )