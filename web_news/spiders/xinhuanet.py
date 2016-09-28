from scrapy.spiders import Rule
from scrapy.linkextractor import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.misc.spiderredis import SpiderRedis
from web_news.items import SpiderItem
import time


class Xinhuanet(SpiderRedis):
    name = "xinhuanet"
    website = "新华网"
    allowed_domain = "xinhuanet.com"
    start_urls = ['http://www.xinhuanet.com/']

    rules = [
        Rule(LinkExtractor(allow=("c_",),
                           deny=("ent", "fashion", "sports", "photo", "video", "caipiao", "food", "travel",
                                 "health", "vr", "uav", "forum", "sike", "auto", "leaders", "renshi")),
             callback="get_news", follow=True),
        Rule(LinkExtractor(allow=("politics", "local", "legal", "world", "mil", "talking", "fortune", "house",
                                  "comments", "info", "datanews", "yuqing", "gangao", "tw", "overseas", "education",
                                  "tech", "energy", "gongyi", "silkroad")),
             follow=True)
    ]

    def get_news(self, response):
        loader = ItemLoader(item=SpiderItem(), response=response)
        try:
            loader.add_value("title", response.xpath('//h1[@id="title"]/text()').extract_first())
            loader.add_value("title", response.xpath('//span[@id="title"]/text()').extract_first())

            loader.add_value("date", response.xpath('//span[@class="time"]/text()').extract_first())
            loader.add_value("date", response.xpath('//span[@id="pubtime"]/text()').extract_first())
            date = ''.join(loader.get_collected_values("date")).strip()
            date = time.strptime(date, '%Y年%m月%d日 %H:%M:%S')
            loader.replace_value("date", time.strftime("%Y-%m-%d %H:%M:%S", date))

            loader.add_value("content",
                             ''.join(response.xpath('//div[@id="content"]/descendant-or-self::text()').extract()))
            loader.add_value("content",
                             ''.join(response.xpath('//div[@class="article"]/descendant-or-self::text()').extract()))
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            loader.add_value('title', '')
            loader.add_value('date', '1970-01-01 00:00:00')
            loader.add_value('content', '')

        loader.add_value('url', response.url)
        loader.add_value('collection_name', self.name)
        loader.add_value('website', self.website)

        return loader.load_item()
