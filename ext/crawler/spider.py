# -*- coding: utf-8 -*-
import json
import re
import traceback
import urllib2
from gzip import GzipFile
from random import random

import datetime
import gevent
import time
import sys

from utils.db import MongoDb
from lxml import etree

from utils.item import Item

if 'threading' in sys.modules:
    del sys.modules['threading']

from StringIO import StringIO
from gevent import monkey
monkey.patch_all()

from gevent.lock import BoundedSemaphore
sem = BoundedSemaphore(10)

header = {
    # 'Host': 'roll.news.qq.com',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    'Accept': '*/*',
    'DNT': '1',
    # 'Referer': 'http://roll.news.qq.com/index.htm?site=news&mod=1&date=2016-10-12&cata=',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,gl;q=0.2',
    # 'Content-type': 'text/html; charset=utf-8',
}

urlTemplate = 'http://roll.%(site)s.qq.com/interface/roll.php?%(random)s&cata=&site=%(site)s&date=%(date)s&page=%(page)s&mode=1&of=json'
db = MongoDb(mongo_db='web_news', mongo_username='uestc', mongo_password='mongoDB',mongo_collection='news', mongo_ip=['10.2.11.231', '10.2.11.230'], mongo_port=27017)
def parse_content(html_data):
    item = Item()
    response = etree.HTML(html_data)
    item['title'] = ''.join(response.xpath('//div[@class="hd"]/h1/descendant-or-self::text()'))
    try:
        item['date'] = re.search(r'\d{4}-\d{2}-\d{2}\W\d{2}:\d{2}', ''.join(html_data)).group()+':00'
    except AttributeError as e:
        item['date'] = '1970-01-01 00:00:00'
    item['content'] = ''.join(response.xpath('//div[@id="Cnt-Main-Article-QQ"]/descendant-or-self::p/text()'))
    item['content'] = ''.join([i.strip() for i in item['content'].split()])
    item['crawl_date'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    return item

def store_item(item):
    item = dict(item)
    item['collection_name'] = 'qq'
    item['date'] = item['date'][:10] if item.get('date')!=None else ''
    ret = db.find(item)
    if ret: return ret
    db.update(item)
    return False

def fetch_each_content(request):
    try:
        del request.headers['Referer']
        del request.headers['Host']
        sem.acquire()
        # wait some time
        gevent.sleep(random()+0.5)
        try:
            response = urllib2.urlopen(request).read()
        except Exception as e:
            print traceback.format_exc()
        sem.release()
        try:
            # 居然压缩了我日
            gf = GzipFile(fileobj=StringIO(response), mode="r")
            html_data = gf.read().decode('gbk')
        except IOError as e:
            print traceback.format_exc()
            html_data = response.decode('gbk')
        # return html_data
        try:
            item = parse_content(html_data)
        except AttributeError as e:
            print traceback.format_exc()
            item = Item()
            item['url'] = request.get_full_url()
            item['website'] = u'腾讯网'
            print 'finish url: %s'%request.get_full_url()
            return store_item(item) and False

        item['url'] = request.get_full_url()
        item['website'] = u'腾讯网'
        # with open(request.get_full_url().split('/')[-1], 'w') as f:
        #     f.write(html_data.encode('utf-8'))
        print 'finish url: %s'%request.get_full_url()
        return store_item(item)
    except Exception as e:
        return  False

def fetch_each_page(request):
    response = urllib2.urlopen(request).read().decode('gbk')
    l = json.loads(response)['data']['article_info']
    urllist = re.findall(r'http://[a-z0-9\.\/]+htm', l)
    jobs = []
    for url in urllist:
        subrequest = urllib2.Request(url=url, headers=request.headers)
        jobs.append(gevent.spawn_later(0.5, fetch_each_content, subrequest))
    gevent.joinall(jobs)
    ret = []
    for j in jobs:
        ret.append(j.value)
    return ret

def main(site=None, date=None):
    d = {
        'site':site or 'finance',
        'random':random(),
        'date':date or str(datetime.date.today()),
        'page':1
    }
    request = urllib2.Request(url=urlTemplate%d, headers=header)
    request.add_header('Referer', request.get_full_url())
    request.add_header('Host', re.search(r'([a-z]+\.)+[a-z]+', request.get_full_url()).group())
    res = urllib2.urlopen(request).read().decode('gbk')
    data = None
    try:
        data = json.loads(res)['data']
    except Exception as e:
        print sys.exc_traceback()
        return
    page = 1
    jobs = []

    while page <= data['count']:
        print 'page:%d'%page
        d['page'] = page
        d['random'] = random()
        page += 1
        request = urllib2.Request(url=urlTemplate%d, headers=header)
        request.add_header('Referer', request.get_full_url())
        request.add_header('Host', re.search(r'([a-z]+\.)+[a-z]+', request.get_full_url()).group())
        jobs.append(gevent.spawn(fetch_each_page, request))
    gevent.joinall(jobs)
    ret = True
    for j in jobs:
        for i in j.value:
            ret = ret and not i
    return ret

if __name__ == '__main__':
    # assert len(sys.argv)>1, 'error: please input which site'
    # site = sys.argv[1]
    site = ['news', 'finance', 'tech']
    # 每天只爬取昨天的新闻
    date = datetime.date.today()+datetime.timedelta(-1)
    cnt = 0
    flag = True
    while  flag:
        for s in site:
            flag = flag and not main(site=s, date=str(date))
        flag = not flag
        cnt += 1
        if cnt > 180:
            break
        date = date +  datetime.timedelta(-1)
    print 'spider exit'

