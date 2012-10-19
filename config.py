# coding=utf-8
import os
import ConfigParser

CONFIG_PATH = os.path.expanduser("~/.lifelog")

defaults = {}
config = ConfigParser.RawConfigParser(defaults)
if os.path.exists(CONFIG_PATH):
    config.read(CONFIG_PATH)
