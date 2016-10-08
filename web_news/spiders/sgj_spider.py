#!/usr/bin/python
# -*- coding:utf-8 -*-
from scrapy.selector import Selector
from scrapy.spiders import Spider
from web_news.items import SpiderItem
from scrapy.http import Request
import re
from web_news.misc.filter import Filter
from scrapy.loader import ItemLoader

class Sgjspider(Spider):
    name="sgj"
    website = u'贵州基层党建网'
    download_delay=0.5
    allowed_domains=["gzjcdj.gov.cn/sgj"]
    start_urls=[
        "http://gzjcdj.gov.cn/special/SpecialMain.jsp?en=1&spid=942&spclassid=0&iscorp=1&Search=&intPage=1" 
    ]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Sgjspider, cls).from_crawler(crawler, *args, **kwargs)
        spider.filter = Filter.from_crawler(spider.crawler, spider.name)
        return spider

    def parse(self, response):
        for url in response.xpath('//table/tr/td/table/tr[4]/td/table/tr/td/a/@href').extract():
            url = "http://gzjcdj.gov.cn/special/"+url
            if self.filter.url_exist(url):
                return
            yield Request(url, callback=self.get_news, dont_filter=True)
        urlpage = response.xpath('//span[@class="chinese"]/a/@href').extract()[-2]
        urlnext = "http://gzjcdj.gov.cn/special/" + urlpage
        pattern = re.compile('.*?intPage=(\d)', re.S)
        num = re.findall(pattern, urlpage)
        if int(num[0]) < 157:
            yield Request(urlnext, callback=self.parse, dont_filter=True)

    def get_news(self,response):
        try:
            item=SpiderItem()
            item['title'] = ''.join(response.xpath('//div[@class="STYLE67"]/text()').extract())
            item['content'] = ''.join(response.xpath('//p/text()').extract())
            item['collection_name'] = self.name
            item['url'] = response.url
            date0=response.xpath('//td[@class="style5"]/div[2]/text()').extract()
            date1=('').join(date0)
            item['date']=date1[0:10] + ' 00:00:00'
            item['website'] = self.website
            yield item
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
            yield l.load_item()
