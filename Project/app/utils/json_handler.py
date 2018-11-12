from flask import Blueprint
from flask_login import UserMixin, login_user

from datetime import datetime
from pathlib import Path
from collections import namedtuple

import config as Config
# import app.controllers.login as Login
# import app.classes as Class

import json
import os
import sys
import inspect
import uuid
import time
import sqlite3

def gen_id():
    return uuid.uuid4().urn[9:]

class ObjectEncoder(json.JSONEncoder):
    """
    Generic object encoder borrowed from https://stackoverflow.com/a/35483750
    """
    def default(self, obj):
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
            )
            return self.default(d)
        return obj

def build_path(filename):
    return Config.basedir + '/data/' + filename + '.json'

def file_exists(filename):
    target = build_path(filename)
    if Path(target).exists() and os.path.getsize(target) > 0:
        return True
    else:
        return False

def load_object(filename):
    target = build_path(filename)

    if Path(target).exists() and os.path.getsize(target) > 0:
        with open(target, 'r') as input:
                return json.load(input)

def save_object(obj, filename):
    target = build_path(filename)

    # Builds required directory structure for file to be saved
    try:
        Path('/'.join(target.split('/')[:-1])).mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass

    with open(target, 'w') as output:
        json.dump(obj, output, cls=ObjectEncoder, sort_keys=True, indent=4, separators=(',', ': '))
