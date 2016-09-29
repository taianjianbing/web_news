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

class WddjSpider(SpiderRedis):
    name = 'wddj'
    website = '乌当党建'
    #download_delay = 0.2
    allowed_domains = ['dj.gzwd.gov.cn']
    start_urls = ['http://dj.gzwd.gov.cn/']

    rules = [
        Rule(LinkExtractor(allow=("dj.gzwd.gov.cn/art/")), callback='get_news', follow=True),
        Rule(LinkExtractor(allow=("dj.gzwd.gov.cn/col/")), callback='get_list', follow=True),
    ]


    def get_list(self,response):
        url = response.url
        num=re.findall(r"[0-9]{4}",url)
        number=num[0]
        headers={
	        'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0",
	        'Host':"dj.gzwd.gov.cn",
	        'Referer':"url"
            }
        cookies={
	    'cookie_url':url}
        formdata={
	    'col':'1',
	    'appid':'1',
	    'webid':'30',
	    'path':'/',
	    'columnid':number,
	    'sourceContentType':'1',
	    'unitid':'16746',
	    'webname':'乌当党建网',
	    'permissiontype':'0'}
        url="http://dj.gzwd.gov.cn/module/jslib/jquery/jpage/dataproxy.jsp?startrecord=1&endrecord=3000&perpage=1000"
        yield FormRequest(url=url,method="POST",formdata=formdata,cookies=cookies,meta={'dont_redirect':True,'handle_httpstatus_list':[302]},callback=self.get_newsurl)    

    def get_news(self,response):
        l = ItemLoader(item=SpiderItem(),response=response)
        l.add_value('title', response.xpath('//td[@class="title"]/text()').extract())
        l.add_value('date',response.xpath('//table[@id="c"]/tr[3]/td/table/tr/td[1]/text()').extract())
        r1 = r"\d{4}\-\d{1,2}\-\d{1,2}"
        date0 = re.compile(r1)
        date = ''.join(l.get_collected_values('date'))
        date1 = date0.findall(date)
        l.replace_value('date', date1[0])
        l.add_value('content',response.xpath('//div[@id="zoom"]/p/text()').extract())
        l.add_value('content',response.xpath('//div[@id="zoom"]/p/span/text()').extract())
        l.add_value('content',response.xpath('//div[@id="zoom"]/p/a/text()').extract())
        l.add_value('content',response.xpath('//div[@id="zoom"]/a/text()').extract())
        l.add_value('content',response.xpath('//div[@class="detail"]/p/text()').extract())
        l.add_value('content',response.xpath('//div[@class="Section0"]/p/span/text()').extract())
        l.add_value('content',response.xpath('//div[@id="zoom"]/div/p/text()').extract())
        l.add_value('url', response.url)
        l.add_value('collection_name', self.name)
        l.add_value('website', self.website)
        return l.load_item()

    def get_newsurl(self,response):
        item=SpiderItem()
        sel=Selector(response)
        sites=sel.xpath('//record')
        for site in sites:
            pattern = re.compile(".*?href='(.*?)'",re.S)
        urls = re.findall(pattern,response.body)
        for url in urls:
            url = "http://dj.gzwd.gov.cn"+url
            yield Request(url,callback=self.get_news,dont_filter=True)
