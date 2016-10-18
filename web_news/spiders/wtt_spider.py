#!/usr/bin/python
# -*- coding:utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from web_news.misc.filter import Filter
from web_news.misc.spiderredis import SpiderRedis
import time
class WttSpider(SpiderRedis):
    name = 'wtt'
    webname = '微头条'
    download_delay = 0.2
    allowed_domains = ['www.wtoutiao.com']
    start_urls = ['http://www.wtoutiao.com/']

    rules = [
	Rule(LinkExtractor(allow=("tech","values")),follow=True),
        Rule(LinkExtractor(allow=("/p/"),deny=('ent',"sports","lady","design")), callback='get_news',follow=True),
    ]

    def get_news(self,response):
	try:
            l = ItemLoader(item=SpiderItem(),response=response)
            l.add_value('title', response.xpath('//div[@class="article_header"]/h1/text()').extract())

            l.add_value('date',response.xpath('//div[@class="article_header"]/p[2]/text()').extract())

            date = ''.join(l.get_collected_values('date'))
            #date = time.strptime(date.split()[0], u'%Y-%m-%d')
            #l.replace_value('date', time.strftime('%Y-%m-%d %H:%M:%S', date))

            l.add_value('content',response.xpath('//div[@class="article_view"]/p/span/span/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="article_view"]/p/span/strong/span/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="article_view"]/p/text()').extract())
 
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            return l.load_item()
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', '')
            l.add_value('date', '1970-01-01 00:00:00')
            l.add_value('source', '')
            l.add_value('content', '')
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            return l.load_item()
