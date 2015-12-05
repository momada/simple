#!/usr/bin/env python
# -*- coding: utf-8 -*-
# database access

import datetime
import os
import sqlite3
import sys

path = os.path.dirname(os.path.realpath(sys.argv[0]))
conn = sqlite3.connect(path + '/news.sqlite3.db')
conn.text_factory = str


def find(i, website, conn):
    c = conn.cursor()
    q = 'select 1 from news where news_id="' + i.encode('ascii') + '" and web_site="' + website.decode('utf-8') + '"'
    c.execute(q)
    for x in c:
        if 1 in x:
            return True
        else:
            return False
    c.close()
    return


def insert(i, title, source, content, post_date, link, web_site, conn):
    c = conn.cursor()
    try:
        c.execute('insert into news values(?,?,?,?,?,?,?)', \
                  (i, title, source, content, post_date, link, web_site))
    except:
        print sys.exc_info()[0]
        print sys.exc_info()[1]
        print sys.exc_info()[2]
    conn.commit()
    c.close()
    print "insert:", title, post_date
    return


def update(id, title, source, content, post_date, link, web_site, conn):
    c = conn.cursor()
    try:
        c.execute(
            'update news set news_id=?,title=?,source=?,content=?,post_date=?,link=?,web_site=? where news_id=?',
            (id, title, source, content, post_date, link, web_site, id))
    except:
        print sys.exc_info()[0]
        print sys.exc_info()[1]
        print sys.exc_info()[2]
    conn.commit()
    c.close()
    print "update:,", title, post_date
    return


def create():
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
    return


def clean(days):
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
    print "clean up for %s days" % days
    return


def list_news():
    c = conn.cursor()
    c.execute('select rowid,title from news')
    for x in c:
        print x[0], x[1]
    return


if __name__ == "__main__":
    clean(6)
