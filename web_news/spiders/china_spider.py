#!/usr/bin/python
# -*- coding:utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from wddj.items import WddjItem
from wddj.misc.filter import Filter
from wddj.misc.spiderredis import SpiderRedis
import re
class ChwangSpider(SpiderRedis):
    name = 'chwang'
    webname = '中国'
    download_delay = 0.2
    allowed_domains = ['www.china.com.cn',
		       'news.china.com.cn',
		       'military.china.com.cn',
		       'yuqing.china.com.cn',
		       'zw.china.com.cn',
		       'cppcc.china.com.cn',
		       'opinion.china.com.cn'
    ]

    start_urls = ['http://www.china.com.cn/']

    rules = [
	Rule(LinkExtractor(allow=("node")),follow=True),
        Rule(LinkExtractor(allow=("content"),deny=("zhibo","fangtan","fuwu","txt","lianghui","aboutus","zhuanti")), callback='get_news',follow=True),
    ]

    def get_news(self,response):
        l = ItemLoader(item=WddjItem(),response=response)
        l.add_value('title', response.xpath('//div[@class="crumbs"]/h1/text()').extract())
	l.add_value('title', response.xpath('//div[@class="headBox"]/h1/text()').extract())
	l.add_value('title', response.xpath('//h1[@class="artTitle"]/text()').extract())
	l.add_value('title', response.xpath('//h1[@class="artiTitle"]/text()').extract())
	l.add_value('title', response.xpath('//h1[@class="artiTitle clearB"]/text()').extract())
	l.add_value('title', response.xpath('//h1[@class="c_title"]/text()').extract())
	l.add_value('title', response.xpath('//h1[@class="c_title"]/span/text()').extract())
	l.add_value('title', response.xpath('//td[@class="a4"]/text()').extract())
	l.add_value('title', response.xpath('//div[@class="Left"]/div/h1/text()').extract())
	l.add_value('title', response.xpath('//div[@class="wrapl"]/h1/text()').extract())
	l.add_value('title', response.xpath('//div[@class="big_img2"]/h1/text()').extract())
	l.add_value('title', response.xpath('//div[@id="contit"]/h1/text()').extract())
	l.add_value('title', response.xpath('//div[@class="headBox"]/div/h1/text()').extract())

        l.add_value('date',response.xpath('//div[@class="pub_date"]/span/text()').extract())
	l.add_value('date',response.xpath('//div[@class="artiInfo pub_date fl"]/span/text()').extract())
	l.add_value('date',response.xpath('//td[@class="a5"]/span/text()').extract())
	l.add_value('date',response.xpath('//span[@id="pubtime_baidu"]/text()').extract())
	l.add_value('date', response.xpath('//div[@class="wrapl"]/h3/text()').extract())
	l.add_value('date', response.xpath('//div[@class="more"]/text()').extract())

        r1 = r"\d{4}\-\d{1,2}\-\d{1,2}"
	date0 = re.compile(r1)
	date = ''.join(l.get_collected_values('date'))
	date1 = date0.findall(date)
        l.replace_value('date', date1[0]+" "+"00:00:00")

        l.add_value('content',response.xpath('//div[@id="articleBody"]/p/text()').extract())
	l.add_value('content',response.xpath('//div[@id="articleBody"]/p/font/text()').extract())
	l.add_value('content',response.xpath('//div[@id="artiContent"]/p/text()').extract())
	l.add_value('content',response.xpath('//div[@id="artiContent"]/p/font/text()').extract())
	l.add_value('content',response.xpath('//div[@id="c_body"]/p/text()').extract())
	l.add_value('content',response.xpath('//td[@class="a1"]/p/text()').extract())
	l.add_value('content',response.xpath('//td[@class="a1"]/p/font/text()').extract())
	l.add_value('content',response.xpath('//div[@id="artbody"]/p/span/text()').extract())
	l.add_value('content',response.xpath('//div[@id="artbody"]/p/text()').extract())
	l.add_value('content',response.xpath('//div[@class="artCon"]/p/text()').extract())
	l.add_value('content',response.xpath('//div[@class="artCon"]/text()').extract())
	l.add_value('content',response.xpath('//div[@id="box3"]/p/text()').extract())
	l.add_value('content',response.xpath('//div[@class="c_content"]/p/text()').extract())
	l.add_value('content',response.xpath('//div[@class="c_content"]/span/p/text()').extract())
	l.add_value('content',response.xpath('//div[@id="cc"]/p/text()').extract())
	l.add_value('content',response.xpath('//div[@id="content"]/p/text()').extract())
	l.add_value('content',response.xpath('//div[@id="bigpic"]/p/text()').extract())
 
        l.add_value('url', response.url)
        l.add_value('collection_name', self.name)

        return l.load_item()

