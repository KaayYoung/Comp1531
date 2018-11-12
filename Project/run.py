#!/usr/bin/env python3
import os
import sys
from pathlib import Path

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
        print(Colour.FAIL + "ALERT: Application start failed, incorrect configuration. Read the README.md for more information." + Colour.NORM)
        sys.exit()

    if '-h' in sys.argv or '--help' in sys.argv or (len(sys.argv) > 1 and \
        not ('-ld' in sys.argv or '--load-defaults' in sys.argv) and \
        not ('-df' in sys.argv or '--debug-features' in sys.argv) and \
        not ('-q' in sys.argv or '--quick-quit' in sys.argv)):
        try:
            with open("README.md", "r") as f:
                help_raw = f.read().split('#### Command-line arguments')[1].split('###')[0]
                help_proc = Colour.BOLD + " --- HELP ---\n" + Colour.NORM
                i = 0
                colouring = False
                while i < len(help_raw):
                    if help_raw[i] == '`':
                        if not colouring:
                            help_proc += Colour.BOLD
                            colouring = True
                        else:
                            help_proc += Colour.NORM
                            colouring = False
                        i += 3
                    elif help_raw[i] == '*':
                        help_proc += '\n ‣'
                        i += 1
                    elif help_raw[i] == '-':
                        try:
                            if help_raw[i+1] == '-':
                                help_proc += Colour.YELLOW + '--'
                                i += 2
                            else:
                                raise ValueError("Shouldn't be highlighted")
                        except:
                            help_proc += help_raw[i]
                            i += 1
                            pass
                    else:
                        help_proc += help_raw[i]
                        i += 1
        except:
            print(Colour.WARNING + "Find README.md for more information, auto-help failed." + Colour.NORM)
        else:
            os.system('clear')
            print(help_proc)
    else:
        from app import app
        import config as Config
        app.run(host='0.0.0.0', port=Config.port, debug=Config.debug)#, ssl_context=(Config.basedir+'/certificates/server.crt', Config.basedir+'/certificates/server.key'))