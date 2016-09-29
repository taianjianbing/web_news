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

class GogSpider(SpiderRedis):
    name = 'gog'
    website = '多彩贵州网'
    download_delay = 0.2
    allowed_domains = ['www.gog.cn',
		       'news.gog.cn',
		       'sc.gog.cn',
		       'gngj.gog.cn',
		       'zt.gog.cn',
	 	       'sc.gog.cn',
		       'comment.gog.cn',
		       'finance.gog.cn',
		       'dfp.gog.cn'
    ]
    start_urls = ['http://www.gog.cn/']

    rules = [
        Rule(LinkExtractor(allow=("shtml",),deny=("index",)), callback="get_news", follow=True),
        Rule(
            LinkExtractor(allow=("news.gog.cn/",
                                 "sc.gog.cn/",
                                 "gngj.gog.cn/",
				 "zt.gog.cn/",
				 "sc.gog.cn/",
				 "comment.gog.cn/",
				 "finance.gog.cn/",
				 "dfp.gog.cn",),deny=("system",)), follow=True),
    ]

    def get_news(self,response):
        l = ItemLoader(item=SpiderItem(),response=response)
        l.add_value('title', response.xpath('//h1[@class="title"]/text()').extract())
        l.add_value('title', response.xpath('//span[@class="articletitle_p22"]/text()').extract())
        l.add_value('title', response.xpath('//h1[@class="tit_h2"]/text()').extract())
        l.add_value('title', response.xpath('//span[@class="gog_title"]/text()').extract())
        l.add_value('title', response.xpath('//td[@class="gog_title"]/text()').extract())

        l.add_value('date',response.xpath('//div[@class="info"]/text()').extract())
        l.add_value('date',response.xpath('//span[@class="p12 LightGray2"]/text()').extract())
        l.add_value('date',response.xpath('//div[@class="articletime"]/text()').extract())
        l.add_value('date',response.xpath('//body/table[5]/tr[5]/td[2]/div/text()').extract())
        l.add_value('date',response.xpath('//body/table[6]/tr/td/table/tr/td/table[3]/tr/td/text()').extract())
        r1 = r"\d{4}.\d{1,2}.\d{1,2}"
        date0 = re.compile(r1)
        date = ''.join(l.get_collected_values('date'))
        date1 = date0.findall(date)
        l.replace_value('date', date1[0])
        l.add_value('content',response.xpath('//div[@class="content"]/p/text()').extract())
        l.add_value('content',response.xpath('//td[@class="p16"]/p/text()').extract())
        l.add_value('content',response.xpath('//div[@class="content01 p16"]/p/text()').extract())
        l.add_value('content',response.xpath('//div[@class="content"]/div/p/text()').extract())
        l.add_value('content',response.xpath('//span[@class="gog_content"]/p/text()').extract())
        l.add_value('content',response.xpath('//div[@class="content"]/p/a/text()').extract())
        l.add_value('content',response.xpath('//td[@class="gog_content"]/p/text()').extract())
        l.add_value('content',response.xpath('//td[@class="gog_content"]/font/p/text()').extract())
        l.add_value('content',response.xpath('//td[@class="p16"]/div/p/text()').extract())

        l.add_value('url', response.url)
        l.add_value('collection_name', self.name)
        l.add_value('website', self.website)
        return l.load_item()
