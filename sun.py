#!./bin/python
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 sts=4 ff=unix ft=python expandtab

# 絡み方が悪質

import codecs
import copy
import hashlib
import inspect
import json
import math
import os
import pickle
import random
import re
import sys
import time
import datetime
import traceback

import cchardet
import emoji
import git
import ipaddress
import requests
import redis
import MeCab
import yaml

import html
from html.parser import HTMLParser
from urllib.parse import parse_qsl

import urllib3
import urllib3.exceptions
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Subculture(object):
    """ abstract """
    content = None
    speaker = None
    text = None
    __redis_db = 14  # don't change me if changes will cause collision other app
    _conn = None
    enable_flood_check = True
    doge_is_away = False
    api_secret = None
    _settings = None
    settings_filename = "settings.yaml"

    def __init__(self, text=None, speaker=None):
        self.speaker = speaker
        self.text = text

    @property
    def conn(self):
        if self._conn is None:
            self._conn = redis.Redis(host='127.0.0.1', db=self.__redis_db)
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

    def fetch(self, url, params=None, guess_encoding=False, payload=None):
        self.content = None
        headers = {
            "User-Agent": r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
        }
        try:
            if payload:
                r = requests.post(url, headers=headers, params=params, data=payload, verify=False)
            else:
                r = requests.get(url, headers=headers, params=params, verify=False)
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
        value = self.conn.get("inu_soku")
        if value is None:
            value = 0
        return float(max(value, 1))

    def spontaneous(self, name, key):
        for app in self.settings["spontaneous"]:
            if app["name"] == name and app["key"] == key:
                return app

    @property
    def temporary(self):
        return None

    @temporary.setter
    def temporary(self, obj):
        key = "temporary_"
        self.conn.rpush(key, json.dumps(obj))
        self.conn.expire(key, 60*60*24)



class SubcultureKnowerLevel(Subculture):

    def response(self):
        level = self.conn.incr("knower-%s" % self.speaker, 1)
        return u"おっ、分かり度 %d ですか" % level


class SubcultureKnowerLevelUp(Subculture):
    pass


class SubcultureRetirementLevelUp(Subculture):
    def response(self):
        self.conn.incr("retirement-%s" % self.speaker, 1)
        return None


class SubcultureNogata(Subculture):
    u""" 姫 """

    PROBABLY = 1

    def response(self):
        if random.randint(0, 200) > self.PROBABLY:
            return None
        mecab = MeCab.Tagger().parse(self.text)
        node = mecab.split("\n")
        noword = []
        for l in node:
            if l == 'EOS' or l == '':
                break
            word, wordclass = l.split("\t")
            wordclass = wordclass.split(",")
            if wordclass[0] == "名詞":
                noword.append(word)
        random.shuffle(noword)
        if len(noword) > 0:
            return noword.pop()
        return None


class SubcultureAtencion(Subculture):
    """ me? """
    atencion = 0
    soku = 0

    atencion_T = .1
    soku_T = .2

    atencion_dic = {
        u'犬': 150,
        u'イヌ': 100,
        u'^お前': 30,
        'main': 10,
        'bot': 10,
        u'メイン': 10,
        u'サブ': 4,
        'doge': 50,
    }
    soku_dic = {
        u'犬': 10,
        u'うぜー': -100,
        u'糞': -80,
        u'クソ': -100,
        u'黙れ': -150,
        u'はい$': 10,
        u'はいじゃないが': -20,
        u'おっ': 20,
        u'オッ': 20,
        u'いいですね': 10,
        u'寿司': 5,
        u'[分|わ]か[らりるっん]': 20,
        u'かわいい': 10,
        u' T ': 50,
        u'だる': -10,
        u'姫': 20,
        u'サ[ブヴ]': 30,
        u'ゴミ': 10,
        u'(馬鹿|バカ)': 40,
        u'機運': 20,
        u'ウッ': 10,
        u'危険': 10,
        u'なるほど': 10,
        u'おもち': -10,
        u'(ない|ねーよ?)$': -30,
        u'絡み方が悪質': 50,
        'doge': 20,
        'Ruby': 10,
    }

    def lpf(self, n0, n1, T=.3):
        return (n0 + (n1 - n0) * (.1 / (1 / (2*3.142*T))))

    def response(self):
        self.atencion = self.conn.get("inu_internal_atencion")
        self.soku = self.conn.get("inu_internal_soku")
        inu_soku = self.conn.get("inu_soku")
        if self.atencion is None:
            self.atencion = 0
        else:
            self.atencion = float(self.atencion)

        if self.text == u'犬寝ろ':
            pass
        else:
            if self.soku is None:
                self.soku = 0
            else:
                self.soku = float(self.soku)

            for dict_k, score in self.atencion_dic.iteritems():
                if re.compile(dict_k).search(self.text):
                    n1 = self.atencion + float(score)
                    self.atencion = self.lpf(self.atencion, n1, self.atencion_T)
            else:
                self.atencion = float(self.atencion) - 1

            me_factor = 1 + math.sqrt(abs(self.atencion))
            for dict_k, score in self.soku_dic.iteritems():
                if re.compile(dict_k).search(self.text):
                    n1 = self.soku + float(score) * me_factor
                    self.soku = self.lpf(self.soku, n1, self.soku_T)
            else:
                self.soku = float(self.soku) - 1

        if self.soku < 0:
            self.soku = 0
        if self.atencion < 0:
            self.atencion = 0

        inu_soku = 1 + math.sqrt(self.soku)
        self.conn.set("inu_soku", inu_soku)
        self.conn.set("inu_internal_atencion", self.atencion)
        self.conn.set("inu_internal_soku", self.soku)
        self.conn.expire("inu_soku", 60*20)
        self.conn.expire("inu_internal_atencion", 60*20)
        self.conn.expire("inu_internal_soku", 60*20)

        random.seed()
        if random.randrange(1, 500) < inu_soku:
            # msg = u"new soku:%.2f, internal_soku:%.2f, internal_atencion:%.2f" % (inu_soku, self.soku, self.atencion)
            return u'オッ'


class SubcultureDogeDetailStatus(Subculture):
    """ Show doge status """
    def response(self):
        # Expireしている場合はNoneが得られるため、maxで数値にしている
        soku = self.conn.get('inu_soku')
        if soku is None:
            soku = 0
        else:
            soku = float(soku)
        in_at = self.conn.get('inu_internal_atencion')
        if in_at is None:
            in_at = 0
        else:
            in_at = float(in_at)
        in_soku = self.conn.get('inu_internal_soku')
        if in_soku is None:
            in_soku = 0
        else:
            in_soku = float(in_soku)
        inu_soku = float(max(soku, 0))
        inu_internal_atencion = float(max(in_at, 0))
        inu_internal_soku = float(max(in_soku, 0))

        return u'クゥーン(soku: %.2f, internal_atencion: %.2f, internal_soku: %.2f)' % (
            inu_soku, inu_internal_atencion, inu_internal_soku)


class SubcultureSelfUpdate(Subculture):
    def response(self):
        repo = git.Repo('.')
        if repo.is_dirty():
            return u'私は穢れている'

        previous_head = repo.head.commit.hexsha
        repo.remotes.origin.pull('master')

        if repo.head.commit.hexsha == previous_head:
            return '?'
        else:
            os.system("make update_packages 1>deploy.log 2>&1")
            url = u'https://github.com/tinbotu/sub/commit/%s' % (repo.head.commit.hexsha,)
            msg = u'ニャーン %s %s %s\n%s' % (repo.head.commit.hexsha,
                                                  repo.head.commit.committer,
                                                  repo.head.commit.message,
                                                  url)
            return msg


class SubcultureShowDogeSoku(Subculture):
    def response(self):
        doge2048 = [
            "doge-wink-114.gif",
            "doge-shake-space-114.gif",
            "doge-peepers-114.gif",
            "doge-prizza-114.gif",
            "doge-hat-114.gif",
            "doge-gradient-114.gif",
            "doge-fat-114.gif",
            "doge-rainbow-114.gif",
            "doge-sunglasses-114.gif",
            "doge-derp-114.gif",
        ]
        ret = None
        try:
            doge_soku = float(self.conn.get("inu_soku"))
            doge_index = int(doge_soku/2.)
            if doge_index >= 0 and doge_index < len(doge2048):
                ret = "http://doge2048.com/img/114/%s" % (doge2048[doge_index])
            else:
                ret = "http://weknowmemes.com/wp-content/uploads/2013/11/doge-sun-meme.jpg\n%d" % (doge_soku)
        except Exception:
            ret = "http://weknowmemes.com/wp-content/uploads/2013/11/doge-sun-meme.jpg"
        return ret


class SubcultureSilent(Subculture):
    """ me too """
    force = False
    PROBABLY = 5

    backward_dic = [
        {
            'wordclass': '動詞',
            'conj1': 'サ変・スル',
        },
        {
            # 'wordclass': '動詞',
            'wordclass1': '接尾',
        },
        {
            'wordclass': '助詞',
            'wordclass1': '格助詞',
        },
        {
            'wordclass': '助詞',
            'wordclass1': '係助詞',
        },
        {
            # 'wordclass': '名詞',
            'wordclass1': '非自立',
        },
        {
            'wordclass': '助動詞',
        },
        {
            'wordclass': '助詞',
            'wordclass1': '接続助詞',
        },
        {
            'wordclass': '助詞',
            'wordclass1': '並立助詞',
        },
        {
            'wordclass': '動詞',
            'conj2': '連用形',
        },
        {
            'wordclass': '助詞',
            # 'wordclass1': '副助詞',
        },
        {
            'wordclass': '名詞',
            # 'wordclass1': '副助詞',
        },
    ]

    break_dic = [
        {
            'word': 'ん',
        },
        {
            'word': 'の',
            'wordclass': '名詞',
            'wordclass1': '非自立',
            'wordclass2': '一般',
        },
        {
            # 'word': 'こと',
            'wordclass': '名詞',
            'wordclass1': '非自立',
        },
        {
            'wordclass': '助詞',
            'wordclass1': '副助詞／並立助詞／終助詞',
        },
        {
            'word': 'も',
            'wordclass': '助詞',
        },
    ]

    def divide_wordclass(self, text):
        word = {}
        if text is None or text == '' or text == "EOS":
            return {"word": text}
        wordclass = ["wordclass", "wordclass1", "wordclass2", "wordclass3", "conj1", "conj2", "conj3", "yomi", "pron"]
        word["word"] = text.split("\t")[0]
        feature = text.split("\t")[1].split(",")

        if len(feature) == len(wordclass):
            for n in feature:
                word[wordclass.pop(0)] = n
        return word

    def check_forward(self, word, i):
        if len(word) <= i:
            return False
        for d in self.break_dic:
            if (d.get("word") is None or word[i+1].get("word") == d["word"]) and \
               (d.get("wordclass") is None or word[i+1].get("wordclass") == d["wordclass"]) and \
               (d.get("wordclass1") is None or word[i+1].get("wordclass1") == d["wordclass1"]) and \
               (d.get("conj1") is None or word[i+1].get("conj1") == d["conj1"]):
                return True

    def check_backward(self, word, i):
        backward = False
        for d in self.backward_dic:
            if (d.get("word") is None or word[i-1].get("word") == d["word"]) and \
               (d.get("wordclass") is None or word[i-1].get("wordclass") == d["wordclass"]) and \
               (d.get("wordclass1") is None or word[i-1].get("wordclass1") == d["wordclass1"]) and \
               (d.get("conj1") is None or word[i-1].get("conj1") == d["conj1"]):
                backward = True
        if backward:
            do = self.check_backward(word, i-1) + word[i-1].get("word")
        else:
            do = word[i-1].get("word")
        return do

    @property
    def probably(self):
        if self.speaker in ["niryuu", "tinbotu"]:
            self.PROBABLY = 100
        random.seed()
        return (self.force is not True
                and random.randrange(0, 100) > self.PROBABLY)

    @property
    def is_not_response(self):
        return self.probably

    def response(self):

        if self.is_not_response:
            return None

        m = MeCab.Tagger()
        node = m.parse(self.text)
        node = node.split("\n")
        word = []
        for l in node:
            word.append(self.divide_wordclass(l))

        for i in range(len(word)):
            do = None
            if word[i].get("word") == 'たい' and word[i].get("wordclass") == '助動詞' and word[i].get("conj1") == '特殊・タイ':
                do = self.check_backward(word, i)
                if self.check_forward(word, i):
                    continue
            if do:
                me = [u'私も', u'私も', u'私も', u'また', u'私も', ]
                return u'%s%sたいな' % (me[random.randrange(0, len(me))], do.decode('utf_8'))


class SubcultureKnowerLevelGet(Subculture):

    def response(self):
        speakers_blacklist = ["knower-tests", "knower-None", ]
        res = ''
        speakers = self.conn.keys("knower-*")

        for s in speakers:
            if s not in speakers_blacklist:
                res += "%s: %s\n" % (s, self.conn.get(s))

        return res


class SubcultureRetirementLevelGet(Subculture):

    def response(self):
        speakers_blacklist = ["knower-tests", "knower-None", ]
        res = ''
        speakers = self.conn.keys("retirement-*")

        for s in speakers:
            if s not in speakers_blacklist:
                res += "%s: %s\n" % (s, self.conn.get(s))

        return res


class SubcultureTwitterScraper(Subculture):
    pick_re = 'og\:image" content="(https://pbs.twimg.com/media/(?:.+(?:\.png|\.jpg)))'
    url_re = "(https?://twitter.com/(?:[0-9A-Za-z_/.]+))[^>\s]?"

    def __init__(self, text=None, speaker=None):
        self.pick_re = re.compile(self.pick_re)
        if text is not None:
            self.fetch(self.get_twitter_url(text))

    def get_twitter_url(self, text):
        self.url_re = re.compile(self.url_re)
        m = self.url_re.search(text)
        if m and m.group():
            return m.group(1)

    def response(self):
        match = self.pick_re.findall(self.content)
        if type(match) is list:
            return "\n".join(match)
        else:
            return None


class SubcultureGyazoScraper(Subculture):
    """ gyazo image url extactor """
    pick_re = r'(?:<link href| src)="(https?://i.gyazo.com/([0-9a-z\.]+))" '

    def __init__(self, text=None, speaker=None):
        self.pick_re = re.compile(self.pick_re)
        if text is not None:
            self.fetch(text.strip())

    def response(self):
        m = self.pick_re.search(str(self.content))
        if m and m.group():
            return m.group(1)
        else:
            return None


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


class SubcultureTitleExtract(Subculture):
    """ <title> extract very quickhack """
    url_blacklist = ['twitter.com', 'gyazo.com', '.png', '.jpg', 'slack.com', ]

    def get_element_title(self, url=None):
        h = None
        prefix = ''
        postfix = ''
        re_google_photo_remove_odd_params = re.compile(r'(http.+?)=[whpk][0-9\-]')

        og_image = ['instagram.com', 'flickr.com/photos/', 'flic.kr', ]
        og_image_postfix_jpg = ['photos.google.com', 'goo.gl/photos', 'photos.app.goo.gl', ]
        og_description = ['twitter.com', 'facebook.com', ]
        if url is not None and True in [u in url for u in og_image]:
            h = HTMLParserGetElementsByTag('meta', target_meta_property='og:image')
        elif url is not None and True in [u in url for u in og_image_postfix_jpg]:
            h = HTMLParserGetElementsByTag('meta', target_meta_property='og:image')
            postfix = '#.jpg'
        elif url is not None and True in [u in url for u in og_description]:
            h = HTMLParserGetElementsByTag('meta', target_meta_property='og:description')
        else:
            prefix = 'Title: '
            h = HTMLParserGetElementsByTag('title', count=1)

        h.feed(str(self.content).replace("\n", ""))

        h.close()

        if len(h.content) > 0:
            text = html.unescape(h.content.strip())
        else:
            text = ''

        # Google Photo 用
        match = re_google_photo_remove_odd_params.search(text)
        if match and "goo" in text:
            text = match.group(1) + "=s1600"

        return prefix + text + postfix

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
            self.fetch(url, guess_encoding=True)
            if hasattr(self, "content_headers") and "text/html" in self.content_headers.get("content-type"):
                res += self.get_element_title(url=url) + "\n"
        return res.rstrip()


class SubcultureGaishutsu(Subculture):
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
            ago = u' %.1f 日くらい前に' % (ago_sec / (60*60*24))
        return u'おっ その %s は%s %s により既出ですね' % (url, ago, r.get('speaker'))

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


class SubcultureMETAR(Subculture):
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
            return u'%s (%.1f\u2103; %d\u3371; %s%%)\n%s' % (self.weather, self.temp_c, self.pressure, self.humidity, self.icon_url)



class SubcultureOmochi(Subculture):
    """ omochi """
    def response(self):
        omochi = [
            'http://icondecotter.jp/data/11787/1253637750/3da1de4437114e091d35483a03824989.png',
            'https://pbs.twimg.com/media/BcPKzauCQAEN7oR.png',
            'http://i.gyazo.com/5f7f28f4794fa6023afa3a0cab0c3ac0.png',
            'http://i.gyazo.com/5f7f28f4794fa6023afa3a0cab0c3ac0.png',
            'http://img-cdn.jg.jugem.jp/f29/2946929/20140106_445358.jpg',
            'http://img-cdn.jg.jugem.jp/f29/2946929/20140106_445355.jpg',
            'https://pbs.twimg.com/media/ByjWDq-CYAAeArB.jpg',
            'https://pbs.twimg.com/media/BsuorQICUAA3nMw.jpg',
            'http://33.media.tumblr.com/aa2a0b8f93a7499b1899c510536ce4a5/tumblr_n9l06rLgmw1qkllbso1_500.gif',
            'http://40.media.tumblr.com/277d6031c2a25ac4cc160acfc984fa8f/tumblr_myzslsgJMh1qkllbso1_500.png',
            'http://livedoor.blogimg.jp/nasuka7777/imgs/c/c/cc8c7ebb.jpg',
            'https://pbs.twimg.com/media/B3grzV5CEAAiCoz.jpg',
            'https://pbs.twimg.com/media/Bzq1yhwCcAE8jRn.jpg',
            'http://ecx.images-amazon.com/images/I/51VDBqtGQ4L.jpg',
            'http://prtimes.jp/i/9289/15/resize/d9289-15-340332-5.jpg',
            'https://pbs.twimg.com/media/BU_9vq6CAAAYv9x.jpg',
            'https://i.gyazo.com/539bccec6e34ccb189b9f2458f95e4cb.png',
            'https://i.gyazo.com/170e5975c586da83c414527442f018c1.png',
            'https://i.gyazo.com/f4df0e3220c86d17d39e932b7dad8233.png',
        ]

        # dont response within 30 seconds
        if self.check_flood(self.speaker, 30) is False:
            return None

        random.seed()
        return omochi[random.randrange(0, len(omochi))]


class SubcultureStone(Subculture):
    """ stone """
    def response(self):
        stone = [
            # Gyazo
            'http://i.gyazo.com/cc5cf9e9f19c4276af1380a18146eadb.png',
            'http://i.gyazo.com/671fee5ce52c6350ace3728fce53fa84.png',
            'http://i.gyazo.com/ca2b01ff7ceb4f3195e33025b7005554.png',
            'http://i.gyazo.com/e5b966c89fd9fd9711ab2d9acdb7daf1.png',
            'http://i.gyazo.com/254db6809c8bbb32e10c80ff8b731a65.png',
            'http://i.gyazo.com/dfce33d4bba619e315fa1a676d0c84ba.png',
            'http://i.gyazo.com/c0c780844c4b015ecfade90138332f22.png',
            'http://i.gyazo.com/30e9859104a68414b2c9f3b8a023ae00.png',
            'http://i.gyazo.com/716c9e12dafb47f2da1e31fbeeb6a467.png',
            'http://i.gyazo.com/a043f697cad2d34ee4febc071d47b03e.png',
            'http://i.gyazo.com/a12974aabdf48eb50e1f81d513546f15.png',
            'http://i.gyazo.com/41dd1a0d542504b44b6028ad472411ce.png',
            'http://i.gyazo.com/d0414248b36a5cfd3ef5456f1b73f28e.png',
            'http://i.gyazo.com/4c75f3c6393ed809472023e583508465.png',
            'http://i.gyazo.com/2e8cbd1c5b450ab7256579bd55a1487e.png',
            'http://i.gyazo.com/1c5243b9aaa91d651a57764a1cc33ef0.png',
            'http://i.gyazo.com/ed92327451d2e7faf581a2024589451f.png',
            'http://i.gyazo.com/3175440fd6c5329a9f35d5191b5920b2.png',
            'http://i.gyazo.com/4793f98f008e2abb1d28af4a38178c3a.png',
            'http://i.gyazo.com/b57b175072f7f9aaca93f1fc460cd63e.png',
            'http://i.gyazo.com/ba99fc4f1f0dc5c90f28cd2b4683a863.png',
            'http://i.gyazo.com/3c7269601fb9afab5c33e272f3054a28.png',
            'http://i.gyazo.com/e5de9dc949228363acb36ed0e3f6b1cb.png',
            'http://i.gyazo.com/72e4d75d8e21479ab50624ab88c8ce17.png',
            'http://i.gyazo.com/f652a12aa54ffd491de317cb981b48b9.png',
            'http://i.gyazo.com/0969e1c43acea1f70632b2157eba5793.png',
            'http://i.gyazo.com/99a4c3f45ee3758a37cac260c171c5d2.png',
            'http://i.gyazo.com/b83f854434de8b4bae0c9d5bb84365f4.png',
            'http://i.gyazo.com/f018d843af2338150b7522dfed84da08.png',
            'http://i.gyazo.com/1c5243b9aaa91d651a57764a1cc33ef0.png',
            'http://i.gyazo.com/3c7269601fb9afab5c33e272f3054a28.png',
            'http://i.gyazo.com/0969e1c43acea1f70632b2157eba5793.png',
            'http://i.gyazo.com/f018d843af2338150b7522dfed84da08.png',
            'http://i.gyazo.com/99a4c3f45ee3758a37cac260c171c5d2.png',
            'http://i.gyazo.com/4360b84e1d5d7861be1a964a9f74d0b8.jpg',

            # etc
            'http://i.gyazo.com/4fd0d04bd674ae6179d2e5de6340161f.png',
            'http://www.gohongi-beauty.jp/blog/wp-content/uploads/2013/08/stone_4.png',
            'http://shonankit.blog.so-net.ne.jp/blog/_images/blog/_285/shonankit/9223616.jpg',
            'http://shonankit.blog.so-net.ne.jp/blog/_images/blog/_285/shonankit/9223612.jpg',
            'http://nyorokesseki.up.seesaa.net/image/kesseki400_300.jpg',
            'http://shonankit.c.blog.so-net.ne.jp/_images/blog/_285/shonankit/02-3c13d.jpg',
            'http://livedoor.blogimg.jp/fknews/imgs/4/c/4c478d9b.jpg',
            'http://i.gyazo.com/29a38b2b9202862189d8f7a4df1e8886.png',
            'http://i.gyazo.com/183cade0a96dfcac84a113125a46bfa9.png',
            u'西山石\nhttp://i.gyazo.com/ed7b4e6adaa018c4a8212c7590a98ab3.png',
        ]

        if self.check_flood(self.speaker, 30) is False:
            return None

        random.seed()
        return stone[random.randrange(0, len(stone))]


class SubcultureWaterFall(Subculture):
    """ water fall """
    def response(self):
        urls = [
            u'http://i.gyazo.com/78984f360ddf36de883ec0488a4178cb.png',
            u'http://i.gyazo.com/684523b240128b6f0eb21825e52f5c6c.png',
        ]

        if self.check_flood(self.speaker, 10) is False:
            return None

        return '\n'.join(urls)


class SubcultureHai(Subculture):
    """ hai """
    def response(self):
        random.seed()

        res = None
        if random.randrange(0, 100) > 40:
            res = u'はい'
        else:
            res = u'はいじゃないが'

        return res


class SubcultureHitozuma(Subculture):
    """ hitozuma """
    def response(self):
        random.seed()

        res = None
        if random.randrange(0, 500) < self.doge_soku():
            if random.randrange(0, 100) > 0:
                res = u'はい'
            else:
                res = u'いいえ'

        return res


class SubcultureKCzuma(Subculture):
    """ KCzuma """
    def response(self):
        random.seed()

        res = None
        if random.randrange(0, 2000) < self.doge_soku():
            if random.randrange(0, 100) > 0:
                res = random.choice([u'K', u'K', u'Y', u'N', u'E', u'P', u'D', u'H', u'U', u'T', u'S', u'O', u'V', ]) + u'C'
            else:
                res = u'KC'
        return res

class SubcultureKC(Subculture):
    def response(self):
        random.seed()
        res = None

        ordeal = random.randrange(0, 100)
        if ordeal > 70:
            res = u'Yes, Kumagai Culture.'
        elif ordeal > 40:
            res = u'Yes, Kuzuha Culture.'
        elif ordeal > 20:
            res = u'No, Not Kumagai Culture.'
        elif ordeal < 5:
            res = u'Exactly, Kuzuha Culture.'
        return res

class AnotherIsMoreKnowerThanMe(Subculture):

    def response(self):
        knower = ['kumagai', 'kuzuha', 'ykic', 'niryuu', 'esehara', 'pha', 'doge', ]

        K = SubcultureKnowerLevelUp('', self.speaker)
        K.response()

        if 'JC' in self.text or 'JAL' in self.text:
            res = 'kuzuha culture'
        else:
            random.seed()
            res = 'No, %s culture.' % knower[random.randrange(0, len(knower))]

        return res


class HateSubculture(Subculture):

    def response(self):
        random.seed()
        return u'川\n' * (random.randint(0, 10) + 20)


class DogeAwayMessage(Exception):
    def __init__(self, msg):
        self.msg = msg


class SubcultureDogeGoAway(Subculture):

    def response(self):
        random.seed()
        if u'逃がす' in self.text:
            if self.check_doge_away() is False:
                self.doge_away(expire_sec=60*60)
                raise DogeAwayMessage(u'(自由)')
        elif u'捕' in self.text:
            if random.randrange(0, 100) > 50:
                self.doge_away(False)
                raise DogeAwayMessage(u'(不自由で邪悪)')
            else:
                raise DogeAwayMessage('http://i.gyazo.com/d8f75febb9d57057731fc38f4f0288d5.png')


class SubcultureDogeHouseStatus(Subculture):

    def response(self):
        self.check_doge_away()
        res = u'(犬' + (u'は逃げました)' if self.doge_is_away else u'はいる)')

        with open("dogehouse.txt", "r") as fp:
            res += fp.read().decode('utf_8')

        raise DogeAwayMessage(res)


class SubcultureKimoti(Subculture):

    def response(self):
        otoko_no_bigaku = [
            "https://i.gyazo.com/57ce687dc640ac945a38b07221dde69e.png",
            "https://i.gyazo.com/a22873a222cdd6366d644298627a3717.png",
            "https://i.gyazo.com/bd420c4c42f76e81fe1f937a57745e37.jpg",
            "https://i.gyazo.com/83c58eb1db4fb1a5b36b4c7b35d5c2de.jpg",
            "https://i.gyazo.com/222e2cbba284710e0e9d289dfcc5f217.jpg",
            "https://i.gyazo.com/6d673a77640232ff0584c3ccce6f5e2f.jpg",
            "https://i.gyazo.com/ed97b6fe05ea6533b06185d4671c2610.jpg",
            "https://i.gyazo.com/d3668cab2d34ff8e25910d06a58376e8.jpg",
            "https://i.gyazo.com/48c1cacec98df70130c0739bf185cfe7.jpg",
            "https://i.gyazo.com/45064e2b054428461ca91fa56fe718b3.jpg",
            "https://i.gyazo.com/cf4605eab0a6953753f14e6540e7f916.jpg",
            "https://i.gyazo.com/f81a179087b49349b1ba72bed3ab77a1.jpg",
            "https://i.gyazo.com/480b38890a3c3c2ca826b09de5d32eed.jpg",
            "https://i.gyazo.com/a05b7cf820c103ae9daf16e45be6ef70.jpg",
            "https://i.gyazo.com/9952fe3b70c428989f83a1a9b59856c4.jpg",
            "http://farm6.static.flickr.com/5229/5757984661_c03a82b843.jpg",
            "https://embed.gyazo.com/5f2af84410714fcd0721c3689ae4e4b0.jpg",
            "https://i.gyazo.com/828c0395a0ac596fd33e7a3da86f4c1a.jpg",
            "https://i.gyazo.com/b73667b5c31d1a847828b1b17c9e661a.png",
            "https://i.gyazo.com/03c62c50700976b4486f8a80b487f7f9.jpg",
            "https://i.gyazo.com/a30020820a98347edad1e7be7add3d44.jpg",
            "https://0x00.be/photo/tajima25.gif",
            "https://i.gyazo.com/5706cf8b2221ae07b1f16017b18ad032.png",
            "https://i.gyazo.com/9b5c887fdd25fe91b94ba93218d1871c.png",
            "https://i.gyazo.com/4439e29666882249fc8687641b746fc8.jpg",
            "https://i.gyazo.com/2746f6cddeb71353d13b7e1c2886a22d.jpg",
            "https://i.gyazo.com/53590ce997cfd7ccfff88d983e1b3731.jpg",
            "https://i.gyazo.com/48bea2b64f30f9a413991920afa4a612.jpg",
            "https://i.gyazo.com/58adb3dbf0e17846e1c98202afa87c94.png",
            "https://i.gyazo.com/bb3e3a715b9c55d9c3dabbbe040ea41a.jpg",
            "https://i.gyazo.com/0258ee4ef2f31b9cc56693b52cd78fe8.jpg",
            "https://i.gyazo.com/af1c7344df585a266b02814593e93769.jpg",
            "https://i.gyazo.com/6506f843c8f7c1f6138b91493b271293.jpg",
            "https://i.gyazo.com/7d7e0b8a31fd736b33913dab7bc2b5fb.jpg",
            "https://i.gyazo.com/e9f13c8f47f5f819cd36034f108617ee.jpg",
            "https://i.gyazo.com/c5606232ff2ac81d04b4bbbaaea5bc2a.jpg",
            "https://i.gyazo.com/67919378fc4ab09346175756d253025f.png",
            "https://i.gyazo.com/d5162f92ce481b681c3a76a9555e099b.jpg",
            "https://i.gyazo.com/2eeb5da684bdd967ecad80405a19c312.jpg",
            "https://i.gyazo.com/177fe6cc05338774f05f1fb2b3b8d1ca.png",
            "https://i.gyazo.com/e4f91f32e2ef55d179bab162d6ad06da.png",
            "https://i.gyazo.com/51e7830f7644444e7d3f1b5c301c04d1.png",

            # takano32
            "https://i.gyazo.com/93cf8f0354831e42cc8fd83e3c5a005c.png",
            
            # pha
            "https://i.gyazo.com/80ef198057bd98d23d5d625cd7ef312e.png",
        ]

        if self.check_flood(self.speaker, 30) is False:
            return None

        random.seed()
        return otoko_no_bigaku[random.randrange(0, len(otoko_no_bigaku))]


class SubcultureKimotiYorokobi(SubcultureKimoti):
    def response(self):
        if self.check_flood(self.speaker, 30) is False:
            return None
        return "https://i.gyazo.com/03c62c50700976b4486f8a80b487f7f9.jpg"


class SubcultureCMD(Subculture):

    def response(self):
        cmd = [u'https://twitter.com/chomado/status/1164468142195662850', u'(*ﾟ▽ﾟ* っ)З', u'(((o(*ﾟ▽ﾟ*)o)))', u'┌（┌ *ﾟ▽ﾟ*）┐', u'(((o===(*ﾟ▽ﾟ*)===o)))', u'┌（┌ *ﾟ▽ﾟ*）┐(*ﾟ▽ﾟ* っ)З', u'Xamarinはいいぞ', u'https://twitter.com/loadlimits/status/1124773878872416256' ]

        if self.check_flood(self.speaker, 30) is False:
            return None

        random.seed()
        return cmd[random.randrange(0, len(cmd))]


class SubcultureTMD(Subculture):

    def response(self):

        shacho = [
            'http://res.cloudinary.com/thefader/image/upload/s--tAIiYzeK--/w_1440,c_limit,q_jpegmini/vtus59nok5kywxecq',
            'https://i.gyazo.com/e361c623a76212499a3878e74dc38a07.jpg',
            'https://i.gyazo.com/627e4a1c291252a2686f1f26d357812c.jpg',
            'https://i.gyazo.com/cbab315f3251cf36d380e38e89b41243.jpg',
            'https://i.gyazo.com/92684b965d70167881ebb79406b4684b.jpg',
            'https://i.gyazo.com/29e5275253a9fe3ee0d224f174a767c4.jpg',
            'https://i.gyazo.com/21892a43c727ee347c136e2ae2992f26.jpg',
            'https://i.gyazo.com/7a962ee36e29c6266e2d7e60a63115a3.jpg',
            'https://i.gyazo.com/ad56d43ea09569c38a5ff661f86f56a0.jpg',
            'https://i.gyazo.com/b4f71013cb8e33f04d46488ff92ec107.jpg',
            'https://i.gyazo.com/06cbac04f18b85c7288038b7dec918d4.jpg',
            'https://i.gyazo.com/c38034e6df985514bca1d7237c76ec67.jpg',
            'https://i.gyazo.com/95dfbbb88cb7afb44e9d290b551f2af0.jpg',
            'https://i.gyazo.com/4906911f01ff464eb58fb429556e4076.jpg',
            'https://i.gyazo.com/a3f6ec22696e9bd52df36247e5147225.jpg',
        ]


        if self.check_flood(self.speaker, 30) is False:
            return None

        random.seed()
        return shacho[random.randrange(0, len(shacho))]


class SubcultureXamarin(Subculture):

    def response(self):
        words = [u'人脈♪', u'Xamarinはいいぞ', ]

        if self.check_flood(self.speaker, 30) is False:
            return None

        random.seed()
        return words[random.randrange(0, len(words))]


class SubcultureKotoshinoKanji(Subculture):

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


class SubculturePizza(Subculture):

    def response(self):

        pizzayas = [
            'https://www.dominos.jp/',
            'https://www.pizza-la.co.jp/',
            'https://pizzahut.jp/',
        ]


        if self.check_flood(self.speaker, 30) is False:
            return None

        random.seed()
        return pizzayas[random.randrange(0, len(pizzayas))]


class SubcultureMineo(Subculture):

    def response(self):
        self.fetch("https://0x00.be/cgi-bin/dogewunderground/mineo_latency.cgi?multispan=true")
        return None


class NotSubculture(object):
    """ main """
    debug = True
    body = None
    message = None
    texts = None
    enable_acl = True
    is_slack = False
    sub = None
    passerby_channel = False

    dic_base = {
        'https?://gyazo.com': SubcultureGyazoScraper,
        'https?': SubcultureTitleExtract,
        # u'https://twitter.com/': SubcultureTwitterScraper,
    }

    dic_extend = {
        '^(Ｓ|ｓ|S|s)(ｕｂ|ub)\s*((Ｃ|ｃ|C|c)(ｕｌｔｕｒｅ|ulture))?$': 'No',
        u'ベンゾ': u'曖昧/d',
        u'(カエリンコ|かえりんこ)': u'いいですよ',
        u'^(Ｔａｒｏ|Taro|太郎|Ｙａｒｏ|Yaro|野郎)$': 'No',
        u'(:?\(sun\)|おはようございます|ohayougozaimasu|起きた|おきた|ぉぁょ)$': u'☀',
        u'^サ(ブ|ヴ)(カルチャー)?(なの)?(では)?(\?|？|。)*$': '?',
        u'^(\?|？)$': '?',
        u'^はい(じゃないが)?$': SubcultureHai,
        u'(kumagai|ykic|kuzuha|esehara|tajima|niryuu|takano(:?32)?|usaco|voqn|tomad|yuiseki|pha|布|jal\JAL) culture': AnotherIsMoreKnowerThanMe,
        '^[KYETNOSVP1UJ]C$': AnotherIsMoreKnowerThanMe,
        u'^[KkＫｋ][CcＣｃ][\?？]$': SubcultureKC,
        u'さすが\s?(kuzuha|ykic|usaco|pha|esehara|niryuu|tajima|usaco)\s?(さん)?': u'わかるなー',
        u'さすが\s?(くまがい|熊谷|kumagai|tinbotu|ｋｕｍａｇａｉ|ｔｉｎｂｏｔｕ)\s?(さん)?': u'?',
        u'わかるなー*$': SubcultureKnowerLevel,
        u'(doge2048|[Jj][Aa][Ll]\s?(123|516)|[Mm][Hh]370)': u'なるほど',
        u'(鐵|鐡)道(では)?$': u'おっ',
        u'電車': u'鐵道または軌道車/b',
        u'戦い': u'戰いでしょ/b',
        u'拝承': u'拝復/c',
        # u'あなた': u'あなたとJAVA, \n今すぐダウンロー\nド\nhttps://www.java.com/ja/',
        # u'([^#]|^)[Cc]h?at[Ww][ao]rk': u'http://b.hatena.ne.jp/chatwark/',
        u'^(おもち|OM[CT])$': SubcultureOmochi,
        u'^(喜び|悦び|歓び|慶び|よろこび)の(氣持ち|気持ち|きもち|KMT)$': SubcultureKimotiYorokobi,
        u'^(氣持ち|気持ち|きもち|KM[CT])$': SubcultureKimoti,
        u'^石$': SubcultureStone,
        u'西山石': u'http://i.gyazo.com/ed7b4e6adaa018c4a8212c7590a98ab3.png',
        u'山だ?$': u'やまいくぞ/c',
        u'がんばるぞい(！|!)?$': 'http://cdn-ak.f.st-hatena.com/images/fotolife/w/watari11/20140930/20140930223157.jpg',
        u'ストール$': u'はい',
        u'(俺は|おれは)?もう(だめ|ダメ)だ[ー〜]*$': u'どうすればいいんだ/d',
        u'どうすればいいんだ': u'おれはもうだめだ/d',
        u'(は|の|とか)((きも|キモ)いの|(サブ|サヴ))(では)?$': u'?',
        u'^(クソ|糞|くそ)(すぎる|だな)ー?$': u'ごめん/c',
        u'^(?:(今日?|きょう)?外?(暑|寒|あつ|さむ|さみ|あち)い?(ー|のかな|？|\?)|METAR|天気)$': SubcultureMETAR,
        u'^消毒$': SubcultureWaterFall,
        u'^流す$': HateSubculture,
        u'^他人のわかり': SubcultureKnowerLevelGet,
        # u'([わゎ分][\/\s\|｜　]*?[か○][\/\s\|｜　]*?[らりるっ]|なるほど|はい|お[\/\s　]*?も[/\s　]*?ち|かわいい|便利|タダメシ|[TDdS]+$|機運|老|若|おっ|ですね|サ[\/\s\|｜　]*?[ブヴ]|布|ヤバい|だる|水|コー|ムー|野方|高円寺|ルノ|サイエンス|野郎|カルチャー|左翼|あっ|ウッ|速|陣営|ゴミ|オタサー|姫|寿司|危険|HOD|椅○)': SubcultureKnowerLevelUp,
        u'オレオ': u'オレオ',
        u'(?:社|無職|辞め|仏教|瞑想|無常|数学|OMD|老|帰|[働動行][きい]たくな|出家|転|つま[らん][なん]|休|不景気|舟|眠|だる|熊野|親|介護|[帰か]え?り[たて]|ポキ|気.*?[なね][しー]|終わり|職|怠|引退|オワ)': SubcultureRetirementLevelUp,
        u'^他人の社会': SubcultureRetirementLevelGet,
        u'たい': SubcultureSilent,
        'http': SubcultureGaishutsu,
        u'うひー': u'うひーとかやめてくれる',
        # u'(Mac|マック|OSX|osx)': u'マックパワー/aB',
        u'^弁当$': u'便當だろ',
        u'\bシュッ\b': u'シュッ！シュッ！\nんっ ...',
        u'(止|と)ま(ら|ん)ない(んす|んすよ)?': u'https://i.gyazo.com/e50a1e1b5dd2a5cdd5c388f654bcf8a4.gif',
        u'^((ヤバ|やば)(イ|い)|yabai)$': u'WHOOP! WHOOP! PULL UP!!!/aA',
        '.+': SubcultureHitozuma,
        '..+': SubcultureKCzuma,
        '^(?!.*http).*$': SubcultureNogata,  # except http
        '.*': SubcultureAtencion,  # 同じキーはだめ
        u'^\(犬?(逃が?す|捕まえる)\)$': SubcultureDogeGoAway,
        u'^\(犬小屋\)$': SubcultureDogeHouseStatus,
        u'^\(コラッ\)$': SubcultureDogeDetailStatus,
        u'\(犬\)': SubcultureShowDogeSoku,
        u'\(犬転生\)': SubcultureSelfUpdate,
        u'かわいい': u'ちーちゃんかわいいね/b',
        u'ナイス案件': u'http://i.gyazo.com/39111fc1ffe29ec1976696b3a95c511d.png',
        u'((高野|たかの|タカノ|takano)さん|うひー)$': u'http://0x00.be/photo/takano32.jpg/dF',
        u'う(ぜ[ーえ]|ざい)': u'オマエモナー/bC',
        u'^[Nn][Oo]$': u'Noじゃないが/c',
        u'官邸': u'http://i.gyazo.com/b8c2408c91cd49ecbe6fd9348e3bcf87.png',
        u'性欲': u'性欲を持て余す/cC',
        u'(ネムイ|ねむい|ねみー|眠い)': u'http://i.gyazo.com/4f6e3d16fecb81f5c7b5cb371efa9074.jpg/aB',
        u'\(飼い主\)': u'tinbotu',
        u'サイエンス': 'http://i.gyazo.com/154e800fd6cdb4126eece72754c033c8.jpg/bF',
        u'^わかりシート$': 'https://docs.google.com/spreadsheets/d/16hNE_a8G-rehisYhPp6FppSL0ZmQSE4Por6v95fqBmA/edit#gid=0',
        u'^姫乃たまシート$': 'https://docs.google.com/spreadsheets/d/1W2lwTx5ib9x_uhigFiCBN534gIcmudAQfLoJtSi6anY/edit#gid=0',
        u'^NHR$': u'うへえへへえぁぁぁあぁ',
        u'^TMD$': SubcultureTMD,
        u'^CMD$': SubcultureCMD,
        u'^EZ$': u'説明の必要はない',
        u'^Xamarin$': SubcultureXamarin,
        u'^(yosh?io|芳雄|よしお|ヨシオ|ヨタ)$':
        """:yos-1-1::yos-1-2::yos-1-3::yos-1-4:
:yos-2-1::yos-2-2::yos-2-3::yos-2-4:
:yos-3-1::yos-3-2::yos-3-3::yos-3-4:
:yos-4-1::yos-4-2::yos-4-3::yos-4-4:
        """,
        u'^(big|BIG|Big)( |　|-)?(takano32)$':
        """:takano32-1-1::takano32-2-1::takano32-3-1::takano32-4-1:
:takano32-1-2::takano32-2-2::takano32-3-2::takano32-4-2:
:takano32-1-3::takano32-2-3::takano32-3-3::takano32-4-3:
:takano32-1-4::takano32-2-4::takano32-3-4::takano32-4-4:
        """,
        u'^(今年|去年|201[0-7]年)の漢字$': SubcultureKotoshinoKanji,
        u'\(ピザ\)': SubculturePizza,
        '^mineo$': SubcultureMineo,
    }

    def __init__(self):
        self.httpheaderHasAlreadySent = False

    def httpheader(self, header="Content-Type: text/plain; charset=UTF-8\n"):
        if self.httpheaderHasAlreadySent is False:
            print(header)
            self.httpheaderHasAlreadySent = True

    def parse_slack_outgoing_webhooks(self, http_body):
        params = parse_qsl(http_body)
        params = dict(params)

        """ generate a *pseudo* message of Lingr """
        self.message = {}
        self.message["events"] = []
        self.message["events"].append({})
        self.message["events"][0]["message"] = {}
        self.message["events"][0]["message"]["id"] = -1
        self.message["events"][0]["message"]["type"] = "user"
        self.message["events"][0]["message"]["speaker_id"] = params.get("user_name")
        self.message["events"][0]["message"]["nickname"] = params.get("user_name")
        self.message["events"][0]["message"]["text"] = params.get("text")
        self.message["events"][0]["message"]["room"] = params.get("team_domain")
        self.message["events"][0]["message"]["slack_channel"] = params.get("channel_name")  # extra
        d = datetime.datetime.fromtimestamp(float(params.get("timestamp"))).isoformat()
        self.message["events"][0]["message"]["timestamp"] = d + 'Z'



    def read_http_post(self, method=None, user_agent=None, http_post_body=None):
        if self.body is None and method == 'POST':
            self.body = http_post_body

            if type(user_agent) is str and user_agent.find("Slackbot") != -1:
                self.is_slack = True
                return self.parse_slack_outgoing_webhooks(self.body)

            try:
                self.message = json.loads(self.body)
            except Exception:
                if self.debug:
                    self.httpheader()
                    print(traceback.format_exc())
                    sys.exit(0)
                else:
                    self.httpheader()
                    print("json decode error:" + self.body)
                    sys.exit(0)
        else:
            print("Status: 400 Bad request\n\n400")
            sys.exit(0)

    def acl(self, acl, ip_address):
        if type(acl) is not list:
            return False
        ip = ipaddress.ip_address(ip_address)
        for address_block in acl:
            block = ipaddress.IPv4Network(address_block)
            if ip in block:
                return True
        return False

    def check_acl(self, acl):
        remote_addr = None

        xff = os.environ.get('HTTP_X_FORWARDED_FOR')
        if type(xff) is str:
            remote_addr = xff.split(',')[-1].strip()
        else:
            remote_addr = os.environ.get('REMOTE_ADDR')

        if type(remote_addr) is str:
            return self.acl(acl, remote_addr)
        return False


    def response(self):
        if self.is_slack:
            self.httpheader(header="Content-Type: application/json; charset=UTF-8\n")
        else:
            self.httpheader()

        if os.path.exists("quiet") or type(self.message) is not dict:
            return

        sub = Subculture()
        self.sub = sub
        sub.check_doge_away()

        response_modifier = {
            'a': .01,  # 1/100
            'b': .1,
            'c': .3,
            'd': .5,
            'e': .8,
            'f': 2.,
            'g': 4.,
            'A': 1/.01,  # Doge's soku multiplier
            'B': 1/.1,
            'C': 1/.3,
            'D': 1/.5,
            'E': 1/.8,
            'F': 1/2.,
            'G': 1/4.,
            'H': 1/8.,
        }

        bridged_channel_list = ['arakawatomonori', 'myroom', 'tinbotu']  # team_domain or Lingr room
        passby_channel_list = ['tarekomi', ]  # not bridged
        denied_bot_list = ['slackbot', ]

        # 自発的発言
        if self.message.get('events') is None and sub.doge_is_away is not True:
            token = sub.spontaneous(name=self.message.get('name'), key=self.message.get('key'))
            t = 15
            if type(token) is dict:
                try:
                    t = int(max(self.message.get('anti_double_sec'), token.get("antidouble")))
                except:
                    pass
                sub.say_lingr(self.message.get('body'), self.message.get('name'), t)
                sub.say_slack(self.message.get('body'), self.message.get('name'), t)
            else:
                print("401 Unauthorized")
            return

        if self.enable_acl is True and self.is_slack is False and self.check_acl(sub.settings.get("hosts_allow_lingr")) is False:
            print("403 Forbidden")
            return

        response_modifier_re = re.compile(r'(.+?)\/([a-zA-Z]+)$')
        doge_soku = sub.doge_soku()
        if doge_soku < 1:
            doge_soku = 1

        random.seed()
        for n in self.message['events']:
            if 'text' in n['message']:
                speaker = n['message']['speaker_id']
                text = n['message']['text']

                dic = copy.copy(self.dic_base)
                if n['message']['room'] in bridged_channel_list:
                    dic.update(self.dic_extend)
                    if n['message'].get('slack_channel') in passby_channel_list:
                        self.passerby_channel = True
                    else:
                        self.passerby_channel = False
                else:
                    self.passerby_channel = True

                # anti pang-pong
                if speaker in denied_bot_list:
                    return

                for dict_k, dict_res in dic.items():
                    pattern = re.compile(dict_k)
                    if pattern.search(text):

                        try:
                            if inspect.isclass(dict_res):
                                I = dict_res(text, speaker)
                                r = I.response()
                                if sub.doge_is_away is not True and r:
                                    yield r
                            elif sub.doge_is_away is not True:
                                # 修飾子を見て返事するか決める
                                threshold = 1.
                                prob_m = response_modifier_re.search(dict_res)
                                if prob_m:
                                    dict_res = prob_m.groups()[0]
                                    for m in list(prob_m.groups()[1]):
                                        if not m in response_modifier:
                                            continue
                                        if m.islower():
                                            threshold *= response_modifier[m]
                                        else:
                                            threshold *= response_modifier[m] * doge_soku

                                r = random.random()-.1
                                # print "thres: %f > %f, doge:%f" % (threshold, r, doge_soku)
                                if threshold > r:
                                    yield dict_res
                        except DogeAwayMessage as e:
                            yield e.msg

    def say(self, slack=False, lingr=True):
        resp = "\n".join(tuple(self.response())).rstrip("\n")
        if slack:
            self.sub.say_slack(message=resp, anti_double=False)
            # Lingr にも話す
            self.sub.say_lingr(message=resp, anti_double=False)
            lingr = False

        if lingr:
            resp_demoji = emoji.demojize(resp)
            print(resp_demoji, end='')
            if not self.passerby_channel:
                self.sub.say_slack(message=resp, anti_double=False)


if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

    no = NotSubculture()
    post_body = sys.stdin.read()
    no.read_http_post(method=os.environ.get('REQUEST_METHOD'), user_agent=os.environ.get('HTTP_USER_AGENT'), http_post_body=post_body)
    no.say(slack=no.is_slack, lingr=False)
