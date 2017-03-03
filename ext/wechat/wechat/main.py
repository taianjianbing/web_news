import json
import re

import datetime
from lxml import etree

import requests
import HTMLParser

import time
from db import MongoDb
from pymongo import MongoClient
from hashlib import md5

db = MongoDb(mongo_db='web_news', mongo_username='', mongo_password='', mongo_collection='news',
             mongo_ip=['10.2.11.231', '10.2.11.230'], mongo_port=27017)


def parse_content(html_data):
    item = {}
    response = etree.HTML(html_data)
    try:
        item['title'] = ''.join(response.xpath('//h2[@class="rich_media_title"]/text()')[0].split())
    except Exception as e:
        item['title'] = ''
    item['content'] = ''.join(
        [''.join(i.split()) for i in response.xpath('//div[@class="rich_media_content "]/descendant-or-self::text()')])
    item['wechatno'] = ''.join(response.xpath(
        '//a[@class="rich_media_meta rich_media_meta_link rich_media_meta_nickname"]/descendant-or-self::text()'))
    return item


def html2dict(str):
    html_parser = HTMLParser.HTMLParser()
    txt = html_parser.unescape(str)
    return txt


def store_item(item):
    item = dict(item)
    item['collection_name'] = 'wechat'
    item['website'] = 'mp.weixin.qq.com'
    item['md5'] = md5((item['url']).encode('utf-8')).hexdigest()
    ret = db.find(item)
    if ret: return ret
    db.update(item)
    return False


sess = requests.session()


def crawl(biz, url, headers):
    url = 'https://mp.weixin.qq.com/mp/getmasssendmsg' + url + '&frommsgid=%s&f=json&count=%s'
    frommsgid = -1
    exit = False
    while exit == False:
        time.sleep(1)
        response = sess.get(url=url % (frommsgid, 10), headers=headers)
        data = json.loads(response.content)
        if data['ret'] != 0:
            print data['errmsg']
            return
        msg_list = json.loads(data['general_msg_list'])['list']
        for msg in msg_list:

            app_msg_ext_info = msg['app_msg_ext_info']
            comm_msg_info = msg['comm_msg_info']

            for msgm in app_msg_ext_info['multi_app_msg_item_list']:
                item = {}
                content_url = html2dict(msgm['content_url'])
                item['url'] = content_url
                item['date'] = datetime.datetime.fromtimestamp(comm_msg_info['datetime']).strftime('%Y-%m-%d %H:%M:%S')
                if url.find('http') == -1:
                    continue
                msgdetail = sess.get(content_url)
                print content_url
                item.update(parse_content(msgdetail.content))
                store_item(item)

            frommsgid = comm_msg_info['id']
            content_url = html2dict(app_msg_ext_info['content_url'])
            item = {}
            item['url'] = content_url
            item['date'] = datetime.datetime.fromtimestamp(comm_msg_info['datetime']).strftime('%Y-%m-%d %H:%M:%S')
            if content_url.find('http') == -1:
                continue
            msgdetail = sess.get(content_url)
            print content_url
            item.update(parse_content(msgdetail.content))
            if store_item(item):
                exit = True
                break
        if data['is_continue'] == 0:
            exit = True


def main():
    dbkey = MongoClient(host='10.2.11.234', port=27017)['wechatkeys']['wechatkeys']
    for i in dbkey.find():
        biz = i['biz']
        headers = i['headers']
        for k in headers.keys():
            headers[k] = headers[k][0]
        url = i['url']
        seq = '?'
        ans = ''
        for k in url.keys():
            ans += seq + k + '=' + url[k][0]
            seq = '&'
        url = ans
        crawl(biz, url, headers)

if __name__ == '__main__':
    main()

