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


class QzdjSpider(SpiderRedis):
    name = 'qzdj'
    website = '清镇党建'
    download_delay = 0.2
    allowed_domains = ['www.gyqzdj.gov.cn']
    start_urls = ['http://www.gyqzdj.gov.cn/']

    rules = [
        Rule(LinkExtractor(allow=("www.gyqzdj.gov.cn/index.php/Home/Index/category/id/")), follow=True),
        Rule(LinkExtractor(allow=("www.gyqzdj.gov.cn/index.php/Home/Index/detail/id/")), callback='get_news', follow=True),
    ]

    def get_news(self,response):
        l = ItemLoader(item=SpiderItem(),response=response)
        l.add_value('title', response.xpath('//div[@id="lbyright_xwxq_title"]/text()').extract())
        l.add_value('date',response.xpath('//div[@id="lbyright_xwxq_xxx"]/text()').extract())
        r1 = r"\d{4}\-\d{1,2}\-\d{1,2}"
        date0 = re.compile(r1)
        date = ''.join(l.get_collected_values('date'))
        date1 = date0.findall(date)
        l.replace_value('date', date1[0])
        l.add_value('content',response.xpath('//div[@id="lbyright_xwxq_txt"]/p/span/text()').extract())
        l.add_value('url', response.url)
        l.add_value('collection_name', self.name)
        l.add_value('website', self.website)
        return l.load_item()


