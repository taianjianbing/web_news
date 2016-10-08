# -*- coding:utf-8 -*-
from web_news.misc.spiderredis import SpiderRedis
from scrapy.http import Request
import json
import time
from urllib.parse import urlencode
from web_news.items import WeiboItem
import re


class SinaSpider(SpiderRedis):
    name = "weibo"
    website = "新浪微博"
    allowed_domains = ["weibo.cn"]
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
    }

    def start_requests(self):
        url = "http://m.weibo.cn/container/getIndex?containerid=106003type%3D25%26filter_type%3Drealtimehot" \
              "&title=%E5%AE%9E%E6%97%B6%E7%83%AD%E6%90%9C%E6%A6%9C&extparam=mi_cid%3D"
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
            'Host': "m.weibo.cn",
            'Referer': "http://m.weibo.cn/p/index?containerid=106003type%3D25%26filter_type%3Drealtimehot"
                       "&containerid=106003type%3D25%26filter_type%3Drealtimehot"
                       "&title=%E5%AE%9E%E6%97%B6%E7%83%AD%E6%90%9C%E6%A6%9C&extparam=mi_cid%3D"
        }
        yield Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        msg = json.loads(response.body_as_unicode())
        for data in msg['cards'][1]['card_group']:
            desc = data['desc']
            containerid = urlencode({'containerid': "100103type=&q=" + desc})
            # title = urlencode({'title': "精选-" + desc})
            # cardid = "weibo_page"
            url = "http://m.weibo.cn/container/getIndex?" + containerid + "&page=1"
            headers = {
                'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                'Host': "m.weibo.cn",
                'Referer': "http://m.weibo.cn/p/index?" + containerid
            }
            yield Request(url=url, callback=self.get_user, headers=headers)

    def get_user(self, response):
        msg = json.loads(response.body_as_unicode())
        for data in msg['cards'][-1]['card_group']:
            user_id = str(data['mblog']['user']['id'])
            url = "http://m.weibo.cn/page/json?containerid=100505" + user_id \
                  + "_-_WEIBO_SECOND_PROFILE_WEIBO&page=1"
            headers = {
                'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                'Host': "m.weibo.cn",
                'Referer': "http://m.weibo.cn/page/tpl?containerid=100505" + user_id +
                           "_-_WEIBO_SECOND_PROFILE_WEIBO&itemid=&title=%E5%85%A8%E9%83%A8%E5%BE%AE%E5%8D%9A"
            }
            yield Request(url=url, callback=self.parse_item, headers=headers)
        count = msg['cardlistInfo']['total']
        if int(count / 50) > 0:
            page_num = 5
        else:
            page_num = int((count - 1) / 10) + 1
        current_page_num = int(re.findall('page=(\d+)', response.url)[0])
        if current_page_num < page_num:
            get_user_url = re.sub('page=(\d+)', 'page=' + str(current_page_num + 1), response.url)
            yield Request(url=get_user_url, callback=self.get_user, headers=response.headers)

    def parse_item(self, response):
        msg = json.loads(response.body_as_unicode())
        for data in msg['cards'][0]['card_group']:
            item = WeiboItem()
            item["content"] = data['mblog']['text']
            item["url"] = "http://m.weibo.cn/" + str(data['mblog']['user']['id']) + '/' + data['mblog']['bid']
            item["reposts_count"] = data['mblog']['reposts_count']
            item["comments_count"] = data['mblog']['comments_count']
            item["attitudes_count"] = data['mblog']['attitudes_count']
            item["date"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['mblog']['created_timestamp']))
            item["collection_name"] = self.name
            item["website"] = self.website
            yield item
        count = msg['count']
        if int(count / 30) > 0:
            page_num = 3
        else:
            page_num = int((count - 1) / 10) + 1
        current_page_num = int(re.findall('page=(\d+)', response.url)[0])
        if current_page_num < page_num:
            url = re.sub('page=(\d+)', 'page=' + str(current_page_num + 1), response.url)
            yield Request(url=url, callback=self.parse_item, headers=response.headers)