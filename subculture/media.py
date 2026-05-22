# -*- coding: utf-8 -*-

import random
from .base import RedisSubculture

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
