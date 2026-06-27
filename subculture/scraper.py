import re
import html
from .base import HTMLParserGetElementsByTag, Subculture


class TwitterScraperSubculture(Subculture):
    pick_re = r'og\:image" content="(https://pbs.twimg.com/media/(?:.+(?:\.png|\.jpg)))'
    url_re = r"(https?://x.com/(?:[0-9A-Za-z_/.]+))[^>\s]?"

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
        if isinstance(match, list):
            return "\n".join(match)
        else:
            return None


class GyazoScraperSubculture(Subculture):
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


class TitleExtractSubculture(Subculture):
    """ <title> extract very quickhack """
    url_blacklist = ['x.com', 'gyazo.com', '.png', '.jpg', 'slack.com', ]

    def get_element_title(self, url=None):
        h = None
        prefix = ''
        postfix = ''
        re_google_photo_remove_odd_params = re.compile(r'(http.+?)=[whpk][0-9\-]')

        og_image = ['instagram.com', 'flickr.com/photos/', 'flic.kr', ]
        og_image_postfix_jpg = ['photos.google.com', 'goo.gl/photos', 'photos.app.goo.gl', ]
        og_description = ['x.com', 'facebook.com', ]
        if url is not None and any(u in url for u in og_image):
            h = HTMLParserGetElementsByTag('meta', target_meta_property='og:image')
        elif url is not None and any(u in url for u in og_image_postfix_jpg):
            h = HTMLParserGetElementsByTag('meta', target_meta_property='og:image')
            postfix = '#.jpg'
        elif url is not None and any(u in url for u in og_description):
            h = HTMLParserGetElementsByTag('meta', target_meta_property='og:description')
        else:
            prefix = 'Title: '
            h = HTMLParserGetElementsByTag('title', count=1)

        h.feed(str(self.content.decode()).replace("\n", ""))

        h.close()

        if len(h.content) > 0:
            text = html.unescape(h.content.strip())
        else:
            text = ''

        # Google Photo 用
        match = re_google_photo_remove_odd_params.search(text)
        if match and "goo" in text:
            text = match.group(1) + "=s1600"

        return f"{prefix}{text}{postfix}"

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
