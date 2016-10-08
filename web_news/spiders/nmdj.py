# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis


class NmdjSpider(SpiderRedis):
    name = 'nmdj'
    allowed_domains = ['nmdj.gov.cn']
    start_urls = ['http://www.nmdj.gov.cn/']
    website = u'南明党建网'

    rules = (
        Rule(LinkExtractor(allow=r'\?id=\d+$'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'\.aspx$'), follow=True),
        Rule(LinkExtractor(allow=r'\.aspx\?xid=\d+$'), follow=True),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            l.add_value('title', response.xpath('//span[contains(@id, "zt")]/text()').extract_first() or '')
            l.add_value('title', response.xpath('//span[@id="show_bt"]/descendant-or-self::text()').extract_first() or '')
            l.add_value('title', response.xpath('//span[@class="show_bt"]/descendant-or-self::text()').extract_first() or '')

            date = response.xpath('//span[contains(@id, "sj")]/text()').re_first(r'\d+-\d+-\d+')
            if date == None:
                date = response.xpath('//div[contains(@class, "show_date")]/text()').re_first(r'\d+-\d+-\d+')
            date = (date if date else '1970-01-01') + ' 00:00:00'

            l.add_value('date', date)

            l.add_value('source', self.website)

            l.add_value('content',
                        ''.join(response.xpath('//div[@id="Main1_txt"]/descendant-or-self::text()').extract()))
            l.add_value('content',
                        ''.join(response.xpath('//span[@id="Main1_txt"]/descendant-or-self::text()').extract()))

            l.add_value('content', ''.join(response.xpath('//span[@id="txt"]/descendant-or-self::text()').extract()))

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
