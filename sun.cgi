#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 sts=4 ff=unix ft=python expandtab

import os
import sys
import json
import re
import traceback
import requests
import codecs


class GyazoScraper(object):
    content = None
    gyazo_image_re = '<meta content="(http://i.gyazo.com/([0-9a-z\.]+))" name="twitter:image" />'

    def __init__(self, url=None):
        self.gyazo_image_re = re.compile(self.gyazo_image_re)
        if url is not None:
            self.fetch(url)

    def fetch(self, url):
        self.content = None
        headers = {
            "User-Agent": r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        }
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == requests.codes.ok:
                self.content = r.content
            else:
                self.content = '?:' + str(r.status_code)
        except Exception:
            self.content = traceback.format_exc()

    def get_image_url(self):
        m = self.gyazo_image_re.search(self.content)
        if m and m.group():
            return m.group(1)
        else:
            return None


class NotSubculture(object):
    debug = True
    body = None
    message = None
    texts = None
    dic = {'^subculture$': 'No',
           '\(sun\)': u'☀',
           u'^サブ(では)?$': '?',
           u'^はい$': u'はい',
           u'さすが\s?kuzuha\s?(さん)?(は)?': u'わかるなー',
           u'JAL\s?123': u'なるほど',
           u'鐵道?(では)?$': u'おっ',
           u'拝承': u'拝復',
           u'^(クソ|糞)すぎる$': u'ごめん',
           }

    def __init__(self):
        self.httpheaderHasAlreadySent = False

    def httpheader(self, header="Content-Type: text/plain; charset=UTF-8\n"):
        if self.httpheaderHasAlreadySent is False:
            print header
            self.httpheaderHasAlreadySent = True

    def read_http_post(self, method, http_post_body):
        if self.body is None and method == 'POST':
            self.body = http_post_body
            try:
                self.message = json.loads(self.body)
            except Exception:
                if self.debug:
                    self.httpheader()
                    print traceback.format_exc()
                    sys.exit(0)
                else:
                    self.httpheader()
                    print "json decode error:", self.body
                    sys.exit(0)
            self.slice_message()

    def slice_message(self):
        if self.message is None:
            return
        self.texts = []
        for n in self.message['events']:
            if 'text' in n['message']:
                self.texts.append(n['message']['text'])

    def response(self):
        self.httpheader()
        if self.texts is not None:
            for t in self.texts:
                if "http://gyazo.com/" in t:
                    g = GyazoScraper(t)
                    url = g.get_image_url()
                    if url:
                        yield url
                else:
                    for k, v in self.dic.iteritems():
                        pattern = re.compile(k)
                        m = pattern.search(t)
                        if m:
                            yield pattern.sub(v, t)


if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

    no = NotSubculture()
    post_body = sys.stdin.read()
    no.read_http_post(os.environ.get('REQUEST_METHOD'), post_body)
    for r in no.response():
        print r
