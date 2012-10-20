# coding=utf-8
import re
from datetime import datetime, date, time, timedelta
from icalendar import Calendar  # , vDate
from config import config
from utils import *
from dateutil import zoneinfo

# http://icalendar.readthedocs.org/en/latest/examples.html

DEFAULT_TZINFO = zoneinfo.gettz("Europe/London")


def get_events(filter_re=None):
    filename = config.get('Local', 'ical_filename')
    cal = Calendar.from_ical(open(filename, 'rb').read())

    # Search
    event_list = []
    for ting in cal.walk():
        if ting.name == "VEVENT":
            if filter_re is None or \
                re.search(filter_re, ting.get('summary').lower()):
                event_list.append(ting)
    return event_list


def sort_events(event_list, ascending=True):
    def event_cmp(x, y):
        x_t = x.get('dtstart').dt
        if type(x_t) == date:
            x_t = datetime.combine(x_t, time(0, tzinfo=DEFAULT_TZINFO))
        y_t = y.get('dtstart').dt
        if type(y_t) == date:
            y_t = datetime.combine(y_t, time(0, tzinfo=DEFAULT_TZINFO))

        if x_t.tzinfo is None:
            x_t = datetime.replace(x_t, tzinfo=DEFAULT_TZINFO)

        if y_t.tzinfo is None:
            y_t = datetime.replace(y_t, tzinfo=DEFAULT_TZINFO)

        c = cmp(x_t, y_t)
        if not ascending:
            c *= -1
        return c

    return sorted(event_list, event_cmp)


def format_event(event):
    start = event.get('dtstart').dt.strftime('%b %d %H:%M')
    end = event.get('dtend').dt.strftime('%b %d %H:%M')
    summary = format_tags(event.get('summary'))
    return okblue("%s - %s" % (start, end)) + "\t" + summary


class ListCommand(object):
    def run(self, args):
        if len(args) > 1:
            print fail("Only up to 1 arg : a filter_re")
            return

        filter_re = args[0] if len(args) == 1 else None

        for ev in sort_events(get_events(filter_re)):
            say(format_event(ev) + "\n")


class SumTimeCommand(object):
    def run(self, args):
        if len(args) > 1:
            print fail("Only up to 1 arg : a filter_re")
            return

        filter_re = args[0] if len(args) == 1 else None

        time_sum = timedelta(0)
        for ev in sort_events(get_events(filter_re)):
            time_sum += (ev.get('dtend').dt - ev.get('dtstart').dt)
        print time_sum
