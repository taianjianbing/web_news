from scrapy.spiders import Rule
from scrapy.linkextractor import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.misc.spiderredis import SpiderRedis
from web_news.items import SpiderItem


class Guokr(SpiderRedis):
    name = "guokr"
    website = "果壳网"
    allowed_domain = "guokr.com"
    start_urls = ['http://www.guokr.com/scientific/']

    rules = [
        Rule(LinkExtractor("article"), callback="get_news", follow=True),
        Rule(LinkExtractor("scientific"), follow=True)
    ]

    def get_news(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        try:
            loader.add_value("title", response.xpath('//h1[@id="articleTitle"]/text()').extract_first())

            date = response.xpath('//div[@class="content-th-info"]/span/text()').extract_first()
            loader.add_value("date", date[-16:] + ":00")

            loader.add_value("content",
                             ''.join(response.xpath('//div[@class="document"]/descendant-or-self::text()').extract()))
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            loader.add_value('title', '')
            loader.add_value('date', '1970-01-01 00:00:00')
            loader.add_value('content', '')

        loader.add_value('url', response.url)
        loader.add_value('collection_name', self.name)
        loader.add_value('website', self.website)

        return loader.load_item()
