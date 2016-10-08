# -*- coding:utf-8 -*-
from scrapy.selector import Selector
from scrapy.spiders import Spider
from web_news.items import SpiderItem
from scrapy.http import Request, FormRequest
import re
from web_news.misc.filter import Filter
from scrapy.loader import ItemLoader


class Gyrlzyspider(Spider):
    name = "gyrlzy"
    website = u'贵阳人力资源和社会保障网'
    download_delay = 0.5
    allowed_domains = ["gzgy.lss.gov.cn"]
    start_urls = [
        "http://gzgy.lss.gov.cn/col/col262/index.html" 
    ]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Gyrlzyspider, cls).from_crawler(crawler, *args, **kwargs)
        spider.filter = Filter.from_crawler(spider.crawler, spider.name)
        return spider

    def parse(self, response):
        sel = Selector(response)
        urls = sel.xpath('//ul[@class="col-title"]/div/a/@href').extract()
        for url in urls:
            url = 'http://gzgy.lss.gov.cn'+url
            yield Request(url, callback=self.parse_url, dont_filter=True)

    def parse_url(self, response):
        sell = Selector(response)
        urlls = sell.xpath('//li[@class="col3list-mid"]/table/tr/td/table/tr/td/a/@href').extract()
        for urll in urlls:
            urll = 'http://gzgy.lss.gov.cn' + urll
            num = re.findall(r"[0-9]{3}", urll)
            number = num[0]
            cookies = {
                'cookie_url': urll}
            formdata = {
                'col': '1',
                'appid': '1',
                'webid': '1',
                'path': '/',
                'columnid': number,
                'sourceContentType': '1',
                'unitid': '1568',
                'webname': '贵阳人力资源和社会保障网',
                'permissiontype': '0'}
            urll = "http://gzgy.lss.gov.cn/module/jslib/jquery/jpage/dataproxy.jsp?startrecord=1&endrecord=600&perpage=200"
            yield FormRequest(url=urll, method="POST", formdata=formdata, cookies=cookies, meta={'dont_redirect': True, 'handle_httpstatus_list': [302]}, callback=self.parse_item)

    def parse_item(self, response):
        pattern = re.compile(".*?href='(.*?)'", re.S)
        urls = re.findall(pattern, ''.join(response.body_as_unicode()))
        for url in urls:
            url = 'http://gzgy.lss.gov.cn' + url
            if self.filter.url_exist(url):
                return
            yield Request(url, callback=self.get_news, dont_filter=True)

    def get_news(self, response):
        try:
            data = response.xpath('//div[@class="Art_left"]')
            item = SpiderItem()
            item['title'] = ''.join(data.xpath('//td[@class="title"]/text()').extract())
            #pattern=re.compile(".*?<p>",re.S)
            #item['content']=re.findall(pattern,data)
            item['content'] = ''.join(data.xpath('//div[@id="zoom"]/p/text()').extract())
            #item['date']=data.xpath('//div[@id="zoom"]/p[3]/text').extract()
            item['collection_name'] = self.name
            item['url'] = response.url
            date0 = data.xpath('//table[@id="c"]/tr[2]/td/table[1]/tr[1]/td[1]/text()').extract()
            date1 = ''.join(date0)
            item['date'] = date1[-11:-1].strip() + ' 00:00:00'
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
