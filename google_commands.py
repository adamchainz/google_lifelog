# coding=utf-8
from datetime import datetime, timedelta
from config import config
from utils import *

# From date.py in google
ACCEPTED_DAY_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def date_format(datetime):
    return datetime.strftime(ACCEPTED_DAY_TIME_FORMAT)


def google_cal_format(cal_str):
    # Remove header
    cal_str = re.sub(r'^\[.*\]$',
                     '',
                     cal_str,
                     flags=re.MULTILINE)

    cal_str = format_tags(cal_str)

    # Highlight event times
    def event_highlight(match):
        return okblue(match.group(2)) + "\t" + match.group(1)
    cal_str = re.sub(r'^(.+),([^,\n]+)$',
                    event_highlight,
                    cal_str,
                    flags=re.MULTILINE)

    return cal_str


class NowCommand(object):
    def run(self, args):
        if len(args) == 0:
            print fail("Usage: add \"Thinking\""), "- adds a 0-minute event right now"
            return
        now = date_format(datetime.now())
        no_length = "%s,%s" % (now, now)
        event = " ".join(args)
        event = hash_parse(event)
        print format_tags(event)
        print run(['google', 'calendar', 'add', '-d', no_length, event], with_stderr=True)


class ForCommand(object):
    def run(self, args):
        if len(args) < 2:
            print fail("Usage: for 10 \"Drinking\""), "- adds a 10 minute event right now"
            return
        now = date_format(datetime.now())
        later = date_format(datetime.now() + timedelta(minutes=int(args[0])))
        length = "%s,%s" % (now, later)
        event = " ".join(args[1:])
        event = hash_parse(event)
        print run(['google', 'calendar', 'add', '-d', length, event], with_stderr=True)


class QuickCommand(object):
    def run(self, args):
        if len(args) == 0:
            print fail("Usage: quick \"tomorrow 7pm Pub with Andy\""), "- adds with google's quick-add syntax"
        else:
            event = " ".join(args)
            event = hash_parse(event)
            print format_tags(event)
            print run(['google', 'calendar', 'add', event], with_stderr=True)


class TodayCommand(object):
    def run(self, args):
        print google_cal_format(run(['google', 'calendar', 'today']))


class YesterdayCommand(object):
    def run(self, args):
        minus_24 = datetime.now() - timedelta(hours=24)
        yesterday = datetime.strftime(minus_24, '%Y-%m-%d')
        print google_cal_format(run(['google', 'calendar', 'list', '-d', yesterday]))


class DownloadCommand(object):
    def run(self, args):
        if len(args) > 0:
            print fail("I don't take any commands.")

        try:
            url = config.get('Google', 'ical_url')
        except:
            print fail("Couldn't find ical_url in config file")
            return

        try:
            filename = config.get('Local', 'ical_filename')
        except:
            print fail("Couldn't find ical_filename in config file")
            return

        ical = run(['curl', url])
        with open(filename, 'w') as fp:
            fp.write(ical)
        print "Downloaded."
