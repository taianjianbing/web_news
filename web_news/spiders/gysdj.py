# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis


class GysdjSpider(SpiderRedis):
    name = 'gysdj'
    allowed_domains = ['www.gysdj.gov.cn']
    start_urls = ['http://www.gysdj.gov.cn/']
    website = r'贵阳党建网'

    rules = (
        Rule(LinkExtractor(allow=r'/(\d+).shtml'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'index'), follow=True),

    )
    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            l.add_value('title', response.xpath('//title/text()').extract_first())
            date = response.xpath('//td[@align="center"]/text()').re(u'\d+年\d+月\d+日')[0]
            date = date.replace(u'年', '-').replace(u'月', '-').replace(u'日', ' ') + '00:00:00'
            l.add_value('date', date)
            l.add_value('source', self.website)
            l.add_value('content', ''.join(response.xpath('//td[@style="line-height: 30px;font-size:16px; padding-top:10px;"]/descendant-or-self::text()').extract()))
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
