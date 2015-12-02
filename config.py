import web

DB = web.database(dbn='sqlite', db='news.sqlite3.db')
DB_s = web.database(dbn='sqlite', db='singtao.db')
pdb = web.database(dbn='postgres', host='192.168.2.130', port=5432, db='mydata', user='webclient', pw='wayaocun')

cache = False
