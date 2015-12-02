#!/usr/bin/env python
# -*- coding: utf-8 -*-
# news.py fetch news from web sites
import web

import DBs
import db
import feedparser
import view
import ystockquote
from view import render

urls = ('/', 'index',
        '/map', 'realmap',
        '/singtao', 'singtao',
        '/singtao/', 'singtao')


class index:
    def GET(self):
        i = web.input(id=None, p='1', q=None)
        # Detail Page
        if i.id:
            _id = i.id
            page = None
            try:
                body = view.detail(_id)
            except:
                print
                return render.error()
                # Search results page
        elif i.q:
            qs = i.q.split(' ')
            qs = ['content like \'%' + x + '%\'' for x in qs]
            _filter = ' and '.join(qs)
            arg = '/?q=' + i.q + '&p'
            page = view.pagecontrol(i.p, db.search(_filter, i.p)[1], arg)
            body = view.search(_filter, i.p)
        # Summary page for page number, default is home page
        else:
            pagenumber = int(i.p)
            if pagenumber > db.maxx():
                return render.error()
            body = view.summary(pagenumber)
            arg = '/?p'
            page = view.pagecontrol(i.p, db.maxx(), arg)
        s = banner()
        return render.base([body, page, i.q, s])


class singtao:
    def GET(self):
        i = web.input(id=None, p='1')
        # Detail Page
        if i.id:
            _id = i.id
            page = None
            try:
                body = view.detail_s(_id)
            except:
                return render.error()
                # Summary page for page number, default is home page
        else:
            pagenumber = int(i.p)
            if pagenumber > DBs.maxx():
                return render.error()
            body = view.summary_s(pagenumber)
            arg = '/singtao/?p'
            page = view.pagecontrol(i.p, DBs.maxx(), arg)
        s = banner()
        return render.base([body, page, None, s])


def banner():
    d = feedparser.parse('http://weather.yahooapis.com/forecastrss?w=9807&u=c')
    temp = d['feed'][u'yweather_location']['city'] + ': ' + d['entries'][0][u'yweather_condition']['text'] + ' ' + \
           d['entries'][0][u'yweather_condition']['temp'] + 'C'
    s = ystockquote.get_all('abt.to')
    stock = ['Abt: $' + s['price'], 'Change: ' + s['change'], temp]
    return stock


if __name__ == "__main__":
    app = web.application(urls, globals())
    # Error debugger should be commented in production
    app.internalerror = web.debugerror

    # web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
