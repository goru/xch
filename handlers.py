#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from time import sleep
import re
from urllib.parse import urljoin

import classes

def http_get(
    url,
    headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'},
    encoding='cp932'):

    request = Request(url, None, headers)
    body = None
    error = None

    try:
        response = urlopen(request)
    except HTTPError as e:
        error = e
    except URLError as e:
        error = e
    else:
        body = response.read().decode(encoding, errors='replace')

    return (body, error)

def command_bbsmenu(args):
    html, error = http_get(args.url)
    if not html or error:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.find_all('a', href=re.compile('http://[^.]+\.(\dch\.net)|(bbspink\.com)/[^/]+/'))
    bbsmenu = [classes.Bbs.from_bs4_element(e) for e in elements]

    for b in bbsmenu:
        print(b)

    return bbsmenu

def command_subback(args):
    url = '{0}/subback.html'.format(args.url)
    html, error = http_get(url)
    if not html or error:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    base_url = urljoin(url, soup.find('base')['href'])
    elements = soup.find_all('a', href=re.compile('[0-9]+/l50'))
    subback = [classes.Thread.from_bs4_element(base_url, e) for e in elements]

    for s in subback:
        if s.response < 1001:
            print(s)
        else:
            if not args.exclude_end:
                print(s)

    return subback

def command_thread(args):
    url = args.url
    rrange = args.range
    interval = args.interval
    skip = 0

    while True:
        thread = get_thread(url, rrange, skip)[skip:]

        if len(thread) > 0:
            for t in thread:
                print(t)
                print()

            if thread[-1].number == 1002:
                break

            rrange = '{0}-n'.format(thread[-1].number)
            skip = 1

        if interval: 
            sleep(interval)
        else:
            break

def get_thread(url, rrange, skip):
    html, error = http_get('{0}/{1}'.format(url, rrange))
    if not html or error:
        return []

    # parse partially (to ignore invalid tag storucture)
    number = BeautifulSoup(html, 'html.parser', parse_only=SoupStrainer('span', class_='number')).contents
    name = BeautifulSoup(html, 'html.parser', parse_only=SoupStrainer('span', class_='name')).contents
    date = BeautifulSoup(html, 'html.parser', parse_only=SoupStrainer('span', class_='date')).contents
    uid = BeautifulSoup(html, 'html.parser', parse_only=SoupStrainer('span', class_='uid')).contents
    escaped = BeautifulSoup(html, 'html.parser', parse_only=SoupStrainer('span', class_='escaped')).contents
    thread = [classes.Response.from_bs4_element(number[i], name[i], name[i].find('a'), date[i], uid[i], escaped[i]) for i in range(len(number))]

    return thread

def command_help(args):
    print(args)
