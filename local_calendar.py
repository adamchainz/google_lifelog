# coding=utf-8
import re
from functools import total_ordering
from datetime import datetime, date, time
from dateutil import zoneinfo
from config import config
from icalendar import Calendar  # , vDate

from utils import *

# http://icalendar.readthedocs.org/en/latest/examples.html

DEFAULT_TZINFO = zoneinfo.gettz("Europe/London")


@total_ordering
class Evently(object):
    """
    Wrapper for iCalendar events
    """
    def __init__(self, vevent):
        self.dtstart = vevent.get('dtstart').dt
        self.dtend = vevent.get('dtend').dt
        self.summary = vevent.get('summary')

        # Normalize start/end to be datetime objects
        for att in ('dtstart', 'dtend'):
            fixed = getattr(self, att)
            if type(fixed) == date:
                fixed = datetime.combine(fixed, time(0, tzinfo=DEFAULT_TZINFO))

            if fixed.tzinfo is None:
                fixed = datetime.replace(fixed, tzinfo=DEFAULT_TZINFO)

            setattr(self, att, fixed)

    def __eq__(self, other):
        return self.dtstart == other.dtstart

    def __le__(self, other):
        return self.dtstart <= other.dtstart

    def __str__(self):
        start = self.dtstart.strftime('%b %d %H:%M')
        end = self.dtend.strftime('%b %d %H:%M')
        summary = format_tags(self.summary)
        return okblue("%s - %s" % (start, end)) + "\t" + summary


def get_events(filter_re=None):
    filename = config.get('Local', 'ical_filename')
    cal = Calendar.from_ical(open(filename, 'rb').read())

    # Search
    event_list = []
    for ting in cal.walk("VEVENT"):
        ev = Evently(ting)
        if filter_re is None or \
           re.search(filter_re, ev.summary.lower(), flags=re.IGNORECASE):
            event_list.append(ev)
    return sorted(event_list)
