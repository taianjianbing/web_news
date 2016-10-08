# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from scrapy.linkextractor import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.misc.spiderredis import SpiderRedis
from web_news.items import SpiderItem


class Ynet(SpiderRedis):
    name = "ynet"
    website = "北青网"
    allowed_domain = "ynet.com"
    start_urls = ['http://www.ynet.com/']

    rules = [
        Rule(LinkExtractor("\d{4}/\d{2}/\d{8}.html$"), callback="get_news", follow=True),
        Rule(LinkExtractor("news", "politics", "world", "difang", "guancha", "theory", "dangjian"
                           "culture", "tech", "edu", ), follow=True)
    ]

    def get_news(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        try:
            loader.add_value("title", response.xpath('//div[@class="articleTitle"]/h2/text()').extract_first())
            loader.add_value("date", response.xpath('//span[@class="yearMsg"]/text()').extract_first())
            loader.add_value("source", response.xpath('//span[@class="sourceMsg"]/text()').extract_first())
            loader.add_value("content", ''.join(
                response.xpath('//div[@class="articleBox mb20 cfix"]/descendant-or-self::text()').extract()))
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            loader.add_value('title', '')
            loader.add_value("source", '')
            loader.add_value('date', '1970-01-01 00:00:00')
            loader.add_value('content', '')

        loader.add_value('url', response.url)
        loader.add_value('collection_name', self.name)
        loader.add_value('website', self.website)

        return loader.load_item()
