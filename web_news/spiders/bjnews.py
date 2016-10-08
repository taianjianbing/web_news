# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from scrapy.loader import ItemLoader
from scrapy.http import Request, HtmlResponse

from web_news.items import SpiderItem
from web_news.misc.filter import Filter
from web_news.misc.spiderredis import SpiderRedis
from scrapy.shell import  inspect_response
import  re

from scrapy_redis.connection import get_redis_from_settings
import json


class BjnewsSpider(SpiderRedis):
    name = 'bjnews'
    website = u'新京报网'
    allowed_domains = ['www.bjnews.com.cn']
    start_urls = ['http://www.bjnews.com.cn/news/', 'http://www.bjnews.com.cn/news/list-43-page-1.html']

    rules = (
        Rule(LinkExtractor(allow=r'news/(\d+){4}/(\d+){2}/(\d+){2}/(\d+)'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'news/list-43-page-(\d+)'), follow=True),
        Rule(LinkExtractor(allow=r'news/?page=(\d+)'), follow=True),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            l.add_value('title', response.xpath('//title/text()').extract_first())
            datep = r'\d+-\d+-\d+\s+\d+:\d+:\d+'
            date = response.xpath('//span[@id="pubtime_baidu"]/descendant-or-self::text()').re(datep)
            if(len(date)>0):
                l.add_value('date', response.xpath('//span[@id="pubtime_baidu"]/descendant-or-self::text()').re(datep)[0])
                l.add_value('source', ''.join(response.xpath('//span[@id="source_baidu"]/descendant-or-self::text()').extract()))
            else:
                dateandsource = ''.join(response.xpath('//dl[@class="ctdate"]/descendant-or-self::text()').extract())
                if(dateandsource.strip() != ''):
                    l.add_value('date', re.search(datep, dateandsource).group())
                    source = re.sub(datep, '', dateandsource)
                    source = [s for s in source.strip()]
                    l.add_value('source', ''.join(source))
                else:
                    l.add_value('date', response.xpath('//span[@class="date"]/text()').extract_first())
                    l.add_value('source', response.xpath('//span[@class="source"]/text()').extract_first())

            l.add_value('content', ''.join(response.xpath('//div[@class="content"]/descendant-or-self::text()').extract()))
            pass
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


