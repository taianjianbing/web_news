# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from scrapy.linkextractor import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.misc.spiderredis import SpiderRedis
from web_news.items import SpiderItem


class Gmw(SpiderRedis):
    name = "gmw"
    website = "光明网"
    allowed_domain = "gmw.cn"
    start_urls = ['http://www.gmw.cn/']

    rules = [
        Rule(LinkExtractor(allow=("content_",),
                           deny=("sports", "shipin", "health", "shuhua", "run", "xueshu", "e.gmw.cn",
                                 "v.gmw.cn", "gongyi", "jd", "ny", "guoxue", "history", "sixiang", "topics",
                                 "photo", "cg", "media", "meiwen", "reader", "bbs", "blog", "travel")),
             callback="get_news", follow=True),
        Rule(LinkExtractor(allow=("node_",),
                           deny=("sports", "shipin", "health", "shuhua", "run", "xueshu", "e.gmw.cn",
                                 "v.gmw.cn", "gongyi", "jd", "ny", "guoxue", "history", "sixiang", "topics",
                                 "photo", "cg", "media", "meiwen", "reader", "bbs", "blog", "travel")),
             follow=True)
    ]

    def get_news(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        try:
            loader.add_value("title", response.xpath('//h1[@id="articleTitle"]/text()').extract_first())
            loader.add_value("title", response.xpath('//div[@id="articleTitle"]/text()').extract_first())

            loader.add_value("date", response.xpath('//span[@id="pubTime"]/text()').extract_first() + ":00")
            loader.add_value("content",
                             ''.join(response.xpath('//div[@id="contentMain"]/descendant-or-self::text()').extract()))
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            loader.add_value('title', '')
            loader.add_value('date', '1970-01-01 00:00:00')
            loader.add_value('content', '')

        loader.add_value('url', response.url)
        loader.add_value('collection_name', self.name)
        loader.add_value('website', self.website)

        return loader.load_item()
