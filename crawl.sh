#!/usr/bin/env bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
cd /home/u234/web_news
for spider in tianya ifeng sznews yunyan gysdj gywb nmdj gysjw huanqiu itmsc techxinwen southcn bjnews kejixun cnetnews citnews bjd k618 21cn huaxi100 tongren qiannan zunyi anshun
do
    if [ ! -e log ]
    then
        mkdir log
    fi
    ./clearredis $spider
    for i in 1 2 3 4 5 6 7 8 9 10
    do
        nohup scrapy crawl $spider --logfile=log/$spider$i.log &
    done
    pid=`ps -ef | grep $spider1.log | grep -v grep | awk '{print $2}'`
    wait $pid
done
cd ext/crawler/
sh tencent.sh
pid=`ps -ef | grep spider.py | grep -v grep | awk '{print $2}'`
wait $pid

cd ../wechat/wechat/
sh wechat.sh
pid=`ps -ef | grep main.py | grep -v grep | awk '{print $2}'`
wait $pid
