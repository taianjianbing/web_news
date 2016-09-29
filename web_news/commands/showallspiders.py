import os
import re
def main():
    spiders = os.listdir("../spiders")
    spiders.sort()    
    for spider in spiders:
        if spider.find('__init__') != -1 or spider.endswith('pyc'):
            continue
        with open("../spiders/"+spider, "r") as f:
            print spider,
            for line in f:
                a = re.search('website\W=', line)
                if a == None:
                    continue
                print re.search("\'.*\'", line.strip().replace('\"', '\'')).group(),
            print ""
        # break 

if __name__ == '__main__':
    main()