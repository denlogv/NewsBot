import datetime
import logging
from dataclasses import dataclass
from typing import List

import dateparser
import lxml.etree
import requests
from lxml.etree import _Element
from requests import HTTPError

DEFAULT_RSS_FEED_URL = 'https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml'


class UrlReader:
    def read_url(self, url: str):
        if url is None:
            logging.error('Provided URL is None')
            return None

        response = requests.get(url)
        content = None
        try:
            response.raise_for_status()
            content = response.content
        except HTTPError as e:
            logging.error('The URL appears to be broken, cannot retrieve data from it!')

        return content


@dataclass
class News(UrlReader):
    title: str = None
    link: str = None
    description: str = None
    date: datetime.datetime = None
    news_id: int = None

    def __post_init__(self):
        self.news_id = hash((self.description, self.date))

    def __hash__(self):
        return self.news_id

    def __eq__(self, other):
        return other and isinstance(other, News) \
            and self.news_id == other.news_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return f'{self.description}\n\n{self.link}'

    def get_full_text(self):
        # content_bytes = self.read_url(url=self.link)
        # if content_bytes is None:
        #     logging.error('Could not get the news full text version')
        #     return None
        # pass
        raise NotImplementedError('Getting news full text is not yet implemented!')


class TagesschauFeedReader(UrlReader):
    def __init__(self, rss_feed_url: str = DEFAULT_RSS_FEED_URL):
        self.rss_feed_url = rss_feed_url

    def get_news(self) -> list[News] | None:
        content_bytes = self.read_url(url=self.rss_feed_url)
        if content_bytes is None:
            return None

        content_root: _Element = lxml.etree.fromstring(content_bytes)
        channels: List[_Element] = content_root.getchildren()
        news_objects = [
            self._get_news_from_item(item=item)
            for channel in channels
            for item in channel.findall('item')
        ]

        return news_objects

    def _get_news_from_item(self, item):
        return News(
            title=getattr(item.find('title'), 'text', None),
            link=getattr(item.find('link'), 'text', None),
            description=getattr(item.find('description'), 'text', None),
            date=dateparser.parse(getattr(item.find('pubDate'), 'text', None))
        )


if __name__ == '__main__':
    feed_reader = TagesschauFeedReader()
    for news in feed_reader.get_news():
        print(news, end='\n\n')
