# coding=utf-8
import re
from collections import defaultdict
from datetime import datetime, date, time
from dateutil import zoneinfo
from dateutil.relativedelta import relativedelta
from functools import total_ordering
from icalendar import Calendar  # , vDate

from config import config

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
        self.description = vevent.get('description')

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
        out = okblue("%s - %s" % (start, end)) + "\t" + summary
        if self.description > '':
            out += '\n\t' + warning(self.description.replace('\n','\n\t'))
        return out


def get_events(filter_re=None):
    filename = config.get('Local', 'ical_filename')
    cal = Calendar.from_ical(open(filename, 'rb').read())

    # Search
    event_list = EventlyList()
    for ting in cal.walk("VEVENT"):
        ev = Evently(ting)
        if filter_re is None or \
           re.search(filter_re, ev.summary.lower(), flags=re.IGNORECASE):
            event_list.append(ev)
    return event_list


class EventlyList(list):

    def bucket(self, bucket_type):
        if not bucket_type in ['days', 'weeks']:
            raise ValueError("bucket_type must be days or weeks")

        bucketed = defaultdict(EventlyList)
        for ev in self:
            if bucket_type == 'weeks':
                key = ev.dtstart.date() - relativedelta(weekday=MO)
            elif bucket_type == 'days':
                key = ev.dtstart.date() - relativedelta(days=0)
            bucketed[key].append(ev)

        return bucketed
