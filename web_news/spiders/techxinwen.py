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
    ret = []
    for link in links:
        url = link.url
        urls = url.split('%0A')
        for l in urls:
            # 只找2010年以后的
            if re.search(r'201{5}/\d+_\d+.shtml', l) != None:

                ret.append(Link(url=l, text=link.text, fragment=link.fragment, nofollow=link.nofollow))
    return ret

class TechxinwenSpider(SpiderRedis):
    name = 'techxinwen'
    allowed_domains = ['www.techxinwen.com']
    start_urls = ['http://www.techxinwen.com/']
    website = u'科技资讯'

    rules = (
        Rule(LinkExtractor(allow=r'show-\d+-\d+-\d+.html'), callback='parse_item', follow=False, process_links=process_links),
        Rule(LinkExtractor(allow=r'list-\d+-\d+.html'), follow=True),
    )

    def gettitle(self, response):
        title = ''
        for i in response.xpath('//div[@class="viewbox"]/descendant-or-self::div[@class="title"]/descendant-or-self::text()').extract():
            title += i.strip()

        # assert title != '', 'title is null, %s'%response.url
        if title == '':
            title += response.xpath('//title/text()').extract_first()
        return title

    def getdate(self, response):
        date = None
        t = ''
        t += response.xpath('//div[@class="info"]/text()').re_first(r'\d+-\d+-\d+\W\d+:\d+:\d+') or ''
        return t

    def getcontent(self, response):
        classname = [{'name':'id',
                      'value':'content'}]
        content = ''
        for c in classname:
            content += ''.join(response.xpath('//div[@%(name)s="%(value)s"]/descendant-or-self::text()'%c).extract())

        # assert content != '', 'content is null, %s'%response.url
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
