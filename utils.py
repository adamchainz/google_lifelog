# coding=utf-8
import re
import sys
import subprocess
from terminal_colours import *


def say(str):
    sys.stdout.write(str)
    sys.stdout.flush()


def run(comm):
    proc = subprocess.Popen(comm,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output = proc.communicate()
    # Concat stdout & stderr, because we don't care
    return output[0] + "\n" + output[1]


def hash_parse(ev_str):
    # Because I can't type hash on terminal.
    return ev_str.replace('--', '#')


def cal_format(cal_str):

    # Highlight hashtags
    def tag_highlight(match):
        return header(match.group(0))

    cal_str = re.sub(r'\#\w+\b',
                    tag_highlight,
                    cal_str,
                    flags=re.MULTILINE)

    # Highlight event times
    def event_highlight(match):
        return okblue(match.group(2)) + "\t" + match.group(1)
    cal_str = re.sub(r'^(.+),([^,\n]+)$',
                    event_highlight,
                    cal_str,
                    flags=re.MULTILINE)

    return cal_str
