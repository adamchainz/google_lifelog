# coding=utf-8
import re
from collections import defaultdict
from datetime import datetime, date, time, timedelta
from icalendar import Calendar  # , vDate
from config import config
from utils import *
from dateutil import zoneinfo
from dateutil.relativedelta import *

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
                re.search(filter_re,
                          ting.get('summary').lower(),
                          flags=re.IGNORECASE):
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


def list_command(args):
    if len(args) > 1:
        print fail("Only up to 1 arg : a filter_re")
        return

    filter_re = args[0] if len(args) == 1 else None

    for ev in sort_events(get_events(filter_re)):
        say(format_event(ev) + "\n")


def sum_time_command(args):
    if len(args) < 1:
        print fail("Only 1 arg : a filter_re")
        return

    filter_re = " ".join(args)

    time_sum = timedelta(0)
    for ev in sort_events(get_events(filter_re)):
        time_sum += (ev.get('dtend').dt - ev.get('dtstart').dt)
    print time_sum


def bucket_command(args):
    if len(args) < 3:
        print fail("bucket (days|weeks) (num|time|var) filter_re")
        return

    time_len = args[0]

    sum_var = args[1]

    filter_re = " ".join(args[2:])

    events = sort_events(get_events(filter_re))

    if sum_var == 'num':
        sum_dict = defaultdict(int)
    elif sum_var == 'time':
        sum_dict = defaultdict(timedelta)
    elif sum_var == 'mg':
        sum_re = re.compile('\\b(\\d+)mg\\b', flags=re.IGNORECASE)
        sum_dict = defaultdict(int)
    else:
        sum_re = re.compile('\\b%s=(\\d+)\\b' % sum_var, flags=re.IGNORECASE)
        sum_dict = defaultdict(int)

    for ev in events:
        if time_len == 'weeks':
            day = ev.get('dtstart').dt.date()
            key = day - relativedelta(weekday=MO)
        elif time_len == 'days':
            key = ev.get('dtstart').dt.date() - relativedelta(days=0)

        print format_event(ev)

        if sum_var == 'num':
            val = 1
        elif sum_var == 'time':
            val = ev.get('dtend').dt - ev.get('dtstart').dt
        else:
            # var fallback
            match = sum_re.search(str(ev.get('summary')))
            try:
                val = int(match.group(1))
            except AttributeError:
                print fail(format_event(ev) + " has no %s" % sum_var)
                val = 0

        sum_dict[key] += val

    # output
    if time_len == 'weeks':
        gap = timedelta(days=7)
    else:
        gap = timedelta(days=1)

    last = sorted(sum_dict)[-1]
    i = sorted(sum_dict)[0]
    while True:
        val = sum_dict.get(i, "")
        print "%s\t%s" % (okblue(str(i)), val)
        i += gap
        if i > last:
            break
