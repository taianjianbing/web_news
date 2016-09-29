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

class KydjSpider(SpiderRedis):
    name = 'kydj'
    website = '开阳党建'
    download_delay = 0.2
    allowed_domains = ['www.gzkydj.gov.cn']
    start_urls = ['http://www.gzkydj.gov.cn/Index.html']

    rules = [
        Rule(LinkExtractor(allow=("www.gzkydj.gov.cn/html"),deny=("epaper","bbs")), callback='get_news', follow=True)
    ]

    def get_news(self,response):
        l = ItemLoader(item=SpiderItem(),response=response)
        l.add_value('title', response.xpath('//div[@class="article_title"]/text()').extract())
        l.add_value('date',response.xpath('//div[@class="article_title1"]/text()').extract())
        r1 = r"\d{1,4}"
        date0 = re.compile(r1)
        date = ''.join(l.get_collected_values('date'))
        date1 = date0.findall(date)
        date1=date1[0]+'-'+date1[1]+'-'+date1[2]
        l.replace_value('date', date1)
        l.add_value('content',response.xpath('//div[@id="MyContent"]/p/span/text()').extract())
        l.add_value('content',response.xpath('//div[@id="MyContent"]/p/font/span/text()').extract())
        l.add_value('content',response.xpath('//p[@class="MsoNormal"]/span/span/font/span/text()').extract())
        l.add_value('content',response.xpath('//p[@class="MsoNormal"]/span/span/font/text()').extract())
        l.add_value('content',response.xpath('//div[@class="article_intro"]/text()').extract())
        l.add_value('content',response.xpath('//div[@id="MyContent"]/p/font/text()').extract())
        l.add_value('content',response.xpath('//p[@id="MsoNormal"]/span/text()').extract())
        l.add_value('url', response.url)
        l.add_value('collection_name', self.name)
        l.add_value('website', self.website)
        return l.load_item()
