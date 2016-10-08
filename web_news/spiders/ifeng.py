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
    ret = []
    for link in links:
        url = link.url
        urls = url.split('%0A')
        for l in urls:
            # 只找2010年以后的
            if re.search(r'201{5}/\d+_\d+.shtml', l) != None:

                ret.append(Link(url=l, text=link.text, fragment=link.fragment, nofollow=link.nofollow))
    return ret

class IfengSpider(SpiderRedis):
    name = 'ifeng'
    allowed_domains = ['news.ifeng.com', 'tech.ifeng.com', 'finance.ifeng.com']
    start_urls = [ 'http://www.ifeng.com/']
    website = u'凤凰网'

    rules = (
        Rule(LinkExtractor(allow=r'\d{8}/\d+_\d+.shtml'), callback='parse_item', follow=False, process_links=process_links),
        Rule(LinkExtractor(allow=r'ifeng'), follow=True),
    )

    def gettitle(self, response):
        title = ''
        title += response.xpath('//h1[@id="artical_topic"]/text()').extract_first() or ''
        title += response.xpath('//div[@class="yc_tit"]/h1/text()').extract_first() or ''

        # assert title != '', 'title is null, %s'%response.url
        if title == '':
            title += response.xpath('//title/text()').extract_first()
        return title

    def getdate(self, response):
        date = None
        t = ''
        t += response.xpath('//span[@itemprop="datePublished"]/text()').extract_first() or ''
        t += response.xpath('//div[@class="yc_tit"]/p/span/text()').extract_first() or ''
        t = t.strip()
        pa = [u'%Y年%m月%d日 %H:%M', u'%Y-%m-%d %H:%M', u'%Y-%m-%d %H:%M:%S']
        for p in pa:
            try:
                date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.mktime(time.strptime(t.strip(), p))))
            except Exception, e:
                # raise e
                pass
            else:
                break

        if date == None:
            t = re.search(r'\d{8}', response.url).group()
            date = date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.mktime(time.strptime(t.strip(), '%Y%m%d'))))
        return date

    def getcontent(self, response):
        classname = [{'name':'id',
                      'value':'main_content'},
                     {'name':'class',
                      'value':'yc_con_txt'},
                     {'name':'class',
                      'value':'wrapIphone AtxtType01'}]
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
