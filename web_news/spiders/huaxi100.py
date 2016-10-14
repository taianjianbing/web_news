# -*- coding: utf-8 -*-
import json
import re

import scrapy
from scrapy.loader import ItemLoader

from web_news.items import SpiderItem
from web_news.misc.pureSpiderredis import PureSpiderRedis


class Huaxi100Spider(PureSpiderRedis):
    name = 'huaxi100'
    allowed_domains = ['www.huaxi100.com', 'news.huaxi100.com']
    start_urls = ['http://www.huaxi100.com/util/portal_interface.php?a=getNews&page=1']
    website = u'华西都市报'

    def parse(self, response):
        data = json.loads(response.text[1:-1])
        datalist = data['data']
        flag = True
        for subdata in datalist:
            if self.filter.url_exist(subdata['url']):
                continue
            else:
                flag = False
                yield scrapy.Request(url=subdata['url'], callback=self.parse_each_news)

        if not flag and data['hasMore']:
            url = response.url
            curpage = int(re.search('page=\d+', url).group().split('=')[1])
            nexturl = re.sub('page=\d+', 'page=%s'%(curpage+1), url)
            yield scrapy.Request(url=nexturl, callback=self.parse)
    
    def parse_each_news(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            l.add_value('title', ''.join(response.xpath('//h1/text()').extract()))
            l.add_value('date', ''.join(response.xpath('//div[@class="details_info"]/text()').re('\d+.*\d+')))
            l.add_value('source', self.website)
            l.add_value('content', ''.join(response.xpath('//div[@id="summary"]/descendant-or-self::p/descendant-or-self::text()').extract()))
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