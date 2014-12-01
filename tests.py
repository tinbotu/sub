#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 sts=4 ff=unix ft=python expandtab

import unittest
import json
from sun import NotSubculture, Subculture, SubcultureGyazoScraper, SubcultureMETAR, SubcultureOmochi, SubcultureStone, SubcultureHitozuma, AnotherIsMoreKnowerThanMe, SubcultureKnowerLevel, SubcultureGaishutsu, SubcultureSilent


class TestGyazoScraper(unittest.TestCase):
    gyazo_url = ['http://gyazo.com/8814b3cbed0a6e8b0a5cbb7203eaaed2', ]
    gyazo_url_false = ['http://i.gyazo.com/8814b3cbed0a6e8b0a5cbb7203eaaed2.png', 'http://example.com', u'http://gyazo.comｇｙａｚｏ', '::1', ]

    def setUp(self):
        self.g = SubcultureGyazoScraper()

    def test_instance(self):
        self.assertIsInstance(self.g, SubcultureGyazoScraper)

    def test_fetch(self):
        for url in self.gyazo_url:
            self.g.fetch(url)
            self.assertRegexpMatches(self.g.content, self.g.pick_re)

    def test_fetch_false(self):
        for url in self.gyazo_url_false:
            self.g.fetch(url)
            self.assertNotRegexpMatches(self.g.content, self.g.pick_re)

    def test_get_image_url(self):
        for url in self.gyazo_url:
            self.g.fetch(url)
            r = self.g.response()
            self.assertRegexpMatches(r, r'http://i.gyazo.com/[0-9a-z]+\.(png|jpg)')

        for url in self.gyazo_url_false:
            self.g.fetch(url)
            r = self.g.response()
            self.assertIsNone(r)


class TestSubcultureKnowerLevel(unittest.TestCase):

    def setUp(self):
        self.r = SubcultureKnowerLevel('', 'tests')

    def test_levelup(self):
        self.assertRegexpMatches(self.r.response(), u'おっ、分かり度 [0-9]+ ですか')


class TestSubcultureMETAR(unittest.TestCase):
    json_openweathermap = """{"coord":{"lon":139.69,"lat":35.69},"sys":{"type":3,"id":7622,"message":0.5056,"country":"JP","sunrise":1415394609,"sunset":1415432388},"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04n"}],"base":"cmc stations","main":{"temp":287.15,"pressure":1029,"humidity":82,"temp_min":287.15,"temp_max":287.15},"wind":{"speed":2.1,"deg":330},"clouds":{"all":90},"dt":1415447880,"id":1850147,"name":"Tokyo","cod":200}"""

    def setUp(self):
        self.r = SubcultureMETAR('', 'tests')

    def test_fetch(self):
        self.r.fetch(self.r.url)
        o = json.loads(self.r.content)
        self.assertIs(type(o), dict)
        self.assertGreater(float(o["main"]["temp"]), 243.15)
        self.assertLess(float(o["main"]["temp"]), 318.15)
        self.assertGreater(float(o["main"]["pressure"]), 800)
        self.assertGreater(float(o["main"]["humidity"]), 1)
        self.assertIs(type(o["weather"][0]["description"]), unicode)
        self.assertIs(type(o["weather"][0]["icon"]), unicode)

    def test_response(self):
        self.r.content = self.json_openweathermap
        res = self.r.response()
        self.assertEqual(res, u'overcast clouds (14.0\u2103; 1029\u3371; 82%)\nhttp://openweathermap.org/img/w/04n.png')


class TestSubcultureOmochi(unittest.TestCase):

    def setUp(self):
        self.r = SubcultureOmochi('', 'tests')

    def test_response_flood(self):
        self.r.clear_flood_status(self.r.speaker)
        self.r.enable_flood_check = True

        res = self.r.response()
        self.assertRegexpMatches(res, r'^https?://')
        res = self.r.response()
        self.assertIs(res, None)

    def test_response(self):
        self.r.clear_flood_status(self.r.speaker)
        self.r.enable_flood_check = False
        for i in xrange(100):
            res = self.r.response()
            self.assertRegexpMatches(res, r'^https?://')


class TestSubcultureStone(unittest.TestCase):

    def setUp(self):
        self.r = SubcultureStone('', 'tests')

    def test_response_flood(self):
        self.r.clear_flood_status(self.r.speaker)
        self.r.enable_flood_check = True
        res = self.r.response()
        self.assertRegexpMatches(res, u'(西山石|https?://)')
        res = self.r.response()
        self.assertIs(res, None)

    def test_response(self):
        self.r.clear_flood_status(self.r.speaker)
        self.r.enable_flood_check = False
        for i in xrange(500):
            res = self.r.response()
            self.assertRegexpMatches(res, u'(西山石|https?://)')


class TestSubcultureHitozuma(unittest.TestCase):

    def setUp(self):
        self.r = SubcultureHitozuma('', 'tests')

    def test_response(self):
        y = False
        n = False

        for i in xrange(100 * 100 * 3):
            res = self.r.response()
            if res == u'はい':
                y = True
            elif res == u'いいえ':
                n = True

        self.assertTrue(y)
        self.assertTrue(n)


class TestAnotherIsMoreKnowerThanMe(unittest.TestCase):

    def setUp(self):
        self.r = AnotherIsMoreKnowerThanMe('', 'tests')

    def test_response(self):
        for i in xrange(100):
            res = self.r.response()
            self.assertRegexpMatches(res, '^No, [A-Za-z0-9]+ culture.')


class TestSubcultureSilent(unittest.TestCase):
    dic = {
        u'会いたい': u'^(:?私も|また)?会いたいな$',
        u'コピペしたい': u'^(:?私も|また)?コピペしたいな$',
        u'観測をしたい': u'^(:?私も|また)?観測をしたいな$',
        u'何がしたいんだ': None,
        u'言わんとしたいことはわかる': None,
    }

    def setUp(self):
        self.r = SubcultureSilent('', 'tests')

    def test_response(self):
        self.r.force = True
        for c, r in self.dic.iteritems():
            self.r.text = c
            if r is None:
                self.assertIsNone(self.r.response())
            else:
                self.assertRegexpMatches(self.r.response(), r)




class TestSubcultureGaishutsu(unittest.TestCase):
    url = 'http://docs.python.jp/2/howto/regex.html'
    text = u'テスト http://docs.python.jp/2/howto/regex.html'

    def setUp(self):
        self.r = SubcultureGaishutsu(self.text, 'tests')
        self.r.redis_connect()

    def test_response_first(self):
        self.r.delete(self.url)

        self.r.text = self.text
        self.assertIs(self.r.response(), '')

        self.r.anti_double = True
        self.assertIs(self.r.response(), '')

    def test_response_say(self):
        self.r.anti_double = False
        res = self.r.response()
        self.assertRegexpMatches(res, u'おっ その (https?://[-_.!~*\'()a-zA-Z0-9;:&=+$,%]+/*[^\s　#]*) は [0-9\.]+ 日くらい前に tests により既出ですね')


class TestNotSubculture(unittest.TestCase):

    dic = {u'サブでは': '?', u'はい': u'はい', u'拝承': u'拝復', }

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

    def test_gyazo(self):
        self.n.read_http_post('POST', self.json_gyazo)
        for r in self.n.response():  # I dont care this comes first or not, one or more
            self.assertEqual(r, 'http://i.gyazo.com/8814b3cbed0a6e8b0a5cbb7203eaaed2.jpg')

    def test_dict_subculture(self):
        self.n.read_http_post('POST', self.json_subculture)
        for r in self.n.response():
            self.assertEqual(r, 'No')

if __name__ == '__main__':
    unittest.main()
