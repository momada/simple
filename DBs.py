import config


def summary(pagenumber):
    return config.DB_s.select('news', order='post_date DESC', limit=25, offset=25 * (pagenumber - 1))


def detail(i):
    qs = 'news_id = \'' + i.encode('ascii') + '\''
    return config.DB_s.select('news', where=qs)


def search(_filter, num):
    res = config.DB_s.select('news', where=_filter, order='post_date DESC', limit=25, offset=25 * (int(num) - 1))
    countnum = config.DB_s.select('news', what="count(*) as count", where=_filter)[0].count
    return res, countnum


def maxx():
    return config.DB_s.select('news', what="count(*) as count")[0].count
