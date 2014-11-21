#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 sts=4 ff=unix ft=python expandtab

import os
import sys
import json
import re
import traceback
import requests
import random
import codecs
import inspect


class Subculture(object):
    """ abstract """
    content = None
    pick_re = ''

    def __init__(self, text=None):
        self.pick_re = re.compile(self.pick_re)

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

    def response(self):
        """ abstract """
        return None


class SubcultureGyazoScraper(Subculture):
    """ gyazo image url extactor """
    pick_re = '<meta content="(http://i.gyazo.com/([0-9a-z\.]+))" name="twitter:image" />'

    def __init__(self, text=None):
        self.pick_re = re.compile(self.pick_re)
        if text is not None:
            self.fetch(text)

    def response(self):
        m = self.pick_re.search(self.content)
        if m and m.group():
            return m.group(1)
        else:
            return None


class SubcultureMETAR(Subculture):
    """ Weather METARs """
    url = 'http://api.openweathermap.org/data/2.5/weather?q=Tokyo,jp'

    def __init__(self, text=None):
        self.fetch(self.url)

    def response(self):
        try:
            w = json.loads(self.content)
            temp_c = float(w["main"]["temp"]) - 273.15
            weather = w["weather"][0]["description"]
            icon_url = 'http://openweathermap.org/img/w/' + w["weather"][0]["icon"] + '.png'
            pressure = int(w["main"]["pressure"])
            humidity = int(w["main"]["humidity"])

            return u'%s (%.1f\u2103; %d\u3371; %d%%)\n%s' % (weather, temp_c, pressure, humidity, icon_url)

        except:
            return traceback.format_exc()


class SubcultureOmochi(Subculture):
    """ omochi """
    def response(self):
        omochi = [
            'http://limg3.ask.fm/assets/318/643/185/thumb/15.png',
            'http://icondecotter.jp/data/11787/1253637750/3da1de4437114e091d35483a03824989.png',
            'https://pbs.twimg.com/media/BcPKzauCQAEN7oR.png',
            'http://www.ttrinity.jp/_img/product/21/21201/1489293/1689893/4764618/product_img_f_4764618.jpg',
            'http://zigg.jp/wp-content/uploads/2014/05/00_Icon.png',
            'http://i.gyazo.com/5f7f28f4794fa6023afa3a0cab0c3ac0.png',
            'http://i.gyazo.com/5f7f28f4794fa6023afa3a0cab0c3ac0.png',
            'http://img-cdn.jg.jugem.jp/f29/2946929/20140106_445358.jpg',
            'http://img-cdn.jg.jugem.jp/f29/2946929/20140106_445355.jpg',
            'https://pbs.twimg.com/media/ByjWDq-CYAAeArB.jpg',
            'https://pbs.twimg.com/media/BsuorQICUAA3nMw.jpg',
            ]
        random.seed()
        return omochi[random.randrange(0, len(omochi))]

class SubcultureStone(Subculture):
    """ stone """
    def response(self):
        stone = [
            'http://i.gyazo.com/4fd0d04bd674ae6179d2e5de6340161f.png',
            'http://www.gohongi-beauty.jp/blog/wp-content/uploads/2013/08/stone_4.png',
            'http://shonankit.blog.so-net.ne.jp/blog/_images/blog/_285/shonankit/9223616.jpg',
            'http://shonankit.blog.so-net.ne.jp/blog/_images/blog/_285/shonankit/9223612.jpg',
            'http://nyorokesseki.up.seesaa.net/image/kesseki400_300.jpg',
            'http://shonankit.c.blog.so-net.ne.jp/_images/blog/_285/shonankit/02-3c13d.jpg?c=a1',
            'http://livedoor.blogimg.jp/fknews/imgs/4/c/4c478d9b.jpg',
            'http://i.gyazo.com/29a38b2b9202862189d8f7a4df1e8886.png',
            'http://i.gyazo.com/183cade0a96dfcac84a113125a46bfa9.png',
            'http://i.gyazo.com/ed7b4e6adaa018c4a8212c7590a98ab3.png',
            ]
        random.seed()
        return stone[random.randrange(0, len(stone))]

class SubcultureHitozuma(Subculture):
    """ hitozuma """
    def response(self):
        random.seed()

        res = None
        if random.randrange(0, 100) == 0:
            if random.randrange(0, 100) > 0:
                res = u'はい'
            else:
                res = u'いいえ'

        return res

class AnotherIsMoreKnowerThanMe(Subculture):

    def response(self):
        knower = ['kuzuha', 'ykic', 'esehara']
        random.seed()
        return 'No, %s culture.' % knower[random.randint(0, len(knower))]
        

class NotSubculture(object):
    """ main """
    debug = True
    body = None
    message = None
    texts = None
    dic = {'^(Ｓ|ｓ|S|s)(ｕｂ|ub)\s*((Ｃ|ｃ|C|c)(ｕｌｔｕｒｅ|ulture))?$': 'No',
           u'ベンゾ': u'曖昧',
           u'カエリンコ': u'いいですよ',
           u'^(Ｔａｒｏ|Taro|太郎|Ｙａｒｏ|Yaro|野郎)$': 'Esehara Likes Taro and Yaro.',
           u'(:?\(sun\)|おはようございます|ohayougozaimasu)': u'☀',
           u'^サ(ブ|ヴ)(カルチャー)?(なの)?(では)?(\?|？|。)*$': '?',
           u'^(\?|？)$': '?',
           u'^はい(じゃないが)?$': u'はい',
           u'kumagai culture': AnotherIsMoreKnowerThanMe,
           u'さすが\s?(kuzuha|ykic|usaco|pha|esehara|niryuu|tajima)\s?(さん)?': u'わかるなー',
           u'さすが\s?(くまがい|熊谷|kumagai|tinbotu|ｋｕｍａｇａｉ|ｔｉｎｂｏｔｕ)\s?(さん)?': u'?',
           u'わかるなー$': u'おっ',
           u'(doge2048|JAL\s?123)': u'なるほど',
           u'(鐵|鐡)道(では)?$': u'おっ',
           u'電車': u'鐵道または軌道車',
           u'戦い': u'戰いでしょ',
           u'拝承': u'拝復',
           u'あなた': u'あなたとJAVA, 今すぐダウンロー\nド\nhttps://www.java.com/ja/',
           u'^おもち$': SubcultureOmochi,
           u'^石$': SubcultureStone,
           u'山だ?$': u'やまいくぞ',
           u'がんばるぞい(！|!)?$': 'http://cdn-ak.f.st-hatena.com/images/fotolife/w/watari11/20140930/20140930223157.jpg',
           u'ストールするぞ(ほんとに)?$': u'はい',
           u'(俺は|おれは)?もう(だめ|ダメ)だ$': u'どうすればいいんだ',
           u'どうすればいいんだ': u'おれはもうだめだ',
           u'(は|の|とか)((きも|キモ)いの|(サブ|サヴ))(では)?$': u'?',
           u'^(クソ|糞|くそ)(すぎる|だな)ー?$': u'ごめん',
           'http://gyazo.com': SubcultureGyazoScraper,
           u'^(?:(今日?|きょう)?外?(暑|寒|あつ|さむ)い(のかな|？|\?)|METAR|天気)$': SubcultureMETAR,
           '.': SubcultureHitozuma,
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
                for k, v in self.dic.iteritems():
                    pattern = re.compile(k)
                    m = pattern.search(t)
                    if m:
                        if inspect.isclass(v):
                            I = v(t)
                            r = I.response()
                            if r:
                                yield r
                        else:
                            yield v


if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

    no = NotSubculture()
    post_body = sys.stdin.read()
    no.read_http_post(os.environ.get('REQUEST_METHOD'), post_body)
    for r in no.response():
        print r
