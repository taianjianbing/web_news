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

class SouthcnSpider(SpiderRedis):
    name = 'southcn'
    allowed_domains = ['news.southcn.com', 'opinion.southcn.com', 'energy.southcn.com',
                       'economy.southcn.com', 'kb.southcn.com', 'it.southcn.com',
                       'finance.southcn.com', 'house.southcn.com', 'law.southcn.com','tech.southcn.com',
                       ]
    start_urls = ['http://www.southcn.com/', ]
    website = u'南方网'

    rules = (
        Rule(LinkExtractor(allow=r'201\d-\d+/\d+/content_\d+.htm'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'southcn'), follow=True),
    )
    def gettitle(self, response):
        title = ''
        for i in response.xpath('//h2[@id="article_title"]/descendant-or-self::text()').extract():
            title += i.strip()

        # assert title != '', 'title is null, %s'%response.url
        if title == '':
            title += response.xpath('//title/text()').extract_first()
        return title

    def getdate(self, response):
        date = None
        t = ''
        t += response.xpath('//span[@id="pubtime_baidu"]/descendant-or-self::text()').re_first(r'\d+-\d+-\d+\W\d+:\d+') or '1970-01-01 00:00'
        p = '%Y-%m-%d %H:%M'
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.mktime(time.strptime(t.strip(), p))))
        return date

    def getcontent(self, response):
        content = ''.join(response.xpath('//div[@class="content"]/descendant-or-self::text()').extract())
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
