#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 sts=4 ff=unix ft=python expandtab

import unittest
from sun import GyazoScraper, NotSubculture


class TestGyazoScraper(unittest.TestCase):
    gyazo_url = ['http://gyazo.com/8814b3cbed0a6e8b0a5cbb7203eaaed2', ]
    gyazo_url_false = ['http://i.gyazo.com/8814b3cbed0a6e8b0a5cbb7203eaaed2.png', 'http://example.com', u'http://gyazo.comｇｙａｚｏ', '::1', ]

    def setUp(self):
        self.g = GyazoScraper()

    def test_instance(self):
        self.assertIsInstance(self.g, GyazoScraper)

    def test_fetch(self):
        for url in self.gyazo_url:
            self.g.fetch(url)
            self.assertRegexpMatches(self.g.content, self.g.gyazo_image_re)

    def test_fetch_false(self):
        for url in self.gyazo_url_false:
            self.g.fetch(url)
            self.assertNotRegexpMatches(self.g.content, self.g.gyazo_image_re)

    def test_get_image_url(self):
        for url in self.gyazo_url:
            self.g.fetch(url)
            r = self.g.get_image_url()
            self.assertRegexpMatches(r, r'http://i.gyazo.com/[0-9a-z]+\.(png|jpg)')

        for url in self.gyazo_url_false:
            self.g.fetch(url)
            r = self.g.get_image_url()
            self.assertIsNone(r)


class TestNotSubculture(unittest.TestCase):

    dic = {u'サブでは': '?', u'はい': u'はい', }

    json_official_sample = """{"status":"ok",
 "counter":208,
 "events":[
  {"event_id":208,
   "message":
    {"id":82,
     "room":"myroom",
     "public_session_id":"UBDH84",
     "icon_url":"http://example.com/myicon.png",
     "type":"user",
     "speaker_id":"kenn",
     "nickname":"Kenn Ejima",
     "text":"yay!",
     "timestamp":"2011-02-12T08:13:51Z",
     "local_id":"pending-UBDH84-1"}}]}"""

    json_gyazo = """{"status":"ok",
 "counter":208,
 "events":[
  {"event_id":208,
   "message":
    {"id":82,
     "room":"myroom",
     "public_session_id":"UBDH84",
     "icon_url":"http://example.com/myicon.png",
     "type":"user",
     "speaker_id":"kenn",
     "nickname":"Kenn Ejima",
     "text":"http://gyazo.com/8814b3cbed0a6e8b0a5cbb7203eaaed2",
     "timestamp":"2011-02-12T08:13:51Z",
     "local_id":"pending-UBDH84-1"}}]}"""

    json_subculture = """{"status":"ok",
 "counter":208,
 "events":[
  {"event_id":208,
   "message":
    {"id":82,
     "room":"myroom",
     "public_session_id":"UBDH84",
     "icon_url":"http://example.com/myicon.png",
     "type":"user",
     "speaker_id":"kenn",
     "nickname":"Kenn Ejima",
     "text":"subculture",
     "timestamp":"2011-02-12T08:13:51Z",
     "local_id":"pending-UBDH84-1"}}]}"""

    def setUp(self):
        self.n = NotSubculture()

    def test_instance(self):
        self.assertIsInstance(self.n, NotSubculture)

    def test_dictionary(self):
        pass

    def test_read_http_post(self):
        self.n.read_http_post('POST', self.json_official_sample)
        self.assertEqual(self.json_official_sample, self.n.body)

    def test_slice_message(self):
        self.n.read_http_post('POST', self.json_official_sample)
        self.n.slice_message()
        self.assertIs(type(self.n.texts), list)
        self.assertEqual(self.n.texts[0], u'yay!')

    def test_gyazo(self):
        self.n.read_http_post('POST', self.json_gyazo)
        self.n.slice_message()
        for r in self.n.response():  # I dont care this comes first or not, one or more
            self.assertEqual(r, 'http://i.gyazo.com/8814b3cbed0a6e8b0a5cbb7203eaaed2.jpg')

    def test_dict_subculture(self):
        self.n.read_http_post('POST', self.json_subculture)
        self.n.slice_message()
        for r in self.n.response():
            self.assertEqual(r, 'No')

if __name__ == '__main__':
    unittest.main()
