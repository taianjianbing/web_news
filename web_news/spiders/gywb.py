# -*- coding: utf-8 -*-
from re import search

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader


from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis


class GywbSpider(SpiderRedis):
    name = 'gywb'
    website = u'贵阳网'
    allowed_domains = ['www.gywb.cn', 'gyfb.gywb.cn']
    start_urls = ['http://www.gywb.cn']

    rules = (
        Rule(LinkExtractor(allow=r'content_'), callback='parse_item', follow=False),
        # 匹配党政
        Rule(LinkExtractor(allow=r'/gov/'), follow=True),
       Rule(LinkExtractor(allow=r'/xinwen/'), follow=True),
       Rule(LinkExtractor(allow=r'/index_gl/'), follow=True),
       Rule(LinkExtractor(allow=r'/gynews/'), follow=True),
       Rule(LinkExtractor(allow=r'/dangshi/'), follow=True),
       Rule(LinkExtractor(allow=r'/lm_zwfb/'), follow=True),
    )

    def parse_item(self, response):
        if response.xpath('//title/text()').extract_first() == u'贵阳市党政领导每日重要工作情况':
            return
        try:
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', response.xpath('//title/text()').extract_first())
            datep = r'\d+-\d+-\d+\s+\d+:\d+:\d+'
            date = response.xpath('//span[@id="pubtime_baidu"]/descendant-or-self::text()').re(datep)
            if len(date) > 0:
                l.add_value('date', response.xpath('//span[@id="pubtime_baidu"]/descendant-or-self::text()').re(datep)[0])
                l.add_value('source', response.xpath('//span[@id="source_baidu"]/descendant-or-self::text()').extract_first())
            else:
                da = response.xpath('//div[@class="detail_more"]/text()').extract_first()
                l.add_value('date', search(datep, da[:da.find('\r\n\r\n')]).group())
                l.add_value('source', da[da.find('\r\n\r\n'):].strip())
            l.add_value('abstract', ''.join(response.xpath('//p[@class="g-content-s"]/descendant-or-self::text()').extract()))
            l.add_value('abstract', ''.join(response.xpath('//div[@class="detail_zy"]/descendant-or-self::text()').extract()))

            l.add_value('content', ''.join(response.xpath('//div[@class="g-content-c"]/descendant-or-self::text()').extract()))
            l.add_value('content', ''.join(response.xpath('//div[@class="detailcon"]/descendant-or-self::text()').extract()))
            l.add_value('content', ''.join(response.xpath('//div[@class="view_box_text"]/descendant-or-self::text()').extract()))
            l.add_value('content', ''.join(response.xpath('//div[@class="con"]/descendant-or-self::text()').extract()))
            
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            return l.load_item()
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
            return l.load_item()
