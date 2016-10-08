# -*- coding: utf-8 -*-
from web_news.misc.spiderredis import SpiderRedis
from scrapy.http import FormRequest, Request
from web_news.items import SpiderItem
import time
from urlparse import urljoin
from scrapy.loader import ItemLoader


class GyxfdjSpider(SpiderRedis):
    name = 'gyxfdj'
    website = u'息烽县党建网'
    allowed_domains = ['gyxfdj.gov.cn']

    def start_requests(self):
        type_ids = list(range(3, 12))
        type_ids.extend([36, 38])
        for type_id in type_ids:
            url = 'http://gyxfdj.gov.cn/list1.aspx?id=' + str(type_id)
            yield Request(url=url, callback=self.get_news_list)

    def get_news_list(self, response):
        for sel in response.xpath('//ul[contains(@class, "main_right_box")]/li'):
            url = urljoin(response.url, sel.xpath('a/@href').extract_first())
            if self.filter.url_exist(url):
                return
            title = sel.xpath('a/@title').extract_first()
            date = sel.xpath('span/text()').extract_first()
            item = SpiderItem()
            item['url'] = url
            item['title'] = title
            date = time.strptime(date.strip(), '%Y-%m-%d %H:%M:%S')
            item['date'] = time.strftime('%Y-%m-%d %H:%M:%S', date)
            request = Request(url=url, callback=self.get_news)
            request.meta['item'] = item
            yield request

        next_page = response.xpath('//div[@id="AspNetPager1"]/a')[-2].xpath('@href')
        if next_page:
            next_one = int(response.xpath('//span[@style="margin-right:5px;font-weight:Bold;color:red;"]/text()').extract()[0]) + 1
            view_state = response.xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
            data = {
                '__EVENTTARGET': 'AspNetPager1',
                '__EVENTARGUMENT': str(next_one),
                '__VIEWSTATE': view_state
            }
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
                'Host': "gyxfdj.gov.cn",
                'Referer': response.url
            }
            yield FormRequest(url=response.url, method="POST", formdata=data, headers=headers, callback=self.get_news_list)

    def get_news(self, response):
        try:
            item = response.meta['item']
            data = response.xpath('//div[@class="content_content"]')
            content = data.xpath('string(.)').extract_first()
            item['content'] = content
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