# coding=utf-8
import scipy
import re
from collections import Counter, defaultdict
from datetime import date, timedelta
from dateutil import zoneinfo
from dateutil.relativedelta import *

from utils import *
from local_calendar import get_events


DEFAULT_TZINFO = zoneinfo.gettz("Europe/London")


def num_events_command(args):
    print len(get_events())


def list_command(args):
    if len(args) == 0:
        print fail("1 arg : a filter_re")
        return

    filter_re = " ".join(args)

    for ev in get_events(filter_re):
        print ev


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
    tags = Counter()

    for ev in events:
        hash_tags = re.findall('\#\w+', ev.summary)
        tags.update(hash_tags)

    for (tag, count) in sorted(tags.items(), key=lambda x:-x[1]):
        print format_tags("%s\t%i" % (tag, count))


def bucket_command(args):
    if len(args) < 3:
        print fail("bucket (days|weeks) (num|time|var) filter_re")
        return

    time_len = args[0]

    sum_var = args[1]

    filter_re = " ".join(args[2:])

    events = get_events(filter_re)

    if len(events) == 0:
        print fail("No events")
        return

    bucketed = events.bucket(time_len)

    # output
    if time_len == 'months':
        gap = relativedelta(months=1)
    elif time_len == 'weeks':
        gap = relativedelta(weeks=1)
    else:
        gap = relativedelta(days=1)

    last = sorted(bucketed)[-1]
    i = sorted(bucketed)[0]
    while True:
        val = bucketed[i].get_sum_var(sum_var)
        print "%s\t%s" % (okblue(str(i)), val)
        i += gap
        if i > last:
            break


def sleep_analysis_command(args):
    if len(args):
        print fail("no args")
        return

    all_events = get_events()

    # + 2 hours to push into the next day
    offset = timedelta(hours=2)
    sleeps = all_events.filter("#sleep\\b")
    sleeps = sleeps.bucket('days', offset=offset)

    melatonins = all_events.filter("#drugs\\b").filter("melatonin")
    melatonins = melatonins.bucket('days', offset=offset)

    max_bucket = max(max(sleeps.keys()), max(melatonins.keys()))

    start_date = date(2012, 9, 12)
    melatonin_pops = defaultdict(list)

    i = start_date
    gap = timedelta(days=1)
    while i <= max_bucket:
        mel_mg = melatonins[i].get_sum_var('mg')
        sleep_minutes = sleeps[i].get_sum_var('minutes')
        melatonin_pops[mel_mg].append(sleep_minutes)
        i += gap

    print header("melatonin mg\tmins asleep mean\tmins asleep std dev\tn")
    for x in melatonin_pops:
        pop = melatonin_pops[x]
        print "%s\t%0.0f\t%0.0f\t%s" % \
            (x, scipy.mean(pop), scipy.std(pop), len(pop))

