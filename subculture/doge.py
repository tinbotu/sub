# -*- coding: utf-8 -*-

import math
import os
import random
import re
import git
from .base import Subculture, RedisSubculture, DogeAwayMessage

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
