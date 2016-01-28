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
    SubculturePushbullet,
)


class TestSubculturePushbullet(unittest.TestCase):

    def setUp(self):
        self.g = SubculturePushbullet()
        self.g.settings_filename = 'pushbullet.yaml.skel'

    def test_settings(self):
        self.assertEqual(type(self.g.settings[0].get('keyword')), list)
        self.assertEqual(type(self.g.settings[0].get('key')), str)

    def test_get_mention_users(self):
        message_p = u'@testkeyword てすと'
        message_n = u'@CH8YEF4U なし'

        r = self.g.get_mention_users(text=message_p, speaker='test')
        self.assertEqual(r[0].get('user'), 'testkeyword')
        self.assertEqual(r[0].get('key'), 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        self.assertEqual(r[0].get('body'), '%s: %s' % ('test', message_p))

        r = self.g.get_mention_users(text=message_n, speaker='test')
        self.assertEqual(type(r), list)
        self.assertEqual(len(r), 0)



class TestTwitterScraper(unittest.TestCase):
    twitter_url = ['https://twitter.com/esehara/status/567342138640171009', 'https://twitter.com/saki61204/status/668731628450000896', ]
    twitter_url_false = ['https://twitter.com/esehara/status/567294583281709057']

    def setUp(self):
        self.g = SubcultureTwitterScraper()

    def test_fetch(self):
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
    gyazo_url = ['http://gyazo.com/8814b3cbed0a6e8b0a5cbb7203eaaed2', 'https://gyazo.com/6726d79c07efbb2ff6ab20cd90b789c9', 'https://gyazo.com/033c02612a1911a84554d89b29462628', ]
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
    json_wunderground = '{"response": {"version":"0.1","termsofService":"http://www.wunderground.com/weather/api/d/terms.html","features": {"conditions": 1}},"current_observation": {"image": {"url":"http://icons.wxug.com/graphics/wu2/logo_130x80.png","title":"Weather Underground","link":"http://www.wunderground.com"},"display_location": {"full":"Tokyo, Japan","city":"Tokyo","state":"","state_name":"Japan","country":"JP","country_iso3166":"JP","zip":"00000","magic":"1","wmo":"47671","latitude":"35.54999924","longitude":"139.77999878","elevation":"8.00000000"},"observation_location": {"full":"Tokyo, ","city":"Tokyo","state":"","country":"JP","country_iso3166":"JP","latitude":"35.55333328","longitude":"139.78111267","elevation":"26 ft"},"estimated": {},"station_id":"RJTT","observation_time":"Last Updated on 十月 13, 4:00 PM JST","observation_time_rfc822":"Tue, 13 Oct 2015 16:00:00 +0900","observation_epoch":"1444719600","local_time_rfc822":"Tue, 13 Oct 2015 16:09:19 +0900","local_epoch":"1444720159","local_tz_short":"JST","local_tz_long":"Asia/Tokyo","local_tz_offset":"+0900","weather":"所により曇","temperature_string":"72 F (22 C)","temp_f":72,"temp_c":22,"relative_humidity":"46%","wind_string":"From the SE at 6 MPH","wind_dir":"SE","wind_degrees":130,"wind_mph":6,"wind_gust_mph":0,"wind_kph":9,"wind_gust_kph":0,"pressure_mb":"1010","pressure_in":"29.83","pressure_trend":"0","dewpoint_string":"50 F (10 C)","dewpoint_f":50,"dewpoint_c":10,"heat_index_string":"NA","heat_index_f":"NA","heat_index_c":"NA","windchill_string":"NA","windchill_f":"NA","windchill_c":"NA","feelslike_string":"72 F (22 C)","feelslike_f":"72","feelslike_c":"22","visibility_mi":"6.2","visibility_km":"10.0","solarradiation":"--","UV":"1","precip_1hr_string":"-9999.00 in (-9999.00 mm)","precip_1hr_in":"-9999.00","precip_1hr_metric":"--","precip_today_string":"0.00 in (0.0 mm)","precip_today_in":"0.00","precip_today_metric":"0.0","icon":"partlycloudy","icon_url":"http://icons.wxug.com/i/c/k/partlycloudy.gif","forecast_url":"http://www.wunderground.com/global/stations/47671.html","history_url":"http://www.wunderground.com/history/airport/RJTT/2015/10/13/DailyHistory.html","ob_url":"http://www.wunderground.com/cgi-bin/findweather/getForecast?query=35.55333328,139.78111267","nowcast":""}}'

    def setUp(self):
        self.r = SubcultureMETAR('', 'tests')

    def test_fetch(self):
        if os.uname()[1] != 'stingray':
            return
        self.r.fetch_wunderground()
        self.r.parse_wunderground()
        self.assertGreater(self.r.temp_c, -50)
        self.assertLess(self.r.temp_c, 50)
        self.assertGreater(self.r.pressure, 800)
        self.assertIsNotNone(self.r.humidity)
        self.assertIs(type(self.r.weather), unicode)

    def test_response(self):
        self.r.content = self.json_wunderground
        res = self.r.response()
        self.assertEqual(res, u'所により曇 (22.0\u2103; 1010\u3371; 46%)\nhttp://icons.wxug.com/i/c/k/partlycloudy.gif')


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

    access_control_list = ['192.168.1.0/29', '172.16.0.0/22', ]

    def setUp(self):
        self.n = NotSubculture()
        self.n.enable_acl = False

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

    def test_acl(self):
        self.assertIs(False, self.n.acl(None, None))
        self.assertIs(False, self.n.acl(None, '192.168.1.60'))
        self.assertIs(False, self.n.acl(self.access_control_list, '192.168.1.60'))
        self.assertIs(True, self.n.acl(self.access_control_list, '192.168.1.2'))
        self.assertIs(True, self.n.acl(self.access_control_list, '172.16.3.254'))
        self.assertIs(False, self.n.acl(self.access_control_list, '172.16.4.1'))


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
        self.assertEqual(self.s.response(), u'Title: 「マッドマックス」上映中の米映画館で発砲、51歳の容疑者射殺 | Reuters')

    def test_instagram(self):
        self.s.text = 'https://www.instagram.com/p/BA_yNXQjvAd/'
        self.assertEqual(self.s.response(), 'https://scontent.cdninstagram.com/t51.2885-15/e35/12568894_505444742950257_187380268_n.jpg')



if __name__ == '__main__':
    unittest.main()
