# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider
from scrapy.http import Request, HtmlResponse
from filter import Filter
from scrapy_redis.connection import get_redis_from_settings
import json

class SpiderRedis(CrawlSpider):

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
        spider = super(SpiderRedis, cls).from_crawler(crawler, *args, **kwargs)
        spider.filter = Filter.from_crawler(spider.crawler, spider.name)
        spider.compete_key()
        return spider


    def _requests_to_follow(self, response):
        links = self.filter.bool_fllow(response, self.rules)
        if len(links) > 0:
            for link in links:
                r = Request(url=link.url, callback=self._response_downloaded)
                r.meta.update(rule=0, link_text=link.text)
                yield self.rules[0].process_request(r)
            if not isinstance(response, HtmlResponse):
                return
            seen = set()
            for n, rule in enumerate(self._rules):
                if n == 0:
                    continue
                links = [lnk for lnk in rule.link_extractor.extract_links(response)
                         if lnk not in seen]
                if links and rule.process_links:
                    links = rule.process_links(links)
                for link in links:
                    seen.add(link)
                    r = Request(url=link.url, callback=self._response_downloaded)
                    r.meta.update(rule=n, link_text=link.text)
                    yield rule.process_request(r)
        else:
            return


