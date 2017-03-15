import time

import logging
from scrapy.extensions.logstats import LogStats
from twisted.internet import task

from web_news.pipelines import MongoDBPipeline

logger = logging.getLogger(__name__)


class LogStatsDIY(LogStats):
    @classmethod
    def from_crawler(cls, crawler):
        o = super(LogStatsDIY, cls).from_crawler(crawler)
        logger.info(o.interval)
        o.mongo = MongoDBPipeline.from_crawler(crawler)
        return o

    def spider_opened(self, spider):
        self.pagesprev = 0
        self.itemsprev = 0

        self.task = task.LoopingCall(self.log, spider)
        self.task.start(3)

    def log(self, spider):
        items = self.stats.get_value('item_scraped_count', 0)
        pages = self.stats.get_value('response_received_count', 0)
        irate = (items - self.itemsprev) * self.multiplier
        prate = (pages - self.pagesprev) * self.multiplier
        self.pagesprev, self.itemsprev = pages, items

        log_args = {'pages': pages, 'pagerate': prate,
                    'items': items, 'itemrate': irate}
        item = {}
        item['name'] = spider.name
        try:
            item['name'] = item['name'] + '%s' % getattr(spider, 'key')
        except Exception as e:
            pass
        item['active_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        item.update(log_args)
        logger.info(item)
        # logger.info(msg, log_args, extra={'spider': spider})
        self.mongo.db['LogStatsDIY'].update({'name': item['name']}, {'$set': dict(item)}, True,
                                            True)
