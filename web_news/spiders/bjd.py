# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from web_news.misc.spiderredis import SpiderRedis
from web_news.items import SpiderItem
from scrapy.loader import ItemLoader

class BjdSpider(SpiderRedis):
    name = 'bjd'
    allowed_domains = ['www.bjd.com.cn']
    start_urls = ['http://www.bjd.com.cn/']
    website = u'京报网'

    rules = (
        Rule(LinkExtractor(allow=r't(\d+)_(\d+)'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'bjd.com.cn'), follow=True),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            date_source_author = response.xpath('//div[@class="info"]/span/text()').extract()
            l.add_value('title', response.xpath('//title/text()').extract_first() or '')
            l.add_value('date', date_source_author[0] if len(date_source_author)>0 else '1970-01-01 00:00:00')
            l.add_value('source', date_source_author[1] if len(date_source_author)>1 else '')
            l.add_value('content', ''.join(response.xpath('//div[@class="TRS_Editor"]/descendant-or-self::text()').extract()))
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