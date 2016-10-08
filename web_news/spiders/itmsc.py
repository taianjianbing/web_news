# -*- coding: utf-8 -*-
import re

import scrapy
import time

from scrapy.link import Link
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis


def process_links(links):
    return links

class itmscSpider(SpiderRedis):
    name = 'itmsc'
    allowed_domains = ['www.itmsc.cn']
    start_urls = ['http://www.itmsc.cn/']
    website = u'科技传媒'

    rules = (
        Rule(LinkExtractor(allow=r'view-\d+-\d+.html'), callback='parse_item', follow=False, process_links=process_links),
        Rule(LinkExtractor(allow=r'list-\d+.html'), follow=True),
    )

    def gettitle(self, response):
        title = ''
        for i in response.xpath('//div[@class="cc_l"]/descendant-or-self::div[@class="arc_h1"]/descendant-or-self::text()').extract():
            title += i.strip()

        # assert title != '', 'title is null, %s'%response.url
        if title == '':
            title += response.xpath('//title/text()').extract_first()
        return title

    def getdate(self, response):
        date = None
        t = ''
        t += response.xpath('//div[@class="cc_l"]/descendant-or-self::div[@class="arc_sc"]/descendant-or-self::text()').re_first(r'\d+-\d+-\d+\W\d+:\d+')
        p = '%Y-%m-%d %H:%M'
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.mktime(time.strptime(t.strip(), p))))
        return date

    def getcontent(self, response):
        content = ''.join(response.xpath('//div[@class="cc_l"]/descendant-or-self::div[@class="arc_body"]/descendant-or-self::text()').extract())
        return content

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            for attr in ['title', 'date', 'content']:
                function = getattr(self, 'get'+attr, None)
                if function:
                    l.add_value(attr, function(response))
                else:
                    self.logger.error('no method for %s'%attr)

        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', '')
            l.add_value('date', '1970-01-01 00:00:00')
            l.add_value('source', '')
            l.add_value('content', '')
            pass
        finally:
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            return l.load_item()
