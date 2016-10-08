# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from web_news.misc.spiderredis import SpiderRedis
import re
from web_news.items import SpiderItem
from scrapy.loader import ItemLoader


class HuanqiuSpider(SpiderRedis):
    name = 'huanqiu'
    allowed_domains = ['china.huanqiu.com', 'society.huanqiu.com', 'finance.huanqiu.com',
                       'tech.huanqiu.com', 'smart.huanqiu.com']
    start_urls = ['http://www.huanqiu.com/']
    website = u'环球网'

    rules = (
        Rule(LinkExtractor(allow=(r'article/.*/(\d+)(_\d+){0,1}.ht',
                                  r'\d+-\d+/\d+.ht')), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'society.huanqiu.com'), follow=True),
        Rule(LinkExtractor(allow=r'china.huanqiu.com'), follow=True),
        Rule(LinkExtractor(allow=r'finance.huanqiu.com'), follow=True),

    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            if response.url == 'http://www.huanqiu.com' or re.search(r'/404.h', response.body) != None:
                raise Exception('this item may be deleted')
            if response.status != 200:
                raise Exception('response status %s'%response.status)
            l.add_value('title', response.xpath('//title/text()').extract_first() or '')
            l.add_value('date', response.xpath('//strong[@id="pubtime_baidu"]/descendant-or-self::text()').extract_first() or '1970-01-01 00:00:00')
            l.add_value('source', response.xpath('//strong[@id="source_baidu"]/descendant-or-self::text()').extract_first() or '')
            l.add_value('content', ''.join(response.xpath('//div[@class="text"]/descendant-or-self::p/text()').extract()) or '')

        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', '')
            l.add_value('date', '1970-01-01 00:00:00')
            l.add_value('source', '')
            l.add_value('content', '')
        finally:
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            return l.load_item()