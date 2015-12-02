#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# news.py fetch news from web sites

import os
import re
import sqlite3
import sys
import time
from Queue import Queue
from threading import Thread

from download import httpfetch

path = os.path.dirname(os.path.realpath(sys.argv[0]))
conn = sqlite3.connect(path + '/news.sqlite3.db')
conn.text_factory = str
q = Queue()
MAXC = 8


def thread_fetch():
    conn = sqlite3.connect(path + '/news.sqlite3.db')
    conn.text_factory = str
    while True:
        topic = q.get()
        fetch(topic, conn)
        q.task_done()


# def search(keyword,full=True):
#    '''search verycd, fetch search results'''
#
#    searchlog = path+'/search.log'
#    open(searchlog,'a').write('\n'+keyword+'\n')
#
#    url = 'http://www.verycd.com/search/folders/'+keyword
#    print 'fetching search results ...'
#    res = httpfetch(url)
#    topics = re.compile(r'/topics/(\d+)',re.DOTALL).findall(res)
#    topics = set(topics)
#    links = []
#    if full:
#        links = re.compile(r'/search/folders/(.*?\?start=\d+)',re.DOTALL).findall(res)
#        print links
#    print topics
#    if topics:
#        for topic in topics:
#            open(searchlog,'a').write(topic+',')
#            q.put(topic)
#    if full and links:
#        for key in links:
#            search(key,full=False)
#        
#
# def hot():
#    ''' read verycd hot res and keep update very day '''
#    url = 'http://www.verycd.com/'
#    print 'fetching homepage ...'
#    home = httpfetch(url)
#    hotzone = re.compile(r'热门资源.*?</dl>',re.DOTALL).search(home).group()
#    hot = re.compile(r'<a href="/topics/(\d+)/"[^>]*>(《.*?》)[^<]*</a>',re.DOTALL).findall(hotzone)
#    html = '<h2 style="color:red">每日热门资源</h2>\n'
#    for topic in hot:
#        print 'fetching hot topic',topic[0],'...'
#        q.put(topic[0])
#        html += '&nbsp;<a target="_parent" href="/?id=%s">%s</a>&nbsp;\n' % topic
#    open(path+'/static/hot.html','w').write(html)
#
# def normal(pages):
#    '''fetch normal res that need login'''
#    if '-' in pages:
#        (f,t)=[ int(x) for x in pages.split('-') ]
#    else:
#        f = t = int(pages)
#    for page in range(f,t+1):
#        url = 'http://www.verycd.com/orz/page%d?stat=normal' % page
#        idx = httpfetch(url,needlogin=True)
#        ids = re.compile(r'/topics/(\d+)',re.DOTALL).findall(idx)
#        print ids[0]
#        for id in ids:
#            q.put(id)
#
# def request(pages):
#    '''fetch request res that need login'''
#    if '-' in pages:
#        (f,t)=[ int(x) for x in pages.split('-') ]
#    else:
#        f = t = int(pages)
#    for page in range(f,t+1):
#        url = 'http://www.verycd.com/orz/page%d?stat=request' % page
#        idx = httpfetch(url,needlogin=True)
#        ids = re.compile(r'/topics/(\d+)',re.DOTALL).findall(idx)
#        print ids[0]
#        for id in ids:
#            q.put(id)
#
# def feed():
#    ''' read verycd feed and keep update very 30 min '''
#    url = 'http://www.verycd.com/sto/feed'
#    print 'fetching feed ...'
#    feeds = httpfetch(url)
#    ids = re.compile(r'/topics/(\d+)',re.DOTALL).findall(feeds)
#    ids = set(ids)
#    print ids
#    #now = time.mktime(time.gmtime())
#    for id in ids:
#        q.put(id)
#        #updtime = fetch(id)
#        #updtime = time.mktime(time.strptime(updtime,'%Y/%m/%d %H:%M:%S'))-8*3600 #gmt+8->gmt
#        #diff = now - updtime
#        #print '%10s secs since update' % (diff)
#        #if diff > 1900: # only need recent 30min updates
#        #    break

def wenxue(num=1):
    urlbase = 'http://news.wenxuecity.com/index.php?page='
    for i in range(1, num + 1):
        print 'fetching wenxue city news on page', i, '...'
        url = urlbase + str(i)
        res = httpfetch(url)
        res2 = re.compile(r'"images/bbslogos/news\.gif"(.*?)"BBSAdd\.php\?SubID=news"', re.DOTALL).findall(res)
        if res2:
            res2 = res2[0]
        else:
            continue

        topics = re.compile(r'messages/(.*?)\.html', re.DOTALL).findall(res2)
        topics = set(topics)

        print topics
        for topic in topics:
            q.put(topic)


def fetch(id, conn=conn, debug=False):
    print 'fetching topic', id, '...'
    urlbase = 'http://news.wenxuecity.com/messages/'
    url = urlbase + str(id) + '.html'
    news_id = id.split('-')[2]
    if dbfind(news_id, conn):
        return

    res = ''
    for _ in range(3):
        try:
            res = httpfetch(url, report=True)
            break
        except:
            continue

    title = re.compile(r'<h1 class="cnTitle">(.*?)</h1>', re.DOTALL).findall(res)
    if title:
        title = title[0]
        link = url
        web_site = '文学城'
    else:
        return
    try:
        source = re.compile(r'<span style="color: #006699;">(.*?)</span>', re.DOTALL).search(res).group(1)
        post_date = re.compile(r'#cc3300;">(.*?)</span>', re.DOTALL).search(res).group(1)
        content = re.compile(r'<td valign="top" class="main">(.*?)<div align="right">', re.DOTALL).findall(res)
    except:
        return

    if content:
        content = content[0]
        content = re.compile(r'<br />', re.DOTALL).sub('\n', content)
        content = re.compile(r'<.*?>', re.DOTALL).sub('', content)
        content = re.compile(r'&.*?;', re.DOTALL).sub(' ', content)
        content = re.compile(r'\n\s+', re.DOTALL).sub('\n', content)
        content = content.strip()
    else:
        content = ''

    if debug:
        print title
        print source
        print content
        print post_date
        print web_site

    tries = 0
    while tries < 3:
        try:
            if not dbfind(news_id, conn):
                dbinsert(news_id, title, source, content, post_date, link, web_site, conn)
            else:
                continue
            # dbupdate(news_id,title,source,content,post_date,link,web_site,conn)
            break;
        except:
            print sys.exc_info()[0]
            tries += 1;
            time.sleep(5);
            continue;

    return post_date


def dbcreate():
    c = conn.cursor()
    try:
        c.execute('''create table news(
        news_id integer primary key,
        title text,
        source text,
        content text,
        post_date text,
        link text,
        web_site text
        )''')
        conn.commit()
        c.close()
    except:
        print "Unexpected error:", sys.exc_info()[1]


def dbinsert(id, title, source, content, post_date, link, web_site, conn):
    c = conn.cursor()
    tries = 0
    while tries < 3:
        try:
            c.execute('insert into news values(?,?,?,?,?,?,?)', \
                      (id, title, source, content, post_date, link, web_site))
            break
        except:
            print sys.exc_info()[0]
            print sys.exc_info()[1]
            print sys.exc_info()[2]
            tries += 1
            time.sleep(3)
            continue
    conn.commit()
    c.close()


def dbclean():
    tries = 0
    c = conn.cursor()
    while tries < 3:
        try:

            c.execute('select * from news where post_date <"2011-04-28 08:00:00"')
            for row in c:
                print 'ID: ', row[0]
            # print 'Title: ',row[1]
            print len(c)
            break
        except:
            tries += 1
            time.sleep(5)
            continue
    conn.commit()
    c.close()


# def dbupdate(id,title,source,content,post_date,link,web_site,conn):
#    tries = 0
#    c = conn.cursor()
#    while tries<10:
#        try:
#            c.execute('update news set news_id=?,title=?,source=?,content=?,post_date=?,link=?,web_site=? where news_id=?',\
#            (id,title,source,content,post_date,link,web_site,id))
#            break
#        except:
#            tries += 1
#            time.sleep(5)
#            continue
#    conn.commit()
#    c.close()

def dbfind(id, conn):
    c = conn.cursor()
    c.execute('select 1 from news where news_id=?', (id,))
    c.close()
    for x in c:
        if 1 in x:
            return True
        else:
            return False


def dblist():
    c = conn.cursor()
    c.execute('select title,content from news')
    for x in c:
        for y in x:
            print y


def usage():
    print '''Usage:
  python news.py createdb
  python news.py wenxue
  python news.py list
  '''


# initialize thread pool
for i in range(MAXC):
    t = Thread(target=thread_fetch)
    t.setDaemon(True)
    t.start()

if __name__ == '__main__':

    # Import Psyco if available
    try:
        import psyco

        psyco.full()
    except ImportError:
        pass

    if len(sys.argv) == 1:
        usage()
    elif len(sys.argv) == 2:
        if sys.argv[1] == 'createdb':
            dbcreate()
        elif sys.argv[1] == 'wenxue':
            wenxue()
        elif sys.argv[1] == 'list':
            dblist()
        elif sys.argv[1] == 'clean':
            dbclean()
        else:
            fetch((sys.argv[1]), debug=False)

    # wait all threads done
    q.join()
