#!./bin/python
# vim: ts=4 sw=4 sts=4 ff=unix ft=python expandtab

# 絡み方が悪質

import copy
import datetime
import inspect
import json
import os
import random
import re
import sys
import traceback

import emoji
import ipaddress

from urllib.parse import parse_qsl


from subculture import (
    RedisSubculture,
    DogeAwayMessage,
    KnowerLevelSubculture,
    KnowerLevelGetSubculture,
    AnotherIsMoreKnowerThanMe,
    RetirementLevelUpSubculture,
    RetirementLevelGetSubculture,
    GyazoScraperSubculture,
    TitleExtractSubculture,
    AtencionSubculture,
    DogeDetailStatusSubculture,
    SelfUpdateSubculture,
    ShowDogeSokuSubculture,
    DogeGoAwaySubculture,
    DogeHouseStatusSubculture,
    NogataSubculture,
    SilentSubculture,
    HaiSubculture,
    HitozumaSubculture,
    KCzumaSubculture,
    KCSubculture,
    OmochiSubculture,
    StoneSubculture,
    WaterFallSubculture,
    KimotiSubculture,
    KimotiYorokobiSubculture,
    CMDSubculture,
    TMDSubculture,
    XamarinSubculture,
    PizzaSubculture,
    METARSubculture,
    KotoshinoKanjiSubculture,
    MineoSubculture,
    GaishutsuSubculture,
    HateSubculture,
)



class NotSubculture:
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
        'https?://gyazo.com': GyazoScraperSubculture,
        'https?': TitleExtractSubculture,
        # 'https://x.com/': TwitterScraperSubculture,
    }

    dic_extend = {
        r'^(Ｓ|ｓ|S|s)(ｕｂ|ub)\s*((Ｃ|ｃ|C|c)(ｕｌｔｕｒｅ|ulture))?$': 'No',
        'ベンゾ': '曖昧/d',
        '(カエリンコ|かえりんこ)': 'いいですよ',
        '^(Ｔａｒｏ|Taro|太郎|Ｙａｒｏ|Yaro|野郎)$': 'No',
        r'(:?\(sun\)|おはようございます|ohayougozaimasu|起きた|おきた|ぉぁょ)$': '☀',
        r'^サ(ブ|ヴ)(カルチャー)?(なの)?(では)?(\?|？|。)*$': '?',
        r'^(\?|？)$': '?',
        r'^はい(じゃないが)?$': HaiSubculture,
        '(kumagai|ykic|kuzuha|esehara|tajima|niryuu|takano(:?32)?|usaco|voqn|tomad|yuiseki|pha|布|jal|JAL) culture': AnotherIsMoreKnowerThanMe,
        '^[KYETNOSVP1UJ]C$': AnotherIsMoreKnowerThanMe,
        r'^[KkＫｋ][CcＣｃ][\?？]$': KCSubculture,
        r'さすが\s?(kuzuha|ykic|usaco|pha|esehara|niryuu|tajima|usaco)\s?(さん)?': 'わかるなー',
        r'さすが\s?(くまがい|熊谷|kumagai|tinbotu|ｋｕｍａｇａｉ|ｔｉｎｂｏｔｕ)\s?(さん)?': '?',
        'わかるなー*$': KnowerLevelSubculture,
        r'(doge2048|[Jj][Aa][Ll]\s?(123|516)|[Mm][Hh]370)': 'なるほど',
        '(鐵|鐡)道(では)?$': 'おっ',
        '電車': '鐵道または軌道車/b',
        '戦い': '戰いでしょ/b',
        '拝承': '拝復/c',
        # 'あなた': 'あなたとJAVA, \n今すぐダウンロー\nド\nhttps://www.java.com/ja/',
        # '([^#]|^)[Cc]h?at[Ww][ao]rk': 'http://b.hatena.ne.jp/chatwark/',
        '^(おもち|OM[CT])$': OmochiSubculture,
        '^(喜び|悦び|歓び|慶び|よろこび)の(氣持ち|気持ち|きもち|KMT)$': KimotiYorokobiSubculture,
        '^(氣持ち|気持ち|きもち|KM[CT])$': KimotiSubculture,
        '^石$': StoneSubculture,
        '西山石': 'http://i.gyazo.com/ed7b4e6adaa018c4a8212c7590a98ab3.png',
        '山だ?$': 'やまいくぞ/c',
        'がんばるぞい(！|!)?$': 'http://cdn-ak.f.st-hatena.com/images/fotolife/w/watari11/20140930/20140930223157.jpg',
        'ストール$': 'はい',
        '(俺は|おれは)?もう(だめ|ダメ)だ[ー〜]*$': 'どうすればいいんだ/d',
        'どうすればいいんだ': 'おれはもうだめだ/d',
        '(は|の|とか)((きも|キモ)いの|(サブ|サヴ))(では)?$': '?',
        '^(クソ|糞|くそ)(すぎる|だな)ー?$': 'ごめん/c',
        r'^(?:(今日?|きょう)?外?(暑|寒|あつ|さむ|さみ|あち)い?(ー|のかな|？|\?)|METAR|天気)$': METARSubculture,
        '^消毒$': WaterFallSubculture,
        '^流す$': HateSubculture,
        '^他人のわかり': KnowerLevelGetSubculture,
        # '([わゎ分][\/\s\|｜　]*?[か○][\/\s\|｜　]*?[らりるっ]|なるほど|はい|お[\/\s　]*?も[/\s　]*?ち|かわいい|便利|タダメシ|[TDdS]+$|機運|老|若|おっ|ですね|サ[\/\s\|｜　]*?[ブヴ]|布|ヤバい|だる|水|コー|ムー|野方|高円寺|ルノ|サイエンス|野郎|カルチャー|左翼|あっ|ウッ|速|陣営|ゴミ|オタサー|姫|寿司|危険|HOD|椅○)': KnowerLevelUpSubculture,
        'オレオ': 'オレオ',
        r'(?:社|無職|辞め|仏教|瞑想|無常|数学|OMD|老|帰|[働動行][きい]たくな|出家|転|つま[らん][なん]|休|不景気|舟|眠|だる|熊野|親|介護|[帰か]え?り[たて]|ポキ|気.*?[なね][しー]|終わり|職|怠|引退|オワ)': RetirementLevelUpSubculture,
        '^他人の社会': RetirementLevelGetSubculture,
        'たい': SilentSubculture,
        'http': GaishutsuSubculture,
        'うひー': 'うひーとかやめてくれる',
        # '(Mac|マック|OSX|osx)': 'マックパワー/aB',
        '^弁当$': '便當だろ',
        r'\bシュッ\b': 'シュッ！シュッ！\nんっ ...',
        '(止|と)ま(ら|ん)ない(んす|んすよ)?': 'https://i.gyazo.com/e50a1e1b5dd2a5cdd5c388f654bcf8a4.gif',
        r'^((ヤバ|やば)(イ|い)|yabai)$': 'WHOOP! WHOOP! PULL UP!!!/aA',
        '.+': HitozumaSubculture,
        '..+': KCzumaSubculture,
        r'^(?!.*http).*$': NogataSubculture,  # except http
        '.*': AtencionSubculture,  # 同じキーはだめ
        r'^\(犬?(逃が?す|捕まえる)\)$': DogeGoAwaySubculture,
        r'^\(犬小屋\)$': DogeHouseStatusSubculture,
        r'^\(コラッ\)$': DogeDetailStatusSubculture,
        r'\(犬\)': ShowDogeSokuSubculture,
        r'\(犬転生\)': SelfUpdateSubculture,
        'かわいい': 'ちーちゃんかわいいね/b',
        'ナイス案件': 'http://i.gyazo.com/39111fc1ffe29ec1976696b3a95c511d.png',
        '((高野|たかの|タカノ|takano)さん|うひー)$': 'http://0x00.be/photo/takano32.jpg/dF',
        'う(ぜ[ーえ]|ざい)': 'オマエモナー/bC',
        '^[Nn][Oo]$': 'Noじゃないが/c',
        '官邸': 'http://i.gyazo.com/b8c2408c91cd49ecbe6fd9348e3bcf87.png',
        '性欲': '性欲を持て余す/cC',
        '(ネムイ|ねむい|ねみー|眠い)': 'http://i.gyazo.com/4f6e3d16fecb81f5c7b5cb371efa9074.jpg/aB',
        r'\(飼い主\)': 'tinbotu',
        'サイエンス': 'http://i.gyazo.com/154e800fd6cdb4126eece72754c033c8.jpg/bF',
        '^わかりシート$': 'https://docs.google.com/spreadsheets/d/16hNE_a8G-rehisYhPp6FppSL0ZmQSE4Por6v95fqBmA/edit#gid=0',
        '^姫乃たまシート$': 'https://docs.google.com/spreadsheets/d/1W2lwTx5ib9x_uhigFiCBN534gIcmudAQfLoJtSi6anY/edit#gid=0',
        '^NHR$': 'うへえへへえぁぁぁあぁ',
        '^TMD$': TMDSubculture,
        '^CMD$': CMDSubculture,
        '^EZ$': '説明の必要はない',
        '^Xamarin$': XamarinSubculture,
        '^(yosh?io|芳雄|よしお|ヨシオ|ヨタ)$':
        """:yos-1-1::yos-1-2::yos-1-3::yos-1-4:
:yos-2-1::yos-2-2::yos-2-3::yos-2-4:
:yos-3-1::yos-3-2::yos-3-3::yos-3-4:
:yos-4-1::yos-4-2::yos-4-3::yos-4-4:
        """,
        '^(big|BIG|Big)( |　|-)?(takano32)$':
        """:takano32-1-1::takano32-2-1::takano32-3-1::takano32-4-1:
:takano32-1-2::takano32-2-2::takano32-3-2::takano32-4-2:
:takano32-1-3::takano32-2-3::takano32-3-3::takano32-4-3:
:takano32-1-4::takano32-2-4::takano32-3-4::takano32-4-4:
        """,
        '^(今年|去年|201[0-7]年)の漢字$': KotoshinoKanjiSubculture,
        r'\(ピザ\)': PizzaSubculture,
        '^mineo$': MineoSubculture,
    }

    def __init__(self):
        self.httpheaderHasAlreadySent = False

    def httpheader(self, header="Content-Type: text/plain; charset=UTF-8\n"):
        if not self.httpheaderHasAlreadySent:
            self.httpheaderHasAlreadySent = True

    def parse_slack_outgoing_webhooks(self, http_body):
        params = dict(parse_qsl(http_body))

        # generate a *pseudo* message of Lingr
        timestamp = datetime.datetime.fromtimestamp(float(params.get("timestamp"))).isoformat()
        self.message = {
            "events": [
                {
                    "message": {
                        "id": -1,
                        "type": "user",
                        "speaker_id": str(params.get("user_name")),
                        "nickname": str(params.get("user_name")),
                        "text": str(params.get("text")),
                        "room": str(params.get("team_domain")),
                        "slack_channel": str(params.get("channel_name")),  # extra
                        "timestamp": timestamp + 'Z',
                    }
                }
            ]
        }



    def read_http_post(self, method=None, user_agent=None, http_post_body=None):
        if self.body is None and method == 'POST':
            self.body = http_post_body

            if isinstance(user_agent, str) and "Slackbot" in user_agent:
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
                    print(f"json decode error:{self.body}")
                    sys.exit(0)
        else:
            print("Status: 400 Bad request\n\n400")
            sys.exit(0)

    def acl(self, acl, ip_address):
        if not isinstance(acl, list):
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
        if isinstance(xff, str):
            remote_addr = xff.split(',')[-1].strip()
        else:
            remote_addr = os.environ.get('REMOTE_ADDR')

        if isinstance(remote_addr, str):
            return self.acl(acl, remote_addr)
        return False


    def response(self):
        if self.is_slack:
            self.httpheader(header="Content-Type: application/json; charset=UTF-8\n")
        else:
            self.httpheader()

        if os.path.exists("quiet") or not isinstance(self.message, dict):
            return

        sub = RedisSubculture()
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
        if self.message.get('events') is None and not sub.doge_is_away:
            token = sub.spontaneous(name=self.message.get('name'), key=self.message.get('key'))
            t = 15
            if isinstance(token, dict):
                try:
                    t = int(max(self.message.get('anti_double_sec'), token.get("antidouble")))
                except Exception:
                    pass
                sub.say_lingr(self.message.get('body'), self.message.get('name'), t)
                sub.say_slack(self.message.get('body'), self.message.get('name'), t)
            else:
                print("401 Unauthorized")
            return

        if self.enable_acl and not self.is_slack and not self.check_acl(sub.settings.get("hosts_allow_lingr")):
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
                                handler = dict_res(text, speaker)
                                r = handler.response()
                                if not sub.doge_is_away and r:
                                    yield r
                            elif not sub.doge_is_away:
                                # 修飾子を見て返事するか決める
                                threshold = 1.
                                prob_m = response_modifier_re.search(dict_res)
                                if prob_m:
                                    dict_res = prob_m.groups()[0]
                                    for m in list(prob_m.groups()[1]):
                                        if m not in response_modifier:
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
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

    no = NotSubculture()
    post_body = sys.stdin.read()
    no.read_http_post(method=os.environ.get('REQUEST_METHOD'), user_agent=os.environ.get('HTTP_USER_AGENT'), http_post_body=post_body)
    no.say(slack=no.is_slack, lingr=False)
