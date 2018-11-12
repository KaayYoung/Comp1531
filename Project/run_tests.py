#!/usr/bin/env python3
import os
import sys
from shutil import copyfile
from pathlib import Path

import config as Config

class Colour:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    NORM = '\033[0m'
    BOLD = '\033[1m'
    WARNING = YELLOW
    FAIL = RED
    HEADER = PURPLE
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    # Checks if running from the right directory
    if not set(['run.py', 'app', 'database', 'data']).issubset(os.listdir('.')):
        print(Colour.FAIL + "ALERT: Tests not run. run_tests.py and tests.py need to be put in the same directory as run.py and the app folder. Read the README.md for more information." + Colour.NORM)
        sys.exit()


    to_restore = True

    # Prevents db corruption
    db_file = Path(Config.DB)
    if db_file.is_file():
        try:
            copyfile(Config.DB, Config.DB_BASE + "database.backup.db")
        except:
            to_restore = False
            print(Colour.FAIL + "Backup of non-test db failed!" + Colour.NORM)
        else:        
            print(Colour.GREEN + "Previous db backed up" + Colour.NORM)
    else:
        to_restore = False
        print(Colour.WARNING + "No non-test db to backup" + Colour.NORM)


    # Runs actual tests
    from tests import *
    run()


    # Cleans everything up after tests are done
    if to_restore:
        try:
            os.rename(Config.DB_BASE + "database.backup.db", Config.DB)
        except:
            print(Colour.ERROR + "Restore of non-test db failed!" + Colour.NORM)
        else:
            print(Colour.GREEN + "Previous db restored" + Colour.NORM)        
    else:
        os.remove(Config.DB)
        print(Colour.GREEN + "Test db cleaned up" + Colour.NORM)
