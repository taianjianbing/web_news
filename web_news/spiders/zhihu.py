# import os
from web_news.misc.spiderredis import SpiderRedis
from scrapy.http import FormRequest, Request
import json
import re
from web_news.items import *
from math import ceil
import requests
from bs4 import BeautifulSoup

# if not os.path.exists('images'):
#     os.mkdir("images")


class ZhihuTopicSpider(SpiderRedis):
    name = 'zhihu'
    website = '知乎'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/topics']
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
    }

    def parse(self, response):
        for sel in response.xpath('//li[@class="zm-topic-cat-item"]'):
            topic_id = sel.xpath('@data-id').extract()[0]
            name = sel.xpath('a/text()').extract()[0]

            url = 'https://www.zhihu.com/topics'
            post_url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
            params = json.dumps({
                'topic_id': topic_id,
                'offset': 0,
                'hash_id': ''
            })
            data = {
                '_xsrf': '',
                'method': 'next',
                'params': params
            }
            headers = {
                'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                'Host': "www.zhihu.com",
                'Referer': url
            }
            yield FormRequest(url=post_url, formdata=data, headers=headers, callback=self.get_topic)

    def get_topic(self, response):
        msg = json.loads(response.body_as_unicode())['msg']
        pattern = re.compile('<a.*?href="/topic/(.*?)">.*?<strong>(.*?)</strong>', re.S)
        topics = re.findall(pattern, ''.join(msg))
        for topic in topics:
            yield Request('https://www.zhihu.com/topic/%s/hot' % topic[0], callback=self.get_question)

    def get_question(self, response):
        data_score = response.xpath('//div[@itemprop="question"]/@data-score')
        data_score = float(data_score.extract()[0])
        offset = ceil(data_score)
        post_url = response.url
        flag = True
        while flag and offset > 3150:
            data = {
                'start': 0,
                'offset': offset
            }
            headers = {
                'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                'Host': "www.zhihu.com",
                'Referer': response.url
            }
            post_msg = requests.post(post_url, data=data, headers=headers)
            msg = post_msg.json()['msg'][1]
            pattern = re.compile('<a.*?class="question_link".*?href="/question/(.*?)".*?>(.*?)</a>', re.S)
            results = re.findall(pattern, ''.join(msg))
            if len(results) == 0:
                flag = False
            else:
                soup = BeautifulSoup(msg, 'html.parser')
                divs = soup.find_all('div', 'feed-item feed-item-hook  folding')
                if len(divs) == 0:
                    flag = False
                else:
                    offset = float(divs[-1]['data-score'])
            for result in results:
                yield Request('https://www.zhihu.com/question/%s' % result[0], callback=self.get_answer)

    def get_answer(self, response):
        url = response.url
        question_id = url.split('/')[-1]
        answer_num = response.xpath('//h3[@id="zh-question-answer-num"]/@data-num').extract()
        if len(answer_num) == 0:
            answer_num = 0
        else:
            answer_num = answer_num[0]

        offset = 0
        page_size = 10
        while offset < int(answer_num) and offset <= 30:
            post_url = "http://www.zhihu.com/node/QuestionAnswerListV2"
            params = json.dumps({
                'url_token': question_id,
                'pagesize': page_size,
                'offset': offset
            })
            data = {
                '_xsrf': '',
                'method': 'next',
                'params': params
            }
            headers = {
                'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                'Host': "www.zhihu.com",
                'Referer': url
            }
            response = requests.post(post_url, data=data, headers=headers)
            answer_list = response.json()['msg']
            # 爬取图片
            # img_urls = re.findall('img .*?data-actualsrc="(.*?_b.*?)"', ''.join(answer_list))
            # for img_url in img_urls:
            #     try:
            #         file_name = basename(img_url)
            #         print(file_name)
            #         img_data = request.urlopen(img_url).read()
            #         print('read success')
            #         output = open('images/' + file_name, 'ab')
            #         output.write(img_data)
            #         output.close()
            #     except Exception as e:
            #         print('read fail', e)
            for answer in answer_list:
                soup = BeautifulSoup(answer, 'html.parser')

                message = soup.find('div', 'zm-item-rich-text expandable js-collapse-body')
                data_entry_url = message['data-entry-url'].split('/')
                question_id = data_entry_url[2]
                answer_id = data_entry_url[4]
                content = soup.find('div', 'zm-editable-content clearfix').get_text()
                agree_num = soup.find('span', 'count').get_text()
                author = soup.find('a', 'author-link')
                if author:
                    user_url = 'https://www.zhihu.com' + author['href']
                else:
                    user_url = '匿名用户'
                summary = soup.find('div', 'zh-summary summary clearfix').get_text()
                comment_num = soup.find('a', 'meta-item toggle-comment js-toggleCommentBox').get_text().replace('\n', '')
                comment_num = 0 if comment_num == u'添加评论' else comment_num[:comment_num.find(' ')]

                answer_item = ZhihuAnswerItem()
                answer_item['url'] = "https://www.zhihu.com/question/" + question_id + "/answer/" + answer_id
                answer_item['content'] = content
                answer_item['agree_num'] = agree_num
                answer_item['question_id'] = question_id
                answer_item['question_url'] = "https://www.zhihu.com/question/" + question_id
                answer_item['answer_id'] = answer_id
                answer_item['user_url'] = user_url
                answer_item['summary'] = summary
                answer_item['comment_num'] = comment_num
                answer_item['collection_name'] = self.name
                answer_item['website'] = self.website

                yield answer_item
            offset += page_size