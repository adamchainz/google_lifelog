# coding=utf-8
import re
from collections import defaultdict
from datetime import timedelta
from dateutil import zoneinfo
from dateutil.relativedelta import *

from utils import *
from local_calendar import get_events


DEFAULT_TZINFO = zoneinfo.gettz("Europe/London")


def list_command(args):
    if len(args) == 0:
        print fail("1 arg : a filter_re")
        return

    filter_re = " ".join(args)

    for ev in get_events(filter_re):
        say(ev.output() + "\n")


def sum_time_command(args):
    if len(args) < 1:
        print fail("Only 1 arg : a filter_re")
        return

    filter_re = " ".join(args)

    time_sum = timedelta(0)
    for ev in get_events(filter_re):
        time_sum += (ev.dtend - ev.dtstart)
    print time_sum, "= {:0.2f} hours".format(time_sum.total_seconds() / 3600)


def hash_tags_command(args):
    if len(args) > 0:
        print fail("No args.")
        return

    events = get_events()
    tags = defaultdict(int)

    for ev in events:
        hash_tags = re.findall('\#\w+', ev.summary)
        for tag in hash_tags:
            tags[tag] += 1

    tags = [(tag, tags[tag]) for tag in tags]
    tags = sorted(tags, key=lambda x:-x[1])

    for tag in tags:
        print format_tags("%s\t%i" % (tag[0], tag[1]))


def bucket_command(args):
    if len(args) < 3:
        print fail("bucket (days|weeks) (num|time|var) filter_re")
        return

    time_len = args[0]

    sum_var = args[1]

    filter_re = " ".join(args[2:])

    events = get_events(filter_re)

    if sum_var == 'num':
        sum_dict = defaultdict(int)
        default = 0
    elif sum_var == 'time':
        sum_dict = defaultdict(timedelta)
        default = timedelta(hours=0)
    elif sum_var == 'minutes':
        sum_dict = defaultdict(int)
        default = 0
    elif sum_var == 'mg':
        sum_re = re.compile('\\b(\\d+)mg\\b', flags=re.IGNORECASE)
        sum_dict = defaultdict(int)
        default = 0
    else:
        sum_re = re.compile('\\b%s=(\\d+)\\b' % sum_var, flags=re.IGNORECASE)
        sum_dict = defaultdict(int)
        default = 0

    for ev in events:
        if time_len == 'weeks':
            key = ev.dtstart.date() - relativedelta(weekday=MO)
        elif time_len == 'days':
            key = ev.dtstart.date() - relativedelta(days=0)

        if sum_var == 'num':
            val = 1
        elif sum_var == 'time':
            val = ev.dtend - ev.dtstart
        elif sum_var == 'minutes':
            val = ev.dtend - ev.dtstart
            val = val.seconds / 60
        else:
            # var fallback
            match = sum_re.search(str(ev.summary))
            try:
                val = int(match.group(1))
            except AttributeError:
                print fail(ev.output() + " has no %s" % sum_var)
                val = 0

        sum_dict[key] += val

    # output
    if time_len == 'weeks':
        gap = timedelta(days=7)
    else:
        gap = timedelta(days=1)

    if len(sum_dict) == 0:
        print "No events"
        return

    last = sorted(sum_dict)[-1]
    i = sorted(sum_dict)[0]
    while True:
        val = sum_dict.get(i, default)
        print "%s\t%s" % (okblue(str(i)), val)
        i += gap
        if i > last:
            break
