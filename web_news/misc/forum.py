# -*- coding: utf-8 -*-
import json

from scrapy import Item
from scrapy import Request
from scrapy import Spider
from scrapy_redis import get_redis_from_settings

from web_news.misc.filter import Filter

class SpiderForum(Spider):

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
        spider = super(SpiderForum, cls).from_crawler(crawler, *args, **kwargs)
        spider.filter = Filter.from_crawler(spider.crawler, spider.name)
        spider.compete_key()
        return spider

    def parse(self, response):
        return self._parse_each_node(response=response)

    def _parse_each_node(self, response):
        requests_it = [i.replace(callback=self._parse_each_item) for i in self.parse_each_node(response)]
        np = self.next_page(response)
        requests_it[-1].meta['nextpage'] = np
        for i in requests_it:
            yield i

    def _parse_each_item(self, response):
        it = self.parse_each_item(response)
        if it==None: return
        # it may be item or request
        ret = []
        if isinstance(it, Item):
            it = dict(it)
            if response.meta.get('nextpage') and \
                    it.get('last_reply') and \
                    not self.filter.link_lastupdate(it['url'], it['last_reply']):
                np = response.meta.get('nextpage')
                ret.append(np.replace(callback=self._parse_each_node))
        else:
            if response.meta.get('nextpage'):
                it.meta['nextpage'] = response.meta.get('nextpage')
            it = it.replace(callback=self._parse_each_item)
        ret.append(it)
        return ret

    def parse_each_node(self, response):
        """
        :param response:
        :return: requests list
        """
        raise  NotImplementedError

    def parse_each_item(self, response):
        """
        :param response:
        :return: (item, response) list
        """
        raise  NotImplementedError

    def next_page(self, response):
        """
        :param response:
        :return: request to next page
        """
        raise NotImplementedError