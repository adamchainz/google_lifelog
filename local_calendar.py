# coding=utf-8
import re
from collections import defaultdict
from datetime import datetime, date, time, timedelta
from dateutil import zoneinfo
from dateutil.relativedelta import relativedelta, MO
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

    def filter(self, filter_re, inverse=False):
        filtered_list = EventlyList()
        for ev in self:
            matches = bool(re.search(filter_re, ev.summary.lower(), flags=re.IGNORECASE))
            if matches != inverse:
                filtered_list.append(ev)

        filtered_list.sort()

        return filtered_list

    def exclude(self, filter_re):
        return self.filter(filter_re, inverse=True)

    def bucket(self, bucket_type, offset=None):
        if not bucket_type in ['days', 'weeks']:
            raise ValueError("bucket_type must be days or weeks")

        bucketed = defaultdict(EventlyList)
        for ev in self:
            start = ev.dtstart
            if offset:
                start += offset

            if bucket_type == 'weeks':
                key = start.date() - relativedelta(weekday=MO)
            elif bucket_type == 'days':
                key = start.date() - relativedelta(days=0)
            bucketed[key].append(ev)

        return bucketed

    def get_sum_var(self, sum_var):
        if sum_var == 'time':
            total = timedelta(hours=0)
        else:
            total = 0

        if sum_var == 'mg':
            sum_re = '([0-9.]+)mg\\b'
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
                    val = float(match.group(1))
                except AttributeError:
                    print fail("%s has no %s" % (ev, sum_var))
                    val = 0

            total += val

        return total


def get_events(filter_re=None):
    filename = config.get('Local', 'ical_filename')
    cal = Calendar.from_ical(open(filename, 'rb').read())

    # Search
    event_list = EventlyList()
    for ting in cal.walk("VEVENT"):
        event_list.append(Evently(ting))

    if filter_re:
        event_list = event_list.filter(filter_re)

    event_list.sort()

    return event_list
