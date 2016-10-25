# -*- coding: utf-8 -*-
import re

import scrapy
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis

def function(links):
    ret = []
    allow=('society', 'tech', 'finance')
    deny=('pic', '/tp/')
    for link in links:
        flag = False
        for a in allow:
            if link.url.find(a)!=-1:
                flag = True
                break
        if not flag:continue
        flag = True
        for d in deny:
            if link.url.find(d)!=-1:
                flag = False
                break
        if not flag:continue
        ret.append(link)
    return  ret

class K618Spider(SpiderRedis):
    name = 'k618'
    allowed_domains = ['news.k618.cn']
    start_urls = ['http://news.k618.cn/']
    website = u'未来网'
    custom_settings = {
        'CLOSESPIDER_TIMEOUT':3600,
    }
    rules = (
        Rule(LinkExtractor(allow=r't\d+_\d+'), callback='parse_item', follow=False, process_links=function),
        Rule(LinkExtractor(allow=('society', 'tech', 'finance')), follow=True),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            l.add_value('title', ''.join(response.xpath('//h1/text()').extract()))
            l.add_value('date', ''.join(response.xpath('//div[@class="news_time_source"]/text()').re('\d+-\d+-\d+\W\d+:\d+:\d+')))
            l.add_value('source', self.website)
            l.add_value('content', ''.join(response.xpath('//div[@class="news_main"]/descendant-or-self::text()').extract()))
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
