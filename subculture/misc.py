# -*- coding: utf-8 -*-

import random
from .redis import METARSubculture, MineoSubculture, GaishutsuSubculture
from subculture import Subculture



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





class HateSubculture(Subculture):

    def response(self):
        random.seed()
        return '川\n' * (random.randint(0, 10) + 20)
