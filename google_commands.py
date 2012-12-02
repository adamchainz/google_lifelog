# coding=utf-8
from datetime import datetime, timedelta
from config import config
from utils import *

# From date.py in google
ACCEPTED_DAY_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def date_format(datetime):
    return datetime.strftime(ACCEPTED_DAY_TIME_FORMAT)


def google_cal_format(cal_str):
    # Remove header
    cal_str = re.sub(r'^\[.*\]$',
                     '',
                     cal_str,
                     flags=re.MULTILINE)

    cal_str = format_tags(cal_str)

    # Highlight event times
    def event_highlight(match):
        return okblue(match.group(2)) + "\t" + match.group(1)
    cal_str = re.sub(r'^(.+),([^,\n]+)$',
                    event_highlight,
                    cal_str,
                    flags=re.MULTILINE)

    return cal_str


def now_command(args):
    try:
        offset = int(args[0])
    except ValueError:
        offset = None
    if offset is not None:
        if len(args) == 1:
            print fail("Usage: now -5 \"Thinking\""), "- adds a 0-minute event 5 minutes ago"
            return
        now = date_format(datetime.now() + timedelta(minutes=offset))
        event = " ".join(args[1:])
    else:
        if len(args) == 0:
            print fail("Usage: now \"Thinking\""), "- adds a 0-minute event right now"
            return
        now = date_format(datetime.now())
        event = " ".join(args)

    no_length = "%s,%s" % (now, now)
    print format_tags(event)
    print run(['google', 'calendar', 'add', '-d', no_length, event], with_stderr=True)


def for_command(args):
    if len(args) < 2:
        print fail("Usage: for 10 \"Drinking\""), "- adds a 10 minute event right now"
        return
    now = date_format(datetime.now())
    later = date_format(datetime.now() + timedelta(minutes=int(args[0])))
    if later < now:
        (now, later) = (later, now)
    length = "%s,%s" % (now, later)
    event = " ".join(args[1:])
    print format_tags(event)
    print run(['google', 'calendar', 'add', '-d', length, event], with_stderr=True)


def quick_command(args):
    if len(args) == 0:
        print fail("Usage: quick \"tomorrow 7pm Pub with Andy\""), "- adds with google's quick-add syntax"
    else:
        event = " ".join(args)
        print format_tags(event)
        print run(['google', 'calendar', 'add', event], with_stderr=True)


def today_command(args):
    print google_cal_format(run(['google', 'calendar', 'today']))


def yesterday_command(args):
    minus_24 = datetime.now() - timedelta(hours=24)
    yesterday = datetime.strftime(minus_24, '%Y-%m-%d')
    print google_cal_format(run(['google', 'calendar', 'list', '-d', yesterday]))


def download_command(args):
    if len(args) > 0:
        print fail("I don't take any commands.")

    try:
        url = config.get('Google', 'ical_url')
    except:
        print fail("Couldn't find ical_url in config file")
        return

    try:
        filename = config.get('Local', 'ical_filename')
    except:
        print fail("Couldn't find ical_filename in config file")
        return

    ical = run(['curl', url])
    if ical > "":
        with open(filename, 'w') as fp:
            fp.write(ical)
        print header("Downloaded.")
    else:
        print fail("Failed to download.")


def popup_command(args):
    if len(args) < 2:
        print fail("Usage : l popup \"defaultanswer\" \"some event string that is also a prompt\"")
    answer = args[0]
    event = args[1:]
    event_string = " ".join(event)
    result = run(["osascript", "-e",
    """set answer to ""
    try
    tell app "SystemUIServer"
    set answer to text returned of (display dialog "%s" default answer "%s")
    end
    end
    activate app (path to frontmost application as text)
    answer
    """ % (event_string, answer)])
    result = result.strip()
    if result > "":
        event[-1] += result
        now_command(event)
