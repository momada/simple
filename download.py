#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# download.py: download with report

import os
import sys
import urllib2
from time import sleep

# from time import time,sleep
#from urllib import ContentTooShortError

path = os.path.dirname(os.path.realpath(sys.argv[0]))

#proxies = {'http':'http://proxyaddress:port'}
#proxy_support = urllib2.ProxyHandler(proxies)
#opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
#urllib2.install_opener(opener)

#functions
def report(blocknum, bs, size, t):
    if t == 0:
        t = 1
    if size == -1:
        print '%10s' % (str(blocknum * bs)) + ' downloaded | Speed =' + '%5.2f' % (bs / t / 1024) + 'KB/s'
    else:
        percent = int(blocknum * bs * 100 / size)
        print '%10s' % (str(blocknum * bs)) + '/' + str(size) + 'downloaded | ' + str(
            percent) + '% Speed =' + '%5.2f' % (bs / t / 1024) + 'KB/s'


def httpfetch(url, charset, headers={}, reporthook=report, postData=None, report=True):
    ok = False
    for _ in range(2):
        try:
            reqObj = urllib2.Request(url, postData, headers)
            fp = urllib2.urlopen(reqObj)
            headers = fp.info()
            rawdata = fp.read()
            #print rawdata
            rawdata = rawdata.decode(charset, 'ignore')

            ok = True
            break
        except:
            print sys.exc_info()[0]
            print sys.exc_info()
            print sys.exc_info()[2]
            sleep(3)
            continue

    if not ok:
        open(path + '/errors', 'a').write(url + '\n')
        return ''
    return rawdata


if __name__ == '__main__':

    try:
        import psyco

        psyco.full()
    except ImportError:
        pass

    url = 'http://www.wenxuecity.com/news/morenews/'
#    test it
    data = httpfetch(url, "utf-8")
    open('down.html', 'w').write(data.encode("utf-8"))

