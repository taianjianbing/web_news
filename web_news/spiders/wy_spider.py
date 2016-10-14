#!/usr/bin/python
# -*- coding:utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import SpiderItem
from web_news.misc.filter import Filter
from web_news.misc.spiderredis import SpiderRedis
import time

class Wy163Spider(CrawlSpider):
    name = 'wy163'
    webname = '网易'
    download_delay = 0.2
    allowed_domains = ['www.163.com',
		       'news.163.com',
		       'money.163.com',
		       'gov.163.com',
		       'war.163.com']
    start_urls = ['http://www.163.com/']

    rules = [
	Rule(LinkExtractor(allow=("special")),follow=True),
        Rule(LinkExtractor(allow=r'\d{4}\/\d{2}',deny=('photo',"keywords","caozhi","quotes")), callback='get_news',follow=True),
    ]

    def get_news(self,response):
	try:
	    l = ItemLoader(item=SpiderItem(),response=response)
            l.add_value('title', response.xpath('//div[@class="post_content_main"]/h1/text()').extract())
	    l.add_value('title', response.xpath('//div[@class="endContent"]/h1/text()').extract())
	    l.add_value('title', response.xpath('//div[@class="theTitle"]/h1/text()').extract())
	    l.add_value('title', response.xpath('//div[@class="ep-main-bg"]/h1/text()').extract())
	    l.add_value('title', response.xpath('//div[@class="ep-content-main"]/h1/text()').extract())
	    l.add_value('title', response.xpath('//div[@class="endContent bg_endPage_Lblue"]/h1/text()').extract())

            l.add_value('date',response.xpath('//div[@class="post_time_source"]/text()').extract())
	    l.add_value('date',response.xpath('//span[@class="info"]/text()').extract())
	    l.add_value('date',response.xpath('//div[@class="text"]/text()').extract())
	    l.add_value('date',response.xpath('//div[@class="ep-time-soure cDGray"]/text()').extract())

            date = ''.join(l.get_collected_values('date'))
            date = time.strptime(date.split()[0], u'%Y-%m-%d')
            l.replace_value('date', time.strftime('%Y-%m-%d %H:%M:%S', date))

            l.add_value('content',response.xpath('//div[@class="post_text"]/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="endText"]/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="endText"]/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="end-text"]/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@class="end-text"]/div/text()').extract())
	    l.add_value('content',response.xpath('//div[@id="content"]/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@id="endText"]/p/text()').extract())
	    l.add_value('content',response.xpath('//div[@id="endText"]/div/p/text()').extract())
 
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
