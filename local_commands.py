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

    from collections import namedtuple

    all_events = get_events()

    # -26 hours to pull back into today
    sleeps = all_events.filter("#sleep\\b")
    sleeps = sleeps.bucket('days', offset=timedelta(hours=-26))

    drugs = all_events.filter(r"#drugs\b")

    melatonins = drugs.filter("melatonin")
    melatonins = melatonins.bucket('days', offset=timedelta(hours=-2))

    alcohols = drugs.filter(r"#alcohol\b")
    alcohols = alcohols.bucket('days', offset=timedelta(hours=-6))

    SleepRow = namedtuple('SleepRow', ('date', 'sleep_mins', 'mel_mg', 'alcohol_units'))

    days = []

    start_date = date(2012, 9, 12)
    end_date = date.today() - timedelta(days=1)  # any sleep minutes from today are for yesterday

    i = start_date
    while i <= end_date:
        day = SleepRow(
                date=i,
                mel_mg=melatonins[i].get_sum_var('mg'),
                sleep_mins=sleeps[i].get_sum_var('minutes'),
                alcohol_units=alcohols[i].get_sum_var('units')
            )

        # Ignore days where night time sleep was not recorded
        if day.sleep_mins > 60:
            days.append(day)

        i += timedelta(days=1)

    print header("date\tmins asleep\tmelatonin mg\talcohol units")
    for day in days:
        print "\t".join([str(x) for x in day])


def alcohol_analysis_command(args):
    if len(args):
        print fail("no args")
        return

    alcohols = get_events(r'#alcohol\b')
    bucketed = alcohols.bucket('days', offset=timedelta(hours=-4))

    weekday_bucket = defaultdict(list)

    for day in bucketed:
        weekday = day.strftime('%A')
        units_this_day = bucketed[day].get_sum_var('units')
        weekday_bucket[weekday].append(units_this_day)

    print header("Day\tUnits mean\tUnits std dev\tTotal")
    for day in ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'):
        pop = weekday_bucket[day]
        print "{0}\t{1:0.0f}\t{2:0.2f}\t{3:0.1f}". format(day, scipy.mean(pop), scipy.std(pop), sum(pop))


def maybe_bad_alcohols_command(args):
    if len(args):
        print fail("no args")
        return

    alcohols = get_events(r'\b(vodka|gin|beer|wine|G&T|champagne)\b')
    for ev in alcohols:
        if not re.search(r'units=', ev.summary):
            print ev
