#!/usr/bin/env python
# -*- coding: utf-8 -*-
# news.py fetch news from web sites

import datetime
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
MAXC = 10


def thread_fetch():
    while True:
        topic = q.get()
        fetch(topic)
        q.task_done()


def wenxue(num=1):
    urlbase = 'http://www.wenxuecity.com/news/'
    for i in range(1, num + 1):
        print 'fetching wenxue city news on page', i, '...'
        url = urlbase + "morenews/?page=" + str(i)
        res = httpfetch(url, 'gb2312')
        res2 = re.compile(r'<div class="list" id="contentList">(.*?)<div class="turnpage">', re.DOTALL).findall(res)
        if res2:
            res2 = res2[0]
        else:
            continue
        # 抓取新闻条目的ID
        topics = re.compile(r'<a href="(.*?)" target="_blank">', re.DOTALL).findall(res2)
        topics = set(topics)

        print topics
        for topic in topics:
            q.put(topic)


def singtao():
    cons = sqlite3.connect(path + '/singtao.db')
    cons.text_factory = str
    url = 'http://news.singtao.ca/vancouver/' + datetime.date.today().strftime("%Y-%m-%d") + '/'
    res = httpfetch(url, 'utf-8')
    #    f=file('a.html','r')
    #    res =f.read()
    #    f.close()
    res2 = re.compile(r'>headline(.*?)\.html', re.DOTALL).findall(res)

    for topic in res2:
        web_site = '星島日報'
        if dbfind(topic, web_site, conn):
            return
        urlbase = url + 'headline' + topic + '.html'

        try:
            item_page = httpfetch(urlbase, 'utf-8', report=True)
        except Exception:
            print "Unexpected error:", sys.exc_info()[1]

        try:
            title = re.compile(r'<title>(.*?)</title>', re.DOTALL).findall(item_page)[0].split('_')[0]
            content = re.compile(r'<div class="content" id="Zoom">(.*?)</div>', re.DOTALL).findall(item_page)[0]
            content = re.compile(r'<br />', re.DOTALL).sub('\n', content)
            content = re.compile(r'<.*?>', re.DOTALL).sub('', content)
            content = re.compile(r'&.*?;', re.DOTALL).sub(' ', content)
            content = re.compile(r'\n\s+', re.DOTALL).sub('\n', content)
        # content = content.strip()
        except:
            print "Unexpected error:", sys.exc_info()[1]
            print urlbase
        source = '星島日報'

        post_date = datetime.date.today().strftime("%Y-%m-%d")
        tries = 0
        while tries < 2:
            try:
                if not dbfind(topic, web_site, cons):
                    dbinsert(topic, title, source, content, post_date, urlbase, web_site, conn)
                else:
                    continue
            except Exception:
                print urlbase
                print sys.exc_info()[0]
                tries += 1;
                time.sleep(10);
                continue
            break

    return


def fetch(id, debug=False):
    con = sqlite3.connect(path + '/news.sqlite3.db')
    con.text_factory = str
    print 'fetching topic', id, '...'
    urlbase = 'http://www.wenxuecity.com'
    url = urlbase + id
    news_id = id.split('/')[5]
    news_id = news_id.split('.')[0]
    w = "文学城"
    if dbfind(news_id, w, con):
        con.close()
        return

    res = ''
    for _ in range(3):
        try:
            res = httpfetch(url, 'utf-8', report=True)
            break
        except:
            print sys.exc_info()[1]
            continue
    res = re.compile(r'<div class="maincontainer">(.*?)<div class="banners">', re.DOTALL).findall(res)[0]
    title = re.compile(r'<h3>(.*?)</h3>', re.DOTALL).findall(res)
    if title:
        title = title[0].encode('utf-8')
        link = url
        web_site = '文学城'
    else:
        con.close()
        return
    try:
        parse = re.compile(r'<div id="postmeta">(.*?) <span>', re.DOTALL).search(res).group(1)
        source = re.compile(r'itemprop="author">(.*?)</span>', re.DOTALL).findall(parse)[0]
        post_date = re.compile(r'datetime(.*?)</time>', re.DOTALL).findall(parse)[0]
        post_date = post_date.split('>')[1]
        content = re.compile(r'<div id="articleContent" class="article">(.*?)<div class="sharewechat">',
                             re.DOTALL).findall(res)
    # print "Content:",content
    except:
        con.close()
        return

    if content:
        content = content[0]
        content = re.compile(r'<div style=(.*?)', re.DOTALL).sub('', content)
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

    if not content:
        print news_id

    tries = 0
    while tries < 2:
        try:
            if not dbfind(news_id, web_site, con):
                dbinsert(news_id, title, source, content, post_date, link, web_site, con)
            else:
                continue
            # dbupdate(news_id,title,source,content,post_date,link,web_site,conn)
            break;
        except:
            print sys.exc_info()[0]
            tries += 1;
            time.sleep(5);
            continue;
    con.close()
    return post_date


def dbcreate():
    c = conn.cursor()
    try:
        c.execute('''create table news(
        news_id text,
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
    while tries < 1:
        try:
            c.execute('insert into news values(?,?,?,?,?,?,?)', \
                      (id, title, source, content, post_date, link, web_site))
            break
        except:
            print sys.exc_info()[0]
            print sys.exc_info()[1]
            print sys.exc_info()[2]
            tries += 1
            time.sleep(500)
            continue
    conn.commit()
    c.close()


def dbclean(days):
    c = conn.cursor()
    try:
        today = datetime.date.today()
        delta = datetime.timedelta(days=int(days))
        margin_date = today - delta
        c.execute('delete from news where post_date < "' + margin_date.strftime("%Y-%m-%d") + '" ')
    except sqlite3.Error, e:
        print "An error occurred:", e.args[0]
    conn.commit()
    c.close()


def dbupdate(id, title, source, content, post_date, link, web_site, conn):
    tries = 0
    c = conn.cursor()
    while tries < 10:
        try:
            c.execute(
                'update news set news_id=?,title=?,source=?,content=?,post_date=?,link=?,web_site=? where news_id=?', \
                (id, title, source, content, post_date, link, web_site, id))
            break
        except:
            tries += 1
            time.sleep(5)
            continue
            conn.commit()
            c.close()
    return


def dbfind(id, website, conn):
    c = conn.cursor()
    q = 'select 1 from news where news_id="' + id.encode('ascii') + '" and web_site="' + website.decode('utf-8') + '"'
    c.execute(q)
    for x in c:
        if 1 in x:
            return True
        else:
            return False
    c.close()


def dblist():
    c = conn.cursor()
    c.execute('select rowid,title from news')
    for x in c:
        print x[0], x[1]


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
    elif len(sys.argv) > 1:
        if sys.argv[1] == 'createdb':
            dbcreate()
        elif sys.argv[1] == 'wenxue':
            wenxue()
        elif sys.argv[1] == 'singtao':
            singtao()
        elif sys.argv[1] == 'list':
            dblist()
        elif sys.argv[1] == 'clean':
            dbclean(sys.argv[2])
        else:
            fetch((sys.argv[1]), debug=False)

    # wait all threads done
    q.join()
