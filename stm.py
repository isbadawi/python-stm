"""
This is a little script that scrapes the STM website for bus schedules.
"""
import argparse
import urllib
from pyquery import PyQuery as pq

def get_schedule(route, stop, direction, day):
    base_url = 'http://www2.stm.info/taz/horaire.php?'
    params = {
        'l': route,
        't': stop,
        'd': direction if direction != 'W' else 'O',
        'lng': 'a',
    }
    url = '%s%s' % (base_url, urllib.urlencode(params))

    # this is just ugly scraping arrived at by inspection
    d = pq(url=url)('td').filter(lambda i: pq(this).text() == day.title())
    if not d:
        return None
    lines = d.parent().next().find('td').text().split('\n')
    mid = lines[len(lines)/2]
    hour, minute = mid.strip().split(' ', 1)
    hours = [h.strip(' \n\th') for h in lines[:len(lines)/2]]
    hours.append(hour[:-1])
    minutes = [m.strip() for m in lines[len(lines)/2 + 1:]]
    minutes.insert(0, minute)
    minutes = [tuple(m.strip('*+>min') for m in l.split()) for l in minutes]
    return zip(hours, minutes)

def _build_parser():
    parser = argparse.ArgumentParser(description='command line interface to stm.info')
    parser.add_argument('-r', '--route', required=True, metavar='#',
        help='route number (e.g. 68)')
    parser.add_argument('-s', '--stop', required=True, metavar='#',
        help='stop number (e.g. 58003)')
    parser.add_argument('-d', '--direction', choices=tuple('NEWS'),
        required=True, help='direction (e.g. E for east)')
    parser.add_argument('--day', choices=('weekday', 'saturday', 'sunday'),
        default='weekday', help='day of the week')
    return parser

if __name__ == '__main__':
    args = _build_parser().parse_args()
    table = get_schedule(**vars(args))
    if table is None:
        print 'no schedule available'
    else:
        for hour, minutes in table:
            for minute in minutes:
                print '%s:%s' % (hour, minute),
            print
