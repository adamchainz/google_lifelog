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

    def get_sum_var(self, sum_var):
        if sum_var == 'time':
            total = timedelta(hours=0)
        else:
            total = 0

        if sum_var == 'mg':
            sum_re = '\\b(\\d+)mg\\b'
        elif sum_var not in ('num', 'time', 'minutes'):
            sum_re = '\\b%s=(\\d+)\\b' % sum_var

        for ev in self:
            if sum_var == 'num':
                val = 1
            elif sum_var == 'time':
                val = ev.dtend - ev.dtstart
            elif sum_var == 'minutes':
                val = ev.dtend - ev.dtstart
                val = val.seconds / 60
            else:
                # var fallback
                match = re.search(sum_re, ev.summary)
                try:
                    val = int(match.group(1))
                except AttributeError:
                    print fail(ev + " has no %s" % sum_var)
                    val = 0

            total += val

        return total


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

    event_list.sort()

    return event_list
