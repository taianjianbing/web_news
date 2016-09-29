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
from web_news.items import *
from web_news.misc.filter import Filter
from web_news.misc.spiderredis import SpiderRedis
import time

class JydjSpider(SpiderRedis):
    name = 'jydj'
    website = '观山湖党建'
    download_delay = 0.2
    allowed_domains = ['www.gyjydj.gov.cn']
    start_urls = ['http://www.gyjydj.gov.cn/']

    rules = [
        Rule(LinkExtractor(allow=("NewsID")), callback='get_news', follow=True),
        Rule(LinkExtractor(allow=("ClassID")), follow=True),
    ]

    def get_news(self,response):
        l = ItemLoader(item=SpiderItem(),response=response)
        l.add_value('title', response.xpath('//form[@id="Form1"]/table/tr/td/table/tr[2]/td/table/tr[2]/td/table/tr/td/table/tr/td/strong/font/text()').extract())
        l.add_value('date',response.xpath('//form[@id="Form1"]/table/tr/td/table/tr[2]/td/table/tr[2]/td/table/tr[3]/td/font/font[1]/text()').extract())
        #date = ''.join(l.get_collected_values('date'))
        #date = time.strptime(date.split()[0], '%Y年%m月%d日%H:%M')
        #l.replace_value('date', time.strftime('%Y-%m-%d %H:%M:%S', date))
        l.add_value('content',response.xpath('//form[@id="Form1"]/table/tr/td/table/tr[2]/td/table/tr[2]/td/table/tr[5]/td/p/span/text()').extract())
        l.add_value('content',response.xpath('//table[@class="p14"]/tr[5]/td/p/text()').extract())
        l.add_value('url', response.url)
        l.add_value('collection_name', self.name)
        l.add_value('website', self.website)
        return l.load_item()
