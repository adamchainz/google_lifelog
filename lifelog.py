# coding=utf-8
import sys
import re
import subprocess
from datetime import datetime, timedelta
from utils import *

commands = {}
for module in ['google_commands', 'local_commands']:
    mod = __import__(module)
    for d in dir(mod):
        obj = getattr(mod, d)
        if d.endswith("Command"):
            name = obj.__name__
            # remove "Command"
            name = name[:-7]
            # snake case
            name = re.sub('([A-Z])', '_\\1', name)
            name = name.lower()[1:]
            # store
            commands[name] = obj


if __name__ == '__main__':
    if len(sys.argv) < 2:
        say(header("Subcommands: "))
        print ", ".join([c for c in commands])
        sys.exit()

    subcommand = sys.argv[1]
    if subcommand in commands:
        commands[subcommand]().run(sys.argv[2:])
    else:
        print fail("That command does not exist")
