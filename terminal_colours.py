# coding=utf-8
import sys
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

if sys.stdout.isatty():
    def header(str):
        return HEADER + str + ENDC

    def fail(str):
        return FAIL + str + ENDC

    def warning(str):
        return WARNING + str + ENDC

    def okblue(str):
        return OKBLUE + str + ENDC

    def okgreen(str):
        return OKGREEN + str + ENDC

else:
    def header(str):
        return str

    def fail(str):
        return str

    def warning(str):
        return str

    def okblue(str):
        return str

    def okgreen(str):
        return str

