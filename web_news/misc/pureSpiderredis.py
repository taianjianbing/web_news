# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Spider
from scrapy.http import Request, HtmlResponse
from filter import Filter
from scrapy_redis.connection import get_redis_from_settings
import json

class PureSpiderRedis(Spider):
    """
    this class is to clear redis dupefilter key, when exit correctly.
    if the spider exit with two INT singal, you may need to clear the key manually.
    """

    def compete_key(self):
        self.server = get_redis_from_settings(self.settings)
        self.redis_compete = self.settings.get('REDIS_COMPETE') % {'spider': self.name}
        self.redis_wait = self.settings.get('REDIS_WAIT') % {'spider': self.name}
        self.key = 1
        # self.server.sadd(self.key, fp)
        while self.server.sadd(self.redis_compete, self.key) == 0:
            self.key = self.key + 1
        self.logger.info("get key %s" % self.key)

    @staticmethod
    def close(spider, reason):
        # before close spider
        spider.server.lpush(spider.redis_wait, json.dumps(spider.key))
        cnt = spider.server.scard(spider.redis_compete)
        if spider.key == 1:
            t = 0
            while t < cnt:
                spider.logger.info("wait %s spiders to stop" % (cnt-t))
                spider.server.brpop(spider.redis_wait, 0)
                t = t + 1
                cnt = spider.server.scard(spider.redis_compete)
            spider.logger.info("all slave spider exit")
            spider.server.delete(spider.redis_compete)
            spider.server.delete(spider.redis_wait)
            spider.server.delete('%(spider)s:dupefilter' % {'spider': spider.name})

            # super(BjnewsSpider, reason).close()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(PureSpiderRedis, cls).from_crawler(crawler, *args, **kwargs)
        spider.filter = Filter.from_crawler(spider.crawler, spider.name)
        spider.compete_key()
        return spider

