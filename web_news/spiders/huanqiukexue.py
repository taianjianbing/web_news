# -*- coding: utf-8 -*-

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.misc.spiderredis import SpiderRedis
from web_news.items import SpiderItem
import time


class Huanqiukexue(SpiderRedis):
    name = "huanqiukexue"
    website = "环球科学网"
    allowed_domain = "huanqiukexue.com"
    start_urls = ['http://www.huanqiukexue.com/']

    rules = [
        Rule(LinkExtractor(allow=("/plus/view", "qianyan.*?html$", "guandian.*?html$")), callback="get_news", follow=True),
        Rule(LinkExtractor(allow=("list.php?tid=1", "list.php?tid=2")), follow=True)
    ]

    def get_news(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        try:
            loader.add_value("title",
                             response.xpath('//div[@class="astrLeft leftFloat details"]/h2[1]/text()').extract_first())
            loader.add_value("title",
                             response.xpath('//div[@class="astrLeft leftFloat details interviewcon"]/h2[1]/text()').extract_first())

            date = time.strptime(response.xpath('//span[@class="date"]/text()').extract_first(), '%Y年%m月%d日')
            loader.add_value("date", time.strftime("%Y-%m-%d %H:%M:%S", date))

            loader.add_value("content", ''.join(
                response.xpath('//div[@class="astrLeft leftFloat details"]/descendant-or-self::text()').extract()))
            loader.add_value("content", ''.join(
                response.xpath('//div[@class="astrLeft leftFloat details interviewcon"]/descendant-or-self::text()').extract()))
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            loader.add_value('title', '')
            loader.add_value('date', '1970-01-01 00:00:00')
            loader.add_value('content', '')

        loader.add_value('url', response.url)
        loader.add_value('collection_name', self.name)
        loader.add_value('website', self.website)

        return loader.load_item()
