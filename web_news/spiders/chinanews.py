# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from scrapy.linkextractor import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.misc.spiderredis import SpiderRedis
from web_news.items import SpiderItem


class Chinanews(SpiderRedis):
    name = "chinanews"
    website = u"中国新闻网"
    allowed_domain = "chinanews.com"
    start_urls = ['http://www.chinanews.com/']

    rules = [
        Rule(LinkExtractor("\d{4}/\d{2}-\d{2}/\d{7}.shtml$"), callback="get_news", follow=True),
        Rule(LinkExtractor("scroll-news", "china", "world", "society", "finance",
                           "business", "fortune", "gangao", "taiwan", "huaren",
                           "theory", "life"), follow=True)
    ]

    def get_news(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        try:
            loader.add_value("title", response.xpath('//div[@id="cont_1_1_2"]/h1[1]/text()').extract_first())
            loader.add_value("date", response.xpath('//span[@id="pubtime_baidu"]/text()').extract_first())
            loader.add_value("content",
                             ''.join(response.xpath('//div[@class="left_zw"]/descendant-or-self::text()').extract()))
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            loader.add_value('title', '')
            loader.add_value('date', '1970-01-01 00:00:00')
            loader.add_value('content', '')

        loader.add_value('url', response.url)
        loader.add_value('collection_name', self.name)
        loader.add_value('website', self.website)

        return loader.load_item()
