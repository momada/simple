import config


def summary(page, i):
    if page == 't':
        return config.pdb.select('town', order='update_date DESC,price ASC', limit=25, offset=25 * (i - 1))
    elif page == 'h':
        return config.pdb.select('house', order='update_date DESC , price ASC', limit=25, offset=25 * (i - 1))
    # return config.pdb.select('house',order='update_date DESC , price ASC',limit=23,offset=23*(pagenumber-1))
    elif page == 'w':
        return config.pdb.select('west', order='update_date DESC,price ASC', limit=25, offset=25 * (i - 1))
    else:
        return None


def marker(pagenumber):
    # yd = (datetime.datetime.today()- datetime.timedelta(days=2))
    #    return config.pdb.select('house',what ='address,price',where="update_date > $d", vars = {'d':yd},order='price ASC', limit=23)
    return config.pdb.select('house', what='address,price', order='update_date DESC,price ASC', limit=18)


def maxx(table):
    if table == 't':
        return config.pdb.select('town', what="count(*) as count")[0].count
    if table == 'h':
        return config.pdb.select('house', what="count(*) as count")[0].count
    if table == 'w':
        return config.pdb.select('west', what="count(*) as count")[0].count
