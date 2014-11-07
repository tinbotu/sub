#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 sts=4 ff=unix ft=python expandtab

import os
import sys
import json
import re
import traceback


class gyazo_scraper(object):
    import requests
    content = None

    def __init__(self, url=None):
        self.gyazo_image_re = re.compile('<meta content="(http://i.gyazo.com/([0-9a-z\.]+))" name="twitter:image" />')
        if url is not None:
            self.fetch(url)

    def fetch(self, url):
        self.content = '??????????'
        headers = {
            "User-Agent": r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        }
        try:
            r = self.requests.get(url, headers=headers)
            if r.status_code == self.requests.codes.ok:
                self.content = r.content
            else:
                self.content = '?', str(r.status_code)
        except Exception:
            self.content = traceback.format_exc()

    def getContent(self):
        return self.content

    def getImageUrl(self):
        m = self.gyazo_image_re.search(self.content)
        if m and m.group():
            return m.group(1)
        else:
            return self.content


class notsubculture(object):

    debug = True
    body = None
    message = None
    texts = None
    dic = {'subculture': 'No', u'サブ': '?', }

    def __init__(self):
        self.httpheaderHasAlreadySent = False

    def httpheader(self, header="Content-Type: text/plain\n"):
        if self.httpheaderHasAlreadySent is False:
            print header
            self.httpheaderHasAlreadySent = True

    def read_http_post(self):
        if self.body is None and os.environ.get('REQUEST_METHOD') == 'POST':
            self.body = sys.stdin.read()
            try:
                self.message = json.loads(self.body)
            except Exception:
                if self.debug:
                    self.httpheader()
                    print self.httpheader, traceback.format_exc()
                    sys.exit(0)

                else:
                    print "json decode error"
                    sys.exit(0)

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
                if "gyazo.com" in t:
                    g = gyazo_scraper(t)
                    print g.getImageUrl()
                if t in self.dic:
                    print self.dic.get(t)

    def dump_text(self):
        self.httpheader()
        print len(self.texts)
        if self.texts is not None:
            for t in self.texts:
                print t
        else:
            print "none"


if __name__ == '__main__':
    no = notsubculture()
    no.read_http_post()
    no.slice_message()
    no.response()

    #g = gyazo_scraper("http://gyazo.com/8814b3cbed0a6e8b0a5cbb7203eaaed2")
    #print g.getImageUrl()
