#!/usr/bin/python
# -*- coding:utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from web_news.misc.filter import Filter
from web_news.misc.spiderredis import SpiderRedis
import time

class DfwangSpider(CrawlSpider):
    name = 'dfw'
    webname = '东方网'
    download_delay = 0.2
    allowed_domains = ['www.eastday.com',
		       'news.eastday.com',
		       'news.eastday.com',
		       'shzw.eastday.com',
		       'www.shzfzz.net']
    start_urls = ['http://www.eastday.com/']

    rules = [
	Rule(LinkExtractor(allow=("gd2008","index")),follow=True),
        Rule(LinkExtractor(allow=r'\d{7,8}',deny=("news.eastday.com/s/")), callback='get_news',follow=True),
    ]

    def get_news(self,response):
	try:
	    l = ItemLoader(item=SpiderItem(),response=response)
            l.add_value('title', response.xpath('//div[@id="biaoti"]/text()').extract())
	    l.add_value('title', response.xpath('//h1[@id="biaoti"]/text()').extract())

            l.add_value('date',response.xpath('//span[@id="pubtime_baidu"]/text()').extract())
	    l.add_value('date',response.xpath('//div[@class="center lh32 grey12a"]/text()').extract())
	    l.add_value('date',response.xpath('//div[@id="left"]/h2/text()').extract())

            l.add_value('content',response.xpath('//div[@id="zw"]/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@id="zw"]/strong/p/text()').extract())

            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
	    url = response.url
	    if url[11:17]=="shzfzz":
                date = ''.join(l.get_collected_values('date'))
                date = time.strptime(date.split()[0], u'%Y年%m月%d日')
                l.replace_value('date', time.strftime('%Y-%m-%d %H:%M:%S', date))
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
