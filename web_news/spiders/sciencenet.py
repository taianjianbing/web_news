# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.misc.spiderredis import SpiderRedis
from web_news.items import *
import time


class Sciencenet(SpiderRedis):
    name = 'sciencenet'
    website = '科学网'
    allowed_domains = ['sciencenet.cn']
    start_urls = ['http://www.sciencenet.cn/']

    rules = [
        Rule(LinkExtractor(allow=(
            "news.sciencenet.cn/htmlnews/",
            "blog.sciencenet.cn/blog.*?html$")), callback="get_news", follow=True),
        Rule(LinkExtractor(allow=("news.sciencenet.cn", "blog.sciencenet.cn")), follow=True),
    ]

    def get_news(self, response):
        try:
            loader = ItemLoader(item=SpiderItem(), response=response)

            loader.add_value('title', ''.join(
                response.xpath('//div[@id="content1"]/table[1]/descendant-or-self::text()').extract()))
            loader.add_value('title', ''.join(
                response.xpath('//div[@class="h pbm"]/h1/text()').extract()))

            date = ''.join(
                response.xpath('//table[@id="content"]/tr[1]/td/div[1]/descendant-or-self::text()').extract()).strip()
            if date != '':
                date = time.strptime(date[date.find(u'发布时间：') + 5:], '%Y/%m/%d %H:%M:%S')
                loader.add_value('date', time.strftime('%Y-%m-%d %H:%M:%S', date))
            else:
                date = ''.join(response.xpath('//p[@class="xg2"]/span[2]/text()').extract()).strip()
                if date != '':
                    date = time.strptime(date, '%Y-%m-%d %H:%M')
                    loader.add_value('date', time.strftime('%Y-%m-%d %H:%M:%S', date))

            loader.add_value('content', ''.join(
                response.xpath('//div[@id="content1"]/descendant-or-self::text()').extract()))
            loader.add_value('content', ''.join(
                response.xpath('//div[@id="blog_article"]/descendant-or-self::text()').extract()))

            loader.add_value('url', response.url)
            loader.add_value('collection_name', self.name)
            loader.add_value('website', self.website)

            return loader.load_item()
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
