#!/usr/bin/python
# -*- coding:utf-8 -*-
from scrapy.selector import Selector
from scrapy.spider import Spider
from scrapy.loader import ItemLoader
from scrapy.http import Request, HtmlResponse
from scrapy.http import Request,FormRequest
import re
from web_news.items import *
from web_news.misc.filter import Filter
from web_news.misc.spiderredis import SpiderRedis

class HxzgSpider(SpiderRedis):
    name = 'hxzg'
    website = '花溪党建'
    download_delay = 0.2
    allowed_domains = ['119.1.109.64:8123/hxdj',
		       '119.1.109.64:8123/hxdj/showart.php',
		       '119.1.109.64:8123',
		       '119.1.109.64']
    start_urls = ['http://119.1.109.64:8123/hxdj/']

    def parse(self,response):
        item = SpiderItem()
        sel = Selector(response)
        number = 1
        while (number<1000):
            number = number+1
            headers={
                'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0",
                'Host':"119.1.109.64:8123",
                'Referer':"http://119.1.109.64:8123/hxdj/artlist.php",
            'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            'Connection':"keep-alive",
            'Cookie':"PHPSESSID=82np8d19ai7j01nur5ehqupjl3",
            'Upgrade-Insecure-Resquests':'1',
                }
            cookies={'PHPSWSSID':'82np8d19ai7j01nur5ehqupjl3'}
            formdata={'xwID':str(number)}
            url="http://119.1.109.64:8123/hxdj/showart.php"
            yield FormRequest(url=url,method="POST",formdata=formdata,cookies=cookies,meta={'dont_redirect':True,'handle_httpstatus_list':[302]},callback=self.get_news)

    def get_news(self,response):
        l = ItemLoader(item=SpiderItem(),response=response)
        l.add_value('title', response.xpath('//table/tr[3]/td[2]/text()').extract())

        l.add_value('date',response.xpath('//table/tr[4]/td/text()').extract())

        r1 = r"\d{4}\-\d{1,2}\-\d{1,2}"
        date0 = re.compile(r1)
        date = ''.join(l.get_collected_values('date'))
        date1 = date0.findall(date)
        l.replace_value('date', date1[0])
        l.add_value('content',response.xpath('//td[@class="tdbg"]/div/font/text()').extract())
        l.add_value('content',response.xpath('//td[@class="tdbg"]/p/font/text()').extract())
        l.add_value('content',response.xpath('//td[@class="tdbg"]/p/span/text()').extract())
        l.add_value('content',response.xpath('//td[@class="tdbg"]/p/text()').extract())

        l.add_value('url', response.url)
        l.add_value('collection_name', self.name)
        l.add_value('website', self.website)
        return l.load_item()
