# coding=utf-8
import scipy
import re
from collections import Counter, defaultdict, OrderedDict
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

    # -20 hours to pull back all of tomorrow's sleep into today
    all_sleeps = all_events.filter("#sleep\\b")

    sleeps = all_sleeps.bucket('days', offset=timedelta(hours=-20))

    naps = all_sleeps.filter(r'^nap\b') \
                 .bucket('days', offset=timedelta(hours=-20))

    all_drugs = all_events.filter(r"#drugs\b")

    melatonins = all_drugs.filter("melatonin") \
                          .bucket('days', offset=timedelta(hours=-2))

    alcohols = all_drugs.filter(r"#alcohol\b") \
                        .bucket('days', offset=timedelta(hours=-6))

    caffeines = all_drugs.filter(r'#caffeine\b') \
                         .bucket('days')

    fast_days = all_events.filter(r'^fast day\b') \
                          .bucket('days')

    # Summarize

    start_date = date(2012, 9, 12)
    end_date = date.today() - timedelta(days=1)  # Up to yesterday
    days = []

    the_date = start_date
    while the_date <= end_date:
        sleep_mins = sleeps[the_date].get_sum_var('minutes')
        nap_mins = naps[the_date].get_sum_var('minutes')

        is_fast_day = (the_date in fast_days)
        alone = not (len(sleeps[the_date].filter('with')) > 0)

        # Store
        # Ignore days where night time sleep was not recorded
        if sleep_mins > 60:
            day = OrderedDict()
            day['Date'] = the_date
            day['Minutes Sleeping'] = sleep_mins
            day['Minutes Napping'] = nap_mins
            day['Minutes Normal Sleep'] = sleep_mins - nap_mins
            day['Alone?'] = 'Yes' if alone else 'No'
            day['Fasting?'] = 'Yes' if is_fast_day else 'No'
            day['Melatonin mg'] = melatonins[the_date].get_sum_var('mg')
            day['Units of Alcohol'] = alcohols[the_date].get_sum_var('units')
            day['Caffeine mg'] = caffeines[the_date].get_sum_var('mg')
            days.append(day)

        the_date += timedelta(days=1)

    # Output

    header_keys = days[0].keys()
    print header('\t'.join(header_keys))
    for day in days:
        print "\t".join([str(day[x]) for x in day])


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


def inhaler_analysis_command(args):
    if len(args):
        print fail("no args!")
        return

    inhalers = get_events('^inhaler').bucket('weeks')

    start_date = date(2012, 6, 25)  # when logs looked sane
    end_date = date.today() - timedelta(days=1)  # up to yesterday
    end_date += relativedelta(weekday=MO, weeks=-1)
    weeks = []

    the_date = start_date
    while the_date <= end_date:
        week = OrderedDict()
        week['Monday'] = the_date
        week['Num Inhalers'] = inhalers[the_date].get_sum_var('num')
        week['Num Inhalers w/o exercise'] = inhalers[the_date].exclude('exercise').get_sum_var('num')
        weeks.append(week)
        the_date += timedelta(days=7)

    header_keys = weeks[0].keys()
    print header('\t'.join(header_keys))
    for week in weeks:
        print "\t".join([str(week[x]) for x in week])
