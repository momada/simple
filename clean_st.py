#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# clean up singtao db for old data
import datetime
import sqlite3

conn = sqlite3.connect('/var/www/news/singtao.db')
conn.text_factory = str
c = conn.cursor()
try:
    today = datetime.date.today()
    delta = datetime.timedelta(5)
    margin_date = today - delta
    c.execute('delete from news where post_date < "' + margin_date.strftime("%Y-%m-%d") + '" ')
    print 'Done'
except sqlite3.Error, e:
    print "An error occurred:", e.args[0]
conn.commit()
c.close()
