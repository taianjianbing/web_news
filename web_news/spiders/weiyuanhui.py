# -*- coding:utf-8 -*-
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.misc.spiderredis import SpiderRedis
from web_news.items import SpiderItem


class Weiyuanhui(SpiderRedis):
    name = "weiyuanhui"
    website = "尾猿会"
    allowed_domain = "weiyuanhui.net"
    start_urls = ['http://www.weiyuanhui.net/']

    rules = [
        Rule(LinkExtractor(allow=("(keji|ziran|renwen)/\d{8}/\d+.html",)), callback="get_news", follow=True),
        Rule(LinkExtractor(allow=("keji", "ziran", "renwen")), follow=True)
    ]

    def get_news(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        try:
            loader.add_value("title",
                             response.xpath('//div[@class="artz"]/h2[1]/text()').extract_first())

            loader.add_value("date", response.xpath('//p[@class="fbsj"]/text()').extract_first()[3:19] + ":00")

            loader.add_value("content", ''.join(
                response.xpath('//div[@class="artz"]/div/descendant-or-self::text()').extract()))
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            loader.add_value('title', '')
            loader.add_value('date', '1970-01-01 00:00:00')
            loader.add_value('content', '')

        loader.add_value('url', response.url)
        loader.add_value('collection_name', self.name)
        loader.add_value('website', self.website)

        return loader.load_item()
