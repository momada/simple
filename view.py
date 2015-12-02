import datetime

import web

import DBs
import config
import db
import pdb

t_globals = dict(datestr=web.datestr, )
render = web.template.render('templates/', cache=config.cache, globals=t_globals)
render._keywords['globals']['render'] = render


def summary(page):
    l = db.summary(page)
    return render.list(l)


def summary_s(page):
    l = DBs.summary(page)
    return render.lists(l)


def summary_p(page, i):
    l = pdb.summary(page, i)
    y = (datetime.datetime.now() - datetime.timedelta(days=5)).date()
    return render.listp(l, y)


def detail(_id):
    r = db.detail(_id)
    return render.detail(r)


def detail_s(_id):
    r = DBs.detail(_id)
    return render.detail(r)


def search(_filter, p):
    res = db.search(_filter, p)[0]
    return render.list(res)


def pagecontrol(pnum, maxnum, arg):
    prev = int(pnum) - 1 == 0 and '1' or str(int(pnum) - 1)
    nex = int(pnum) + 1 <= (maxnum - 1) / 25 + 1 and str(int(pnum) + 1) or pnum
    end = str((maxnum - 1) / 25 + 1)
    pages = [prev, nex, end]
    left = min(4, int(pnum) - 1)
    right = min(4, int(end) - int(pnum))
    if left < 4:
        right = min(8 - left, int(end) - int(pnum))
    if right < 4:
        left = min(8 - right, int(pnum) - 1)
    while left > 0:
        pages.append(str(int(pnum) - left))
        left -= 1
    j = 0
    while j <= right:
        pages.append(str(int(pnum) + j))
        j += 1
    return render.page([pages, arg])
