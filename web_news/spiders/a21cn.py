# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis

class A21cnSpider(SpiderRedis):
    name = '21cn'
    allowed_domains = ['news.21cn.com']
    start_urls = ['http://news.21cn.com/']
    website = u'21CN网'

    rules = (
        Rule(LinkExtractor(allow=r'(\d){4}/(\d){4}/(\d){2}/\d+.shtml'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'domestic/'), follow=True),
        Rule(LinkExtractor(allow=r'social//'), follow=True),
    )


    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            l.add_value('title', response.xpath('//title/text()').extract_first() or '')
            l.add_value('date', response.xpath('//span[@class="pubTime"]/text()').extract_first())
            l.add_value('source', response.xpath('//a[@rel="nofollow"]/text()').extract_first())
            l.add_value('content', ''.join(response.xpath('//div[@id="article_text"]/descendant-or-self::p/text()').extract()))
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', '')
            l.add_value('date', '1970-01-01 00:00:00')
            l.add_value('source', '')
            l.add_value('content', '')
            pass
        finally:
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            return l.load_item()