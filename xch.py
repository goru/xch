#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import argparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from time import sleep
import re
from urllib.parse import urljoin

def http_get(
    url,
    headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"},
    encoding="cp932"):

    request = Request(url, None, headers)
    html = None
    error = None

    try:
        response = urlopen(request)
    except HTTPError as e:
        error = e
    except URLError as e:
        error = e
    else:
        html = response.read().decode(encoding, errors="replace")

    return (html, error)

def pass_surrogate_pair(string):
    if string:
        # http://imagawa.hatenadiary.jp/entry/2016/12/25/193000
        return string.encode("utf-16", "surrogatepass").decode("utf-16")
    else:
        return ""

class Bbs:
    def __init__(self, title, url):
        self.title = title
        self.url = url

    def __str__(self):
        return "{0}: {1}".format(self.title, self.url)

    @staticmethod
    def from_bs4_element(element):
        return Bbs(pass_surrogate_pair(element.string), element["href"])

class Thread:
    def __init__(self, number, title, response, url):
        self.number = number
        self.title = title
        self.response = response
        self.url = url

    def __str__(self):
        return "{0}: {1} ({2}): {3}".format(self.number, self.title, self.response, self.url)

    @staticmethod
    def from_bs4_element(base_url, element):
        m = re.match("([0-9]+): (.*) \(([0-9]+)\)", pass_surrogate_pair(element.string))
        if m:
            return Thread(
                int(m.group(1)),
                m.group(2),
                int(m.group(3)),
                urljoin(urljoin(base_url, element["href"]), "."))
        else:
            return None

class Response:
    def __init__(self, number, name, email, date, uid, message):
        self.number = number
        self.name = name
        self.email = email
        self.date = date
        self.uid = uid
        self.message = message

    def __str__(self):
        return "{0} {1} [{2}] {3} {4}\n{5}".format(self.number, self.name, self.email, self.date, self.uid, self.message)

    @staticmethod
    def from_bs4_element(number, name, email, date, uid, escaped):
        list(map(lambda x: x.unwrap(), escaped.find_all("a")))
        message = "\n".join(BeautifulSoup(str(escaped), "html.parser").stripped_strings)

        return Response(
            int(number.string),
            pass_surrogate_pair(name.string),
            pass_surrogate_pair(email["href"].replace("mailto:", "") if email else ""),
            pass_surrogate_pair(date.string),
            pass_surrogate_pair(uid.string),
            pass_surrogate_pair(message))

def command_bbsmenu(args):
    html, error = http_get(args.url)
    if not html or error:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.find_all("a", href=re.compile("http://[^.]+\.(\dch\.net)|(bbspink\.com)/[^/]+/"))
    bbsmenu = [Bbs.from_bs4_element(e) for e in elements]

    for b in bbsmenu:
        print(b)

    return bbsmenu

def command_subback(args):
    url = "{0}/subback.html".format(args.url)
    html, error = http_get(url)
    if not html or error:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    base_url = urljoin(url, soup.find("base")["href"])
    elements = soup.find_all("a", href=re.compile("[0-9]+/l50"))
    subback = [Thread.from_bs4_element(base_url, e) for e in elements]

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

            rrange = "{0}-n".format(thread[-1].number)
            skip = 1

        if interval: 
            sleep(interval)
        else:
            break

def get_thread(url, rrange, skip):
    html, error = http_get("{0}/{1}".format(url, rrange))
    if not html or error:
        return []

    # parse partially (to ignore invalid tag storucture)
    number = BeautifulSoup(html, "html.parser", parse_only=SoupStrainer("span", class_="number")).contents
    name = BeautifulSoup(html, "html.parser", parse_only=SoupStrainer("span", class_="name")).contents
    date = BeautifulSoup(html, "html.parser", parse_only=SoupStrainer("span", class_="date")).contents
    uid = BeautifulSoup(html, "html.parser", parse_only=SoupStrainer("span", class_="uid")).contents
    escaped = BeautifulSoup(html, "html.parser", parse_only=SoupStrainer("span", class_="escaped")).contents
    thread = [Response.from_bs4_element(number[i], name[i], name[i].find("a"), date[i], uid[i], escaped[i]) for i in range(len(number))]

    return thread

def command_help(args):
    print(args)

# main parser
parser = argparse.ArgumentParser(description="xch command")
subparsers = parser.add_subparsers()

# bbsmenu
parser_bbsmenu = subparsers.add_parser("bbsmenu", help="see `bbsmenu -h`")
parser_bbsmenu.add_argument("-u", "--url", required=True, help="https://menu.xch.net/bbsmenu.html")
parser_bbsmenu.set_defaults(handler=command_bbsmenu)

# subback
parser_subback = subparsers.add_parser("subback", help="see `subback -h`")
parser_subback.add_argument("-u", "--url", required=True, help="http://xxx.xch.net/xxx/")
parser_subback.add_argument("--exclude-end", action='store_true', required=False, help="exclude 1001")
parser_subback.set_defaults(handler=command_subback)

# thread
parser_thread = subparsers.add_parser("thread", help="see `thread -h`")
parser_thread.add_argument("-u", "--url", required=True, help="http://xxx.xch.net/test/read.cgi/xxx/0000000000/")
parser_thread.add_argument("-r", "--range", required=False, default="l50", help="start position and range for reading. l50 (default), 100-200, 100-n")
parser_thread.add_argument("-i", "--interval", type=int, required=False, help="if this option is specified, will reload in specified sec.")
parser_thread.set_defaults(handler=command_thread)

# help
parser_help = subparsers.add_parser("help", help="see `help -h`")
parser_help.add_argument("command", help="command name which help is shown")
parser_help.set_defaults(handler=command_help)

args = parser.parse_args()
if hasattr(args, "handler"):
    args.handler(args)
else:
    parser.print_help()
