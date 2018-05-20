#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import re
from urllib.parse import urljoin

def pass_surrogate_pair(string):
    if string:
        # http://imagawa.hatenadiary.jp/entry/2016/12/25/193000
        return string.encode('utf-16', 'surrogatepass').decode('utf-16')
    else:
        return ''

class Bbs:
    def __init__(self, title, url):
        self.title = title
        self.url = url

    def __str__(self):
        return '{0}: {1}'.format(self.title, self.url)

    @staticmethod
    def from_bs4_element(element):
        return Bbs(pass_surrogate_pair(element.string), element['href'])

class Thread:
    def __init__(self, number, title, response, url):
        self.number = number
        self.title = title
        self.response = response
        self.url = url

    def __str__(self):
        return '{0}: {1} ({2}): {3}'.format(self.number, self.title, self.response, self.url)

    @staticmethod
    def from_bs4_element(base_url, element):
        m = re.match('([0-9]+): (.*) \(([0-9]+)\)', pass_surrogate_pair(element.string))
        if m:
            return Thread(
                int(m.group(1)),
                m.group(2),
                int(m.group(3)),
                urljoin(urljoin(base_url, element['href']), '.'))
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
        return '{0} {1} [{2}] {3} {4}\n{5}'.format(self.number, self.name, self.email, self.date, self.uid, self.message)

    @staticmethod
    def from_bs4_element(number, name, email, date, uid, escaped):
        list(map(lambda x: x.unwrap(), escaped.find_all('a')))
        message = '\n'.join(BeautifulSoup(str(escaped), 'html.parser').stripped_strings)

        return Response(
            int(number.string),
            pass_surrogate_pair(name.string),
            pass_surrogate_pair(email['href'].replace('mailto:', '') if email else ''),
            pass_surrogate_pair(date.string),
            pass_surrogate_pair(uid.string),
            pass_surrogate_pair(message))
