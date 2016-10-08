# -*- coding: utf-8 -*-
from web_news.misc.spiderredis import SpiderRedis
from scrapy.http import FormRequest, Request
import json
import time
from web_news.items import SpiderItem
from scrapy.loader import ItemLoader


class NewsSpider(SpiderRedis):
    name = 'news12371'
    website = u'12371共产党员网'
    allowed_domains = ['12371.cn']
    start_urls = ['http://news.12371.cn/qwfb/']

    def parse(self, response):
        for sel in response.xpath('//div[@class="gcdywB4994_ind02"]/p'):
            url = sel.xpath('a/@href').extract()[0]
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
                'Host': "news.12371.cn",
                'Referer': url
            }
            date = time.strftime('%Y%m%d', time.localtime())
            url += 'data/' + date + '.shtml?t=' + str(int(time.time()*1000))
            yield FormRequest(url=url, headers=headers, method="GET", meta={
                'dont_redirect': True, 'handle_httpstatus_list': [302]}, callback=self.get_news_list)

    def get_news_list(self, response):
        msg = json.loads(response.body_as_unicode())['rollData']
        for result in msg:
            item = SpiderItem()
            item['url'] = result['url']
            if self.filter.url_exist(result['url']):
                return
            item['title'] = result['title']
            item['date'] = result['dateTime']
            item['brief'] = result['brief']
            request = Request(result['url'], callback=self.get_news)
            request.meta['item'] = item
            yield request

    def get_news(self, response):
        try:
            data = response.xpath('//div[@id="font_area"]')
            content = data.xpath('string(.)').extract()[0]
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