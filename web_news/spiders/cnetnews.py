# -*- coding: utf-8 -*-
import re

import scrapy
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis


class CnetnewsSpider(SpiderRedis):
    name = 'cnetnews'
    allowed_domains = ['cnetnews.com.cn']
    start_urls = ['http://www.cnetnews.com.cn/']
    website = u'CNET科技资讯网'

    rules = (
        # 只要2010年以后的
        Rule(LinkExtractor(allow=r'201\d+/\d+'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'list'), follow=True),

    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            l.add_value('title', response.xpath('//title/text()').extract_first())
            date = re.search(r'\d{4}/\d{4}', response.url).group()
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.mktime(time.strptime(date, '%Y/%m%d'))))
            l.add_value('date', date)
            l.add_value('source', 'CNET科技资讯网')
            classname = ['qu_content_div', 'qu_ocn', 'qu_wenzhang_con_div', 'text1', 'bin_pic']
            content = ''
            for c in classname:
                content += ''.join(response.xpath('//div[@class="%s"]/descendant-or-self::text()'%c).extract())
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
