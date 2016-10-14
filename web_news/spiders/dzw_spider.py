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
    webname = '大众网'
    download_delay = 0.2
    allowed_domains = ['www.dzwww.com',
		       'yuqing.dzwww.com']
    start_urls = ['http://www.dzwww.com/']

    rules = [
	Rule(LinkExtractor(allow=("default"),deny=("shehuixinwen")),follow=True),
        Rule(LinkExtractor(allow=r't(\d+)_(\d+)',deny=("shehuixinwen","tupian")), callback='get_news',follow=True),
    ]

    def get_news(self,response):
	try:
	    l = ItemLoader(item=SpiderItem(),response=response)
            l.add_value('title', response.xpath('//div[@class="layout"]/h2/text()').extract())
	    l.add_value('title', response.xpath('//div[@id="wrapper"]/h1/text()').extract())
	    l.add_value('title', response.xpath('//div[@class="top"]/h1/text()').extract())

            l.add_value('date',response.xpath('//div[@class="layout"]/div/text()').extract())
	    l.add_value('date',response.xpath('//div[@class="left"]/span/text()').extract())
	    l.add_value('title', response.xpath('//div[@class="top"]/p/text()').extract())

            date = ''.join(l.get_collected_values('date'))
            date = time.strptime(date.split()[0], '%Y-%m-%d')
            l.replace_value('date', time.strftime('%Y-%m-%d %H:%M:%S', date))

            l.add_value('content',response.xpath('//div[@class="news-con"]/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@id="news-con"]/div/div/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="news-con"]/div/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="news-con"]/div/div/div/font/text()').extract())
	    l.add_value('content',response.xpath('//div[@id="news-con"]/div/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@id="news-con"]/div/font/font/p/text()').extract())

            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
	    url = response.url

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
