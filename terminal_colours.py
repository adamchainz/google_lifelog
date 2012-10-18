# coding=utf-8
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'


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


