import random
import MeCab
from .redis import HitozumaSubculture, KCzumaSubculture
from .base import Subculture


class NogataSubculture(Subculture):
    """ 姫 """

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

class SilentSubculture(Subculture):
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
        return (not self.force
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
        for line in node:
            word.append(self.divide_wordclass(line))

        for i in range(len(word)):
            do = None
            if word[i].get("word") == 'たい' and word[i].get("wordclass") == '助動詞' and word[i].get("conj1") == '特殊・タイ':
                do = self.check_backward(word, i)
                if self.check_forward(word, i):
                    continue
            if do:
                me = ['私も', '私も', '私も', 'また', '私も', ]
                return f'{random.choice(me)}{do}たいな'


class HaiSubculture(Subculture):
    """ hai """
    def response(self):
        random.seed()

        res = None
        if random.randrange(0, 100) > 40:
            res = 'はい'
        else:
            res = 'はいじゃないが'

        return res





class KCSubculture(Subculture):
    def response(self):
        random.seed()
        res = None

        ordeal = random.randrange(0, 100)
        if ordeal > 70:
            res = 'Yes, Kumagai Culture.'
        elif ordeal > 40:
            res = 'Yes, Kuzuha Culture.'
        elif ordeal > 20:
            res = 'No, Not Kumagai Culture.'
        elif ordeal < 5:
            res = 'Exactly, Kuzuha Culture.'
        return res
