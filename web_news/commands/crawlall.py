from scrapy.commands import ScrapyCommand


class Command(ScrapyCommand):

    requires_project = True

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def run(self, args, opts):

        spider_loader = self.crawler_process.spider_loader

        for spider_name in spider_loader.list():
            print("*********crawlall spidername************" + spider_name)
            self.crawler_process.crawl(spider_name)

        self.crawler_process.start()