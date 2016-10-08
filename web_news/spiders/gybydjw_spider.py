# -*- coding: utf-8 -*-
from web_news.misc.spiderredis import SpiderRedis
from scrapy.http import Request
from web_news.items import SpiderItem
from scrapy.loader import ItemLoader


class GybydjwSpider(SpiderRedis):
    name = 'gybydjw'
    website = u'中共贵阳市白云区委党建网'
    allowed_domains = ['gybydjw.gov.cn']
    start_urls = ['http://www.gybydjw.gov.cn/']

    def parse(self, response):
        for sel in response.xpath('//td[@class="Baiyun1"]')[1:7]:
            url = response.url + sel.xpath('a/@href').extract_first()
            yield Request(url=url, callback=self.get_class)

    def get_class(self, response):
        urls = response.xpath('//td[@background="/Img/2_right.gif"]/a/@href').extract()
        urls.append('html/wangzhangonggao/')
        for url in urls:
            url = 'http://www.gybydjw.gov.cn/' + url
            yield Request(url=url, callback=self.get_news_list)

    def get_news_list(self, response):
        for sel in response.xpath('//li[@style="border-bottom:1px dotted #ccc; margin-top:10px; margin-bottom:20px;"]'):
            url = sel.xpath('span[1]/a/@href').extract_first()
            if self.filter.url_exist(url):
                return
            title = sel.xpath('span[1]/a/text()').extract_first()
            date = sel.xpath('span[2]/text()').extract_first()
            item = SpiderItem()
            item['url'] = url
            item['title'] = title
            item['date'] = date[1:-1].strip()
            request = Request(url=url, callback=self.get_news)
            request.meta['item'] = item
            yield request

        next_page = response.xpath('//div[@id="pages2"]/a')
        if next_page:
            next_one = 'http://www.gybydjw.gov.cn/' + next_page[-1].xpath('@href').extract_first()
            if next_one != response.url:
                yield Request(url=next_one, callback=self.get_news_list)

    def get_news(self, response):
        try:
            data = response.xpath('//div[@class="content"]')
            content = data.xpath('string(.)').extract_first()
            item = response.meta['item']
            item['content'] = content
            item['collection_name'] = self.name
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