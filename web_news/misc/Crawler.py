import time
from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.spiders import CrawlSpider

from web_news.misc.LogSpider import LogStatsDIY


class CrawlSpiderDIY(CrawlSpider):
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CrawlSpiderDIY, cls).from_crawler(crawler, *args, **kwargs)
        spider.crawler.signals.connect(spider.spider_idle, signal=signals.spider_idle)
        spider.l = LogStatsDIY.from_crawler(crawler)
        return spider


    def spider_idle(self):
        """Schedules a request if available, otherwise waits."""
        # XXX: Handle a sentinel to close the spider.
        # sleep somtime ?
        time.sleep(300)
        self.logger.info('restart')
        # start_requests won't be filtered
        for req in self.start_requests():
            self.crawler.engine.crawl(req, spider=self)
        raise DontCloseSpider