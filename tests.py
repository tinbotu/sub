#!./bin/python
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 sts=4 ff=unix ft=python expandtab

import json
import unittest
import os

from sun import (
    NotSubculture,
    Subculture,
    SubcultureGyazoScraper,
    SubcultureTwitterScraper,
    SubcultureMETAR,
    SubcultureOmochi,
    SubcultureStone,
    SubcultureHitozuma,
    AnotherIsMoreKnowerThanMe,
    SubcultureKnowerLevel,
    SubcultureGaishutsu,
    SubcultureSilent,
    SubcultureNogata,
    SubcultureDogeDetailStatus,
    SubcultureShowDogeSoku,
    SubcultureSelfUpdate,
    SubcultureTitleExtract,
)


class TestTwitterScraper(unittest.TestCase):
    twitter_url = [
        'https://twitter.com/esehara/status/567342138640171009',
        'https://twitter.com/miminashi/status/566437373056016384']
    twitter_url_false = ['https://twitter.com/esehara/status/567294583281709057']

    def setUp(self):
        self.g = SubcultureTwitterScraper()

    def test_fatch(self):
        for url in self.twitter_url:
            self.g.fetch(url)
            self.assertRegexpMatches(self.g.content, self.g.pick_re)

    def test_inner_url(self):
        texts = [
            "@niryuu https://twitter.com/ah_hpc/status/567754030638964736",
            "https://twitter.com/ah_hpc/status/567754030638964736",
            "https://twitter.com/ah_hpc/status/567754030638964736 @niryuu"]
        for text in texts:
            self.assertRegexpMatches(self.g.get_twitter_url(text), self.g.url_re)


class TestGyazoScraper(unittest.TestCase):
    gyazo_url = ['http://gyazo.com/8814b3cbed0a6e8b0a5cbb7203eaaed2', 'https://gyazo.com/6726d79c07efbb2ff6ab20cd90b789c9', ]
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
            self.assertRegexpMatches(r, r'https?://i.gyazo.com/[0-9a-z]+\.(png|jpg)')

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

        for i in xrange(100 * 100 * 10):
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


class TestSubcultureDogeDetailStatus(unittest.TestCase):
    def setUp(self):
        self.r = SubcultureDogeDetailStatus('', 'tests')

    def test_return_status_expired(self):
        self.r.conn.delete('inu_soku')
        self.r.conn.delete('inu_internal_atencion')
        self.r.conn.delete('inu_internal_soku')
        self.assertEqual(self.r.response(), u'クゥーン(soku: 0.00, internal_atencion: 0.00, internal_soku: 0.00)')

    def test_return_status(self):
        self.r.conn.set('inu_soku', 5.219039183)
        self.r.conn.set('inu_internal_atencion', 1.2345678)
        self.r.conn.set('inu_internal_soku', 9.87654)
        self.assertEqual(self.r.response(), u'クゥーン(soku: 5.22, internal_atencion: 1.23, internal_soku: 9.88)')


class TestSubcultureShowDogeSoku(unittest.TestCase):
    def setUp(self):
        self.r = SubcultureShowDogeSoku('', 'tests')

    def test_response(self):
        self.assertRegexpMatches(self.r.response(), '^https?://')


class TestSubcultureNogata(unittest.TestCase):
    text = u'姫'
    def setUp(self):
        self.nogata = SubcultureNogata(self.text)
        self.nogata.PROBABLY = 200

    def test_response(self):
        word = self.nogata.response()
        self.assertEqual(word, u'姫')

    def test_nogata(self):
        self.nogata.text = u'おっ'
        word = self.nogata.response()
        self.assertIs(word, None)


class TestSubcultureGaishutsu(unittest.TestCase):
    url = 'http://docs.python.jp/2/howto/regex.html'
    text = u'テスト http://docs.python.jp/2/howto/regex.html'

    def setUp(self):
        self.r = SubcultureGaishutsu(self.text, 'tests')

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


class TestSubcultureSelfUpdate(unittest.TestCase):
    def test_create_instance(self):
        instance = SubcultureSelfUpdate('', u'(犬転生)')
        self.assertIsInstance(instance, SubcultureSelfUpdate)

    def test_import_git(self):
        import git
        self.assertIsInstance(git.Repo('.'), git.Repo)


class TestPermission(unittest.TestCase):
    def test_permission(self):
        s = os.stat("sun.cgi")
        self.assertEqual(s.st_mode, 33261)  # -rwxr-xr-x


class TestSubcultureSpontaneity(unittest.TestCase):
    def setUp(self):
        self.s = Subculture()

    def test_build_payload(self):
        room = "tinbotu"
        bot = "dummy___"
        text = "text"
        key = "8fzyJKABFxtfmXuaeakfQbDasJN"

        r = self.s.build_say_payload(room, bot, text, key)
        self.assertEqual(r["room"], room)
        self.assertEqual(r["bot"], bot)
        self.assertEqual(r["text"], text)
        self.assertEqual(r["bot_verifier"], '621d424bdaeb065e18800ccf720e2860ba204bcd')


    def test_read_bot_api_secret(self):
        self.s.read_bot_api("bot_secret.yaml.skel")
        self.assertIsNotNone(self.s.api_secret.get("bot_secret"))
        self.assertIsNotNone(self.s.api_secret.get("bot_id"))
        self.assertIsNotNone(self.s.api_secret.get("room"))

    def test_say(self):
        pass


class TestSubcultureTitleExtract(unittest.TestCase):
    def setUp(self):
        self.s = SubcultureTitleExtract()

    def test_cp932(self):
        self.s.text = 'http://kakaku.com'
        self.assertEqual(self.s.response(), u'Title: 価格.com - 「買ってよかった」をすべてのひとに。')

    def test_euc(self):
        self.s.text = 'http://www.mozilla.gr.jp/standards/webtips0022.html'
        self.assertEqual(self.s.response(), u'Title: 文字コード宣言は行いましょう(HTML) - Web標準普及プロジェクト')

    def test_utf8(self):
        self.s.text = 'http://www.google.com'
        self.assertEqual(self.s.response(), u'Title: Google')

    def test_utf8_withlazycrlf(self):
        self.s.text = 'http://jp.reuters.com/article/2015/08/05/us-theater-shooting-idJPKCN0QA2O720150805'
        self.assertEqual(self.s.response(), u'Title: 「マッドマックス」上映の劇場で発砲、容疑者射殺後に空気銃と判明 | Reuters')



if __name__ == '__main__':
    unittest.main()
