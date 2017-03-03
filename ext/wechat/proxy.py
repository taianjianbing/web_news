
import urlparse
from pymongo import MongoClient
import json
db = MongoClient(host='10.2.11.234', port=27017)['wechatkeys']


def request(context, flow):
    url = flow.request.get_url()
    if url.find('getmasssendmsg')==-1:
        return
    par = urlparse.parse_qs(urlparse.urlparse(url).query)
    data = {'biz': par['__biz'][0]}
    data['url'] = par
    data['headers'] = dict(flow.request.headers)
    db.wechatkeys.update({'biz': data['biz'],}, {'$set': dict(data)}, True, True)

