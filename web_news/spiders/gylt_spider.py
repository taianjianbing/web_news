#!/usr/bin/python
# -*- coding:utf-8 -*-
from scrapy.selector import Selector
from scrapy.spider import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.http import Request, HtmlResponse
from scrapy.http import Request,FormRequest
import re
from web_news.items import SpiderItem
from web_news.misc.filter import Filter
from web_news.misc.spiderredis import SpiderRedis

class GyltSpider(SpiderRedis):
    name = 'gylt'
    webname = '当代党建'
    download_delay = 0.2
    allowed_domains = ['bbs.cn0851.com']
    start_urls = ['http://bbs.cn0851.com/']

    rules = [
        Rule(LinkExtractor(allow=("bbs.cn0851.com/forum")), follow=True),
        Rule(LinkExtractor(allow=("bbs.cn0851.com/thread")), callback='get_news',follow=True),
    ]

    def get_news(self,response):
	try:
            l = ItemLoader(item=SpiderItem(),response=response)
            l.add_value('title', response.xpath('//span[@id="thread_subject"]/text()').extract())

            l.add_value('date',response.xpath('//div[@class="authi"]/em/text()').extract())

            r1 = r"\d{4}\-\d{1,2}\-\d{1,2}\s\d{2}\:\d{2}"
	    date0 = re.compile(r1)
	    date = ''.join(l.get_collected_values('date'))
	    date1 = date0.findall(date)
            l.replace_value('date', date1[0])
            l.add_value('content',response.xpath('//div[@class="t_fsz"]/table/tr/td/div/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="t_fsz"]/table/tr/td/br/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="t_fsz"]/table/tr/td/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="t_fsz"]/table/tr/td/div/font/font/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="t_fsz"]/table/tr/td/font/font/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="t_fsz"]/table/tr/td/font/font/font/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="t_fsz"]/table/tr/td/p/font/font/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="t_fsz"]/table/tr/td/div/div/div/font/font/strong/text()').extract())

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
