#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# download.py: download with report

import sys
import urllib2
from time import sleep


def httpfetch(url, charset, headers={}, postData=None, report=True):
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

