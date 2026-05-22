# -*- coding: utf-8 -*-

import hashlib
import json
import os
import random
import traceback
import emoji
import requests
import redis
import yaml
from html.parser import HTMLParser

class Subculture(object):
    """ abstract """
    content = None
    speaker = None
    text = None
    enable_flood_check = True
    doge_is_away = False
    api_secret = None
    _settings = None
    settings_filename = "settings.yaml"

    def __init__(self, text=None, speaker=None):
        self.speaker = speaker
        self.text = text

    def check_flood(self, speaker='', sec=30):
        return True

    def clear_flood_status(self, speaker='', sec=30):
        pass

    def check_doge_away(self):
        return self.doge_is_away

    def doge_away(self, goaway=True, expire_sec=60*15):
        pass

    def fetch(self, url, params=None, guess_encoding=False, payload=None):
        self.content = None
        headers = {
            "User-Agent": r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
        }
        try:
            import cchardet
            if payload:
                r = requests.post(url, headers=headers, params=params, data=payload)
            else:
                r = requests.get(url, headers=headers, params=params)
            if r.status_code == requests.codes.ok:
                self.content = r.content
                self.content_headers = r.headers
                if guess_encoding:
                    self.content_encoding = cchardet.detect(r.content).get("encoding")
                else:
                    self.content_encoding = r.encoding
            else:
                self.content = '?:' + str(r.status_code)
        except Exception:
            self.content = traceback.format_exc()

    def response(self):
        """ abstract """
        return None

    def read_bot_api(self, filename='bot_secret.yaml'):
        if self.api_secret is not None:
            return
        yaml_file = open(filename)
        content = yaml_file.read()
        yaml_file.close()
        self.api_secret = yaml.safe_load(content)

    @property
    def settings(self):
        if self._settings is not None:
            return self._settings
        fp = open(self.settings_filename).read()
        self._settings = yaml.safe_load(fp)
        return self._settings

    def build_say_payload(self, room, bot, text, apikey):
        """ Lingr """
        demoji = emoji.demojize(text)

        return {
            'room': room,
            'bot': bot,
            'text': demoji,
            'bot_verifier': hashlib.sha1(str(bot + apikey).encode()).hexdigest(),
        }

    def say_lingr(self, message, speaker='doge', anti_double_sec=15, anti_double=True):
        if self.api_secret is None:
            self.read_bot_api()

        if self.api_secret.get("bot_secret") is None or \
           self.api_secret.get("bot_id") is None or \
           self.api_secret.get("room") is None:
            return

        if anti_double and self.check_flood("bot_say_"+speaker, anti_double_sec) is False:
            print("301 Flood")
            return

        payload = self.build_say_payload(self.api_secret.get("room"), self.api_secret.get("bot_id"), message, self.api_secret.get("bot_secret"))

        self.fetch('http://lingr.com/api/room/say', payload)


    def say_slack(self, message, speaker='doge', anti_double_sec=15, anti_double=True):
        if self.api_secret is None:
            self.read_bot_api()

        if self.api_secret.get("slack_webhook_url") is None:
            return

        if anti_double and self.check_flood("bot_say_slack_"+speaker, anti_double_sec) is False:
            print("301 Flood")
            return

        payload = {}
        payload["text"] = message
        payload["channel"] = "#general"
        payload["username"] = "main"
        self.fetch(self.api_secret.get("slack_webhook_url"), payload=json.dumps(payload))


    def doge_soku(self):
        return 1.0

    def spontaneous(self, name, key):
        for app in self.settings["spontaneous"]:
            if app["name"] == name and app["key"] == key:
                return app

    @property
    def temporary(self):
        return None

    @temporary.setter
    def temporary(self, obj):
        pass


class RedisSubculture(Subculture):
    __redis_db = 14  # don't change me if changes will cause collision other app
    _conn = None

    @property
    def conn(self):
        if self._conn is None:
            self._conn = redis.Redis(host='127.0.0.1', db=self.__redis_db, decode_responses=True)
            try:
                self._conn.ping()
            except redis.exceptions.ResponseError as e:
                if e.message == 'NOAUTH Authentication required.':
                    self._conn.execute_command("AUTH", self.settings["redis_auth"])
                else:
                    raise
        return self._conn

    def check_flood(self, speaker='', sec=30):
        if self.enable_flood_check is False:
            return True

        key = 'flood_%s__%s' % (self.__class__.__name__, speaker)
        if self.conn.get(key) is not None:
            return False

        self.conn.set(key, '1')
        self.conn.expire(key, sec)

        return True

    def clear_flood_status(self, speaker='', sec=30):
        key = 'flood_%s__%s' % (self.__class__.__name__, speaker)
        self.conn.delete(key)

    def check_doge_away(self):
        if self.conn.get('doge_away') == "1":
            self.doge_is_away = True
        else:
            self.doge_is_away = False
        return self.doge_is_away

    def doge_away(self, goaway=True, expire_sec=60*15):
        if goaway:
            self.conn.set('doge_away', "1")
            self.conn.expire('doge_away', expire_sec)
        else:
            self.conn.delete('doge_away')

    def doge_soku(self):
        value = self.conn.get("inu_soku")
        if value is None:
            value = 0
        else:
            value = float(value)
        return float(max(value, 1))

    @property
    def temporary(self):
        return None

    @temporary.setter
    def temporary(self, obj):
        key = "temporary_"
        self.conn.rpush(key, json.dumps(obj))
        self.conn.expire(key, 60*60*24)


class HTMLParserGetElementsByTag(HTMLParser):
    reading = False
    _count = 0

    def __init__(self, target_tag, target_meta_property=None, count=None):
        HTMLParser.__init__(self)
        self.target_tag = target_tag
        self.target_meta_property = target_meta_property
        self.countlimit = count
        self._content = ''

    def handle_starttag(self, tag, attrs):
        if type(self.countlimit) is int and self._count >= self.countlimit:
            return

        attrs = dict(attrs)

        if tag == self.target_tag:
            self._count += 1
            # <meta property="og:title" content="T I T L E" /> とかはここで取っちゃう
            if self.target_meta_property is not None:
                if self.target_meta_property == attrs.get("property"):
                    self._content += attrs.get("content") + "\n"
            else:
                self.reading = True


    def handle_data(self, data):
        self.concat_content(data)

    def handle_charref(self, data):
        self.concat_content(self.unescape('&#'+data+';'))

    def handle_entityref(self, data):
        self.concat_content(self.unescape('&'+data+';'))

    def handle_endtag(self, tag):
        if tag == self.target_tag:
            self.reading = False

    def concat_content(self, data):
        if self.reading:
            self._content += data


    @property
    def content(self):
        return self._content


class DogeAwayMessage(Exception):
    def __init__(self, msg):
        self.msg = msg
