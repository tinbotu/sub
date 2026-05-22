# -*- coding: utf-8 -*-

import random
from .base import RedisSubculture

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
