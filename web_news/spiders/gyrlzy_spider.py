#!/usr/bin/python
# -*- coding:utf-8 -*-
from scrapy.selector import Selector
from scrapy.spider import Spider
from web_news.items import SpiderItem
from scrapy.http import Request,FormRequest
import re
from web_news.misc.filter import Filter
class Gyrlzyspider(Spider):
    name="gyrlzy"
    download_delay=0.5
    allowed_domains=["gzgy.lss.gov.cn"]
    start_urls=[
        "http://gzgy.lss.gov.cn/col/col262/index.html" 
    ]
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Gyrlzyspider, cls).from_crawler(crawler, *args, **kwargs)
        spider.filter = Filter.from_crawler(spider.crawler, spider.name)
        return spider
    def parse(self,response):
        sel=Selector(response)
        urls=sel.xpath('//ul[@class="col-title"]/div/a/@href').extract()
        for url in urls:
            url='http://gzgy.lss.gov.cn'+url
	    yield Request(url,callback=self.parse_url,dont_filter=True)
    def parse_url(self,response):
	sell=Selector(response)
        urlls=sell.xpath('//li[@class="col3list-mid"]/table/tr/td/table/tr/td/a/@href').extract()
        for urll in urlls:
	    urll='http://gzgy.lss.gov.cn'+urll
	    print urll
	    num=re.findall(r"[0-9]{3}",urll)
	    number=num[0]
            headers={
	        'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:47.0) Gecko/20100101 Firefox/47.0",
	        'Host':"gzgy.lss.gov.cn",
	        'Referer':"urll"
            }
	    cookies={
	        'cookie_url':urll}
	    formdata={
		'col':'1',
		'appid':'1',
		'webid':'1',
		'path':'/',
		'columnid':number,
		'sourceContentType':'1',
		'unitid':'1568',
		'webname':'贵阳人力资源和社会保障网',
		'permissiontype':'0'}
	    urll="http://gzgy.lss.gov.cn/module/jslib/jquery/jpage/dataproxy.jsp?startrecord=1&endrecord=600&perpage=200"
            yield FormRequest(url=urll,method="POST",formdata=formdata,cookies=cookies,meta={'dont_redirect':True,'handle_httpstatus_list':[302]},callback=self.parse_item)
    def parse_item(self,response):
        item=SpiderItem()
        sel=Selector(response)
        sites=sel.xpath('//record')
        for site in sites:
            item=SpiderItem()
	    pattern = re.compile(".*?title='(.*?)'", re.S)
	    item['title'] = re.findall(pattern, response.body)
            pattern1=re.compile(".*?href='(.*?)'",re.S)
	    urls=re.findall(pattern1,response.body)
        for url in urls:
            url='http://gzgy.lss.gov.cn'+url
	    if self.filter.url_exist(url):
		break
            yield Request(url,callback=self.get_news,dont_filter=True)
    def get_news(self,response):
	data=response.xpath('//div[@class="Art_left"]')
	item=SpiderItem()
        item['title']=data.xpath('//td[@class="title"]/text()').extract()
	#pattern=re.compile(".*?<p>",re.S)
	#item['content']=re.findall(pattern,data)
        item['content']=data.xpath('//div[@id="zoom"]/p/text()').extract()
	item['url']=response.url
	date0=data.xpath('//table[@id="c"]/tr[2]/td/table[1]/tr[1]/td[1]/text()').extract()
	date1=('').join(date0)
	item['date']=date1[-11:-1]
        yield item

