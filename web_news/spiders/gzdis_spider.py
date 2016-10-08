# -*- coding: utf-8 -*-
from web_news.misc.spiderredis import SpiderRedis
from scrapy.http import Request
from web_news.items import SpiderItem
import re
from urlparse import urljoin
from scrapy.loader import ItemLoader


class GzdisSpider(SpiderRedis):
    name = 'gzdis'
    website = u'中共贵州省纪律检查委员会、贵州省监察厅'
    allowed_domains = ['gzdis.gov.cn']
    start_urls = [
        'http://www.gzdis.gov.cn/xwzx/lzyw/',
        'http://www.gzdis.gov.cn/gzdt/xsgz/',
        'http://www.gzdis.gov.cn/xxgk/xxgknb/'
        'http://www.gzdis.gov.cn/lzjy/qlkm/'
        'http://www.gzdis.gov.cn/wlft/wqft/'
    ]

    def parse(self, response):
        script = response.xpath('//div[@class="lmdh"]/ul').extract()[0]
        pattern = re.compile('str="(.*?)"', re.S)
        urls = re.findall(pattern, ''.join(script))[0]
        for url in urls:
            url = response.url + url
            yield Request(url, callback=self.get_news_list)

    def get_news_list(self, response):
        script = response.xpath('//ul[@class="list01"]').extract_first()
        pattern = re.compile('str_1 = "(.*?)".*?str_3 = "(.*?)".*?<span>(.*?)</span>', re.S)
        results = re.findall(pattern, ''.join(script))
        for result in results:
            url = urljoin(response.url, result[0])
            if self.filter.url_exist(url):
                return
            title = result[1]
            date = result[2]
            item = SpiderItem()
            item['url'] = url
            item['title'] = title
            item['date'] = date.strip() + " 00:00:00"
            request = Request(url=url, callback=self.get_news)
            request.meta['item'] = item
            yield request

        next_page = response.xpath('//div[@class="page"]/script').extract_first()
        pattern = re.compile('createPageHTML\((.*?), (.*?),', re.S)
        result = re.findall(pattern, ''.join(next_page))[0]
        all_page = int(result[0]) - 1
        current_page = int(result[1])
        if all_page != current_page:
            url = response.url
            url = url[0:url.find('index')]
            yield Request(url=url + 'index_' + str(current_page + 1) + ".html", callback=self.get_news_list)

    def get_news(self, response):
        try:
            data = response.xpath('//div[@id="textBox"]')
            content = data.xpath('string(.)').extract_first()
            item = response.meta['item']
            item['content'] = content[0:content.find(u'分享到：')]
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