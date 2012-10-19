# coding=utf-8
import re
import sys
import subprocess
from terminal_colours import *
from django.utils.encoding import smart_str


def say(string):
    sys.stdout.write(smart_str(string))
    sys.stdout.flush()


def run(comm):
    proc = subprocess.Popen(comm,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output = proc.communicate()
    # Concat stdout & stderr, because we don't care
    return output[0]


def hash_parse(ev_str):
    # Because I can't type hash on terminal.
    return ev_str.replace('--', '#')


def format_tags(str):
    def tag_highlight(match):
        return header(match.group(0))

    return re.sub(r'\#\w+\b',
                  tag_highlight,
                  str,
                  flags=re.MULTILINE)
