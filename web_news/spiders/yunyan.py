# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis


class YunyanSpider(SpiderRedis):
    name = 'yunyan'
    allowed_domains = ['yunyan.gov.cn']
    start_urls = ['http://www.yunyan.gov.cn/']
    website = u'云岩区人民政府网'
    rules = (
        Rule(LinkExtractor(allow=r'content_\d+'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'index'), follow=True),
        Rule(LinkExtractor(allow=r'node_\d+'), follow=True),
    )
    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            date_source_author = response.xpath('//p[@class="new_laiy"]/span/text()').extract()
            l.add_value('title', response.xpath('//title/text()').extract_first() or '')
            l.add_value('date', date_source_author[1] if len(date_source_author)>1 else '1970-01-01 00:00:00')
            l.add_value('source', date_source_author[2] if len(date_source_author)>2 else '')
            l.add_value('content', ''.join(response.xpath('//div[@id="content"]/descendant-or-self::text()').extract()))
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
