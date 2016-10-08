# -*- coding: utf-8 -*-
from web_news.misc.spiderredis import SpiderRedis
from scrapy.http import Request
from scrapy.selector import Selector
from web_news.items import SpiderItem
import re
import chardet
from urlparse import urljoin
import time
from scrapy.loader import ItemLoader


class XwzzbSpider(SpiderRedis):
    name = 'xwzzb'
    website = u'息烽县党建网'
    allowed_domains = ['xwzzb.cn']
    type_ids = [21, 26, 25, 28, 32, 34, 24, 27, 38, 42, 40, 43, 32]
    start_urls = ['http://www.xwzzb.cn/Type.asp?typeid=' + str(type_id) for type_id in type_ids]

    def parse(self, response):
        urls = response.xpath('//a[@class="class"]/@href').extract()
        for url in urls:
            url = 'http://www.xwzzb.cn/' + url
            yield Request(url=url, callback=self.get_news_list)

    def get_news_list(self, response):
        content_type = chardet.detect(response.body)
        if content_type['encoding'] != 'utf-8':
            html_content = response.body.decode(content_type['encoding'], 'ignore')
        selector = Selector(text=html_content)
        more = selector.xpath('//a[@class="class"]/@href')
        if more:
            url = urljoin(response.url, more.extract_first())
            yield Request(url=url, callback=self.get_news_list)
        else:
            for sel in selector.xpath('//td[@width="62%"]'):
                item = SpiderItem()
                url = urljoin(response.url, sel.xpath('a/@href').extract_first())
                if self.filter.url_exist(url):
                    return
                title = sel.xpath('a/@title').extract_first()
                item['url'] = url
                item['title'] = title
                request = Request(url=url, callback=self.get_news)
                request.meta['item'] = item
                yield request

            next_page = selector.xpath('//a[@class="black"]')
            if next_page and next_page.xpath('text()').extract_first() == u'下一页':
                next_one = next_page.xpath('@href').extract()[-1]
                yield Request(url=next_one, callback=self.get_news_list)

    def get_news(self, response):
        try:
            item = response.meta['item']
            content_type = chardet.detect(response.body)
            if content_type['encoding'] != 'utf-8':
                html_content = response.body.decode(content_type['encoding'], 'ignore')
            pattern = re.compile('align=center bgcolor="#FFFFFF">(.*?)&nbsp;', re.S)
            date = re.findall(pattern, html_content)[0]
            response = Selector(text=html_content)
            view_num = response.xpath('//font[@color="red"]/text()').extract_first()
            data = response.xpath('//td[@id="fontzoom"]')
            content = data.xpath('string(.)').extract_first().replace(u'\xa0', '')
            date = time.strptime(date.split(u'：')[1].strip(), u'%Y年%m月%d日')
            item['date'] = time.strftime('%Y-%m-%d %H:%M:%S', date)
            item['content'] = content
            item['view_num'] = view_num
            item['collection_name'] = self.name
            item['website'] = self.website
            yield item
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
            yield l.load_item()