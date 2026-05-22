# -*- coding: utf-8 -*-

import json
import pickle
import random
import re
import time
from .base import Subculture, RedisSubculture

class METARSubculture(RedisSubculture):
    """ Weather METARs """
    url = 'http://api.openweathermap.org/data/2.5/weather?id=1850147&APPID=%s'

    def fetch_openweathermap(self):
        apikey = self.settings.get('openweathermap_apikey')
        self.url = self.url % apikey
        self.fetch(self.url)

    def parse_openweathermap(self):
        w = json.loads(self.content)
        self.weather = w["weather"][0]["description"]
        self.temp_c = float(w["main"]["temp"]) - 273.15  # kelvin
        self.icon_url =  ("https://openweathermap.org/img/w/%s.png" % w["weather"][0]["icon"])
        self.pressure = int(w["main"]["pressure"])
        self.humidity = w["main"]["humidity"]

    def response(self):
        if self.content is None:
            self.fetch_openweathermap()
        self.parse_openweathermap()

        if self.weather is not None:
            return '%s (%.1f\u2103; %d\u3371; %s%%)\n%s' % (self.weather, self.temp_c, self.pressure, self.humidity, self.icon_url)


class KotoshinoKanjiSubculture(Subculture):

    def response(self):
        return """2010 罰
2011 罰
2012 罰
2013 諦
2014 渋
2015 老
2016 家
2017 終
2018 転
2019 無
2020 終
2021 蟄
2022 葬
2023 隠"""


class MineoSubculture(RedisSubculture):

    def response(self):
        self.fetch("https://0x00.be/cgi-bin/dogewunderground/mineo_latency.cgi?multispan=true")
        return None


class GaishutsuSubculture(RedisSubculture):
    """ url gaishutsu checker """
    """ title extractor """
    anti_double = True
    url_blacklist = ['gyazo.com', '.png', '.jpg', ]

    def build_message(self, url, body):
        r = pickle.loads(body)
        ago = ''
        if r.get('speaker') == self.speaker and self.speaker != 'tests':
            return ""

        if r.get("first_seen"):
            ago_sec = time.time() - float(r.get("first_seen"))
            if self.anti_double and ago_sec < 30:
                return ""  # dont respond within 30 sec
            ago = ' %.1f 日くらい前に' % (ago_sec / (60*60*24))
        return 'おっ その %s は%s %s により既出ですね' % (url, ago, r.get('speaker'))

    def update(self, key, count=1):
        r = {}
        r['speaker'] = self.speaker
        r['first_seen'] = time.time()
        r['last_seen'] = time.time()
        r['count'] = count
        self.conn.set(key, pickle.dumps(r))

    def delete(self, url):
        self.conn.delete(self.get_key(url))

    def get_key(self, url):
        # plase dont pollute url
        return "%s__URI__%s" % (self.__class__.__name__, url)

    def response(self):
        url_re = re.compile(r'<?(https?:\/\/[-_.!~*\'()a-zA-Z0-9;:&=+$,%]+\/*[^\s>　]*)>?')

        res = ''
        urls = url_re.findall(self.text)
        for url in urls:
            skip = False
            for black in self.url_blacklist:
                if black in url or len(url) > 1024:
                    skip = True
            if skip:
                continue

            key = self.get_key(url)
            value = self.conn.get(key)
            if value is not None:
                res += self.build_message(url, value)
            else:
                self.update(key)

        return res

class HateSubculture(Subculture):

    def response(self):
        random.seed()
        return '川\n' * (random.randint(0, 10) + 20)
