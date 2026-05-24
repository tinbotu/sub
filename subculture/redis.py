# -*- coding: utf-8 -*-

import json
import math
import os
import pickle
import random
import re
import time

import git
import redis

from .base import DogeAwayMessage, Subculture

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


class KnowerLevelSubculture(RedisSubculture):

    def response(self):
        level = self.conn.incr("knower-%s" % self.speaker, 1)
        return "おっ、分かり度 %d ですか" % level


class KnowerLevelUpSubculture(RedisSubculture):
    pass


class KnowerLevelGetSubculture(RedisSubculture):

    def response(self):
        speakers_blacklist = ["knower-tests", "knower-None", ]
        res = ''
        speakers = self.conn.keys("knower-*")

        for s in speakers:
            if s not in speakers_blacklist:
                res += "%s: %s\n" % (s, self.conn.get(s))

        return res


class AnotherIsMoreKnowerThanMe(RedisSubculture):

    def response(self):
        knower = ['kumagai', 'kuzuha', 'ykic', 'niryuu', 'esehara', 'pha', 'doge', ]

        K = KnowerLevelUpSubculture('', self.speaker)
        K.response()

        if 'JC' in self.text or 'JAL' in self.text:
            res = 'kuzuha culture'
        else:
            random.seed()
            res = 'No, %s culture.' % knower[random.randrange(0, len(knower))]

        return res


class RetirementLevelUpSubculture(RedisSubculture):
    def response(self):
        self.conn.incr("retirement-%s" % self.speaker, 1)
        return None


class RetirementLevelGetSubculture(RedisSubculture):

    def response(self):
        speakers_blacklist = ["knower-tests", "knower-None", ]
        res = ''
        speakers = self.conn.keys("retirement-*")

        for s in speakers:
            if s not in speakers_blacklist:
                res += "%s: %s\n" % (s, self.conn.get(s))

        return res


class AtencionSubculture(RedisSubculture):
    """ me? """
    atencion = 0
    soku = 0

    atencion_T = .1
    soku_T = .2

    atencion_dic = {
        '犬': 150,
        'イヌ': 100,
        '^お前': 30,
        'main': 10,
        'bot': 10,
        'メイン': 10,
        'サブ': 4,
        'doge': 50,
    }
    soku_dic = {
        '犬': 10,
        'うぜー': -100,
        '糞': -80,
        'クソ': -100,
        '黙れ': -150,
        'はい$': 10,
        'はいじゃないが': -20,
        'おっ': 20,
        'オッ': 20,
        'いいですね': 10,
        '寿司': 5,
        '[分|わ]か[らりるっん]': 20,
        'かわいい': 10,
        ' T ': 50,
        'だる': -10,
        '姫': 20,
        'サ[ブヴ]': 30,
        'ゴミ': 10,
        '(馬鹿|バカ)': 40,
        '機運': 20,
        'ウッ': 10,
        '危険': 10,
        'なるほど': 10,
        'おもち': -10,
        '(ない|ねーよ?)$': -30,
        '絡み方が悪質': 50,
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

        if self.text == '犬寝ろ':
            pass
        else:
            if self.soku is None:
                self.soku = 0
            else:
                self.soku = float(self.soku)

            for dict_k, score in self.atencion_dic.items():
                if re.compile(dict_k).search(self.text):
                    n1 = self.atencion + float(score)
                    self.atencion = self.lpf(self.atencion, n1, self.atencion_T)
            else:
                self.atencion = float(self.atencion) - 1

            me_factor = 1 + math.sqrt(abs(self.atencion))
            for dict_k, score in self.soku_dic.items():
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
            # msg = "new soku:%.2f, internal_soku:%.2f, internal_atencion:%.2f" % (inu_soku, self.soku, self.atencion)
            return 'オッ'


class DogeDetailStatusSubculture(RedisSubculture):
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

        return 'クゥーン(soku: %.2f, internal_atencion: %.2f, internal_soku: %.2f)' % (
            inu_soku, inu_internal_atencion, inu_internal_soku)


class SelfUpdateSubculture(RedisSubculture):
    def response(self):
        repo = git.Repo('.')
        if repo.is_dirty():
            return '私は穢れている'

        previous_head = repo.head.commit.hexsha
        repo.remotes.origin.pull('master')

        if repo.head.commit.hexsha == previous_head:
            return '?'
        else:
            os.system("make update_packages 1>deploy.log 2>&1")
            url = 'https://github.com/tinbotu/sub/commit/%s' % (repo.head.commit.hexsha,)
            msg = 'ニャーン %s %s %s\n%s' % (repo.head.commit.hexsha,
                                                  repo.head.commit.committer,
                                                  repo.head.commit.message,
                                                  url)
            return msg


class ShowDogeSokuSubculture(RedisSubculture):
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


class DogeGoAwaySubculture(RedisSubculture):

    def response(self):
        random.seed()
        if '逃がす' in self.text:
            if self.check_doge_away() is False:
                self.doge_away(expire_sec=60*60)
                raise DogeAwayMessage('(自由)')
        elif '捕' in self.text:
            if random.randrange(0, 100) > 50:
                self.doge_away(False)
                raise DogeAwayMessage('(不自由で邪悪)')
            else:
                raise DogeAwayMessage('http://i.gyazo.com/d8f75febb9d57057731fc38f4f0288d5.png')


class DogeHouseStatusSubculture(RedisSubculture):

    def response(self):
        self.check_doge_away()
        res = '(犬' + ('は逃げました)' if self.doge_is_away else 'はいる)')

        with open("dogehouse.txt", "r") as fp:
            res += fp.read()

        raise DogeAwayMessage(res)


class OmochiSubculture(RedisSubculture):
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


class StoneSubculture(RedisSubculture):
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
            '西山石\nhttp://i.gyazo.com/ed7b4e6adaa018c4a8212c7590a98ab3.png',
        ]

        if self.check_flood(self.speaker, 30) is False:
            return None

        random.seed()
        return stone[random.randrange(0, len(stone))]


class WaterFallSubculture(RedisSubculture):
    """ water fall """
    def response(self):
        urls = [
            'http://i.gyazo.com/78984f360ddf36de883ec0488a4178cb.png',
            'http://i.gyazo.com/684523b240128b6f0eb21825e52f5c6c.png',
        ]

        if self.check_flood(self.speaker, 10) is False:
            return None

        return '\n'.join(urls)


class KimotiSubculture(RedisSubculture):

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


class KimotiYorokobiSubculture(KimotiSubculture):
    def response(self):
        if self.check_flood(self.speaker, 30) is False:
            return None
        return "https://i.gyazo.com/03c62c50700976b4486f8a80b487f7f9.jpg"


class CMDSubculture(RedisSubculture):

    def response(self):
        cmd = ['https://twitter.com/chomado/status/1164468142195662850',
               '(*ﾟ▽ﾟ* っ)З', '(((o(*ﾟ▽ﾟ*)o)))', '┌（┌ *ﾟ▽ﾟ*）┐',
               '(((o===(*ﾟ▽ﾟ*)===o)))', '┌（┌ *ﾟ▽ﾟ*）┐(*ﾟ▽ﾟ* っ)З', 'Xamarinはいいぞ',
               'https://twitter.com/loadlimits/status/1124773878872416256']

        if self.check_flood(self.speaker, 30) is False:
            return None

        random.seed()
        return cmd[random.randrange(0, len(cmd))]


class TMDSubculture(RedisSubculture):

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


class XamarinSubculture(RedisSubculture):

    def response(self):
        words = ['人脈♪', 'Xamarinはいいぞ', ]

        if self.check_flood(self.speaker, 30) is False:
            return None

        random.seed()
        return words[random.randrange(0, len(words))]


class PizzaSubculture(RedisSubculture):

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


class HitozumaSubculture(RedisSubculture):
    """ hitozuma """
    def response(self):
        random.seed()

        res = None
        if random.randrange(0, 500) < self.doge_soku():
            if random.randrange(0, 100) > 0:
                res = 'はい'
            else:
                res = 'いいえ'

        return res


class KCzumaSubculture(RedisSubculture):
    """ KCzuma """
    def response(self):
        random.seed()

        res = None
        if random.randrange(0, 2000) < self.doge_soku():
            if random.randrange(0, 100) > 0:
                res = random.choice(['K', 'K', 'Y', 'N', 'E', 'P', 'D', 'H', 'U', 'T', 'S', 'O', 'V', ]) + 'C'
            else:
                res = 'KC'
        return res
