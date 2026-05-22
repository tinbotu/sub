# -*- coding: utf-8 -*-

from .base import RedisSubculture

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
