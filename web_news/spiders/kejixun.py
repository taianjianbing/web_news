# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis

def function(links):
    for link in links:
        if link.url.find('m.kejixun.com') != -1:continue
        yield link

class KejixunSpider(SpiderRedis):
    name = 'kejixun'
    allowed_domains = ['kejixun.com']
    start_urls = ['http://www.kejixun.com/']
    website = u'科技讯'

    rules = (
        Rule(LinkExtractor(allow=r'article/\d+/\d+'), callback='parse_item', follow=False, process_links=function),
        Rule(LinkExtractor(allow=r'kejixun'), follow=True),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            l.add_value('title', response.xpath('//title/text()').extract_first() or '')
            l.add_value('date', response.xpath('//div[@class="titleInfo"]/span[1]/text()').extract_first() or '')
            l.add_value('source', self.website)
            classname = ['artibody']
            content = ''
            for c in classname:
                content += ''.join(response.xpath('//div[@id="%s"]/descendant-or-self::text()'%c).extract())
            # if content == None or content.strip() == '':
            #     self.logger.info(response.url)
            l.add_value('content', content)
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