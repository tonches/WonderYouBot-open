from sqlalchemy import create_engine
import config
import time
from datetime import datetime

db_name = config.db_name
db_user = config.db_user
db_pass = config.db_pass
db_host = config.db_host
db_port = config.db_port

db_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_user, db_pass, db_host, db_port, db_name)
db = create_engine(db_string)


def check_column(n):
    res = db.execute("SELECT EXISTS (SELECT column_name FROM information_schema.columns "
                     "WHERE table_name='reads' and column_name='" + str(n) + "');")
    for (r) in res:
        return r[0]

def add_column(n):
    db.execute("ALTER table reads add column \"" + str(n) + "\"  smallint;")


def add_new_row(n, t):
    # Insert a new number into the 'numbers' table.
    ts = int(round(time.time())) - 2*3600 - t*3600  #до 5 утра день длится
    d = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
    db.execute("update reads set \"" + str(n) + "\" = 1 where date = '" + str(d) + "';")
    

def check_name(table, userid):
    query = ("SELECT EXISTS (SELECT name FROM " 
             + table + " WHERE number = " + str(userid) + ");")
    result_set = db.execute(query)
    for (r) in result_set:  
        return r[0]
    '''query = ("SELECT EXISTS (SELECT 1 FROM "
             "information_schema.columns WHERE "
             "table_name='" + table + "' AND "
             "column_name='" + name  + "');")'''

def check_same(name):
	query = ("SELECT exists (SELECT 1 FROM names WHERE name = '" + str(name) + "' LIMIT 1);")
	res = db.execute(query)
	for (r) in res:
		return r[0]

             
def insert_name(userid, name):
    if check_name('names', userid) != True:
        query = ("INSERT INTO names (number,name) VALUES "
                "(" + str(userid) + ", '" + str(name) + "');")
        db.execute(query)
    else:
        pass

def change_name(userid, name):
	query = ("update names set name = '" + str(name) + "' where number = '" + str(userid) + "';")
	db.execute(query)

def get_name(userid):
    res = db.execute("select name from names where number = " + str(userid) + ";")
    for (r) in res:
        return r[0]

def in_group(userid, groupid):
    res = db.execute("SELECT exists (SELECT * FROM names WHERE number = " + str(userid) + " and " + str(groupid) + " = ANY(groupids) LIMIT 1);")
    for (r) in res:
        return r[0]


def attend_to_group(userid, groupid):
    db.execute("UPDATE names set groupids = groupids || '{" + str(groupid) + "}' where number = " + str(userid) + ";")


def remove_from_group(userid, groupid):
    db.execute("UPDATE names set groupids = array_remove(groupids, " + str(groupid) + ") where number = " + str(userid) + ";")

def get_groups():
    res = db.execute("with cte as (select number, groupids from names) select to_json(cte) from cte;")
    list_of_dicts = [row[0] for row in res]
    fin = {}
    for hash in list_of_dicts:
        fin[hash["number"]] = hash["groupids"]
    return(fin)

def get_names():
    res = db.execute("select number from names order by number;")
    list_of_dicts = [row[0] for row in res]
    return list_of_dicts

def get_times(mode):
    ts = int(round(time.time())) - 2*3600   #5 am MSK is here
    
    if mode == 'mm':
        dn = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
        ds = datetime.today().replace(day=1).strftime('%Y-%m-%d')
        return [dn, ds]
    elif mode == 'series':
        dn = datetime.utcfromtimestamp(ts).strftime('%d')
        ds = datetime.today().replace(day=1).strftime('%d')
        times = []
        for i in range(int(ds), int(dn) + 1):
            times.append( {"text": str(i)} )
        return times

def add_id(groupid):
    db.execute("INSERT INTO ids (groupid,id) VALUES (" + str(groupid) + " ,0);")


def check_id(groupid):
    res = db.execute("SELECT exists (SELECT * FROM ids WHERE groupid = " + str(groupid) + " LIMIT 1);")
    for (r) in res:
        return r[0]

def increment_id(groupid, mode):
    res = db.execute("select id from ids where groupid = " + str(groupid) + ";")
    for (r) in res:
        n = r[0]
    if mode == 'get':
        return n
    elif mode == 'add':
        n += 1
        db.execute("update ids set id = " + str(n) + " where groupid = " + str(groupid) + ";")

def get_report(userid, mode):
    dn = get_times('mm')[0]
    ds = get_times('mm')[1]
    rows = db.execute("SELECT TO_JSON(a) FROM (select \"" + str(userid) + "\" as \"text\" from reads where date >= '" + str(ds) + "' and date <= '" + str(dn) + "' order by date) a;")
    list_of_dicts = [{key: value for (key, value) in row["to_json"].items()} for row in rows]
    if mode == 'global':
        _dict = []
        #[{'text': None}, {'text': None}, {'text': None}, {'text': None}, {'text': None}, {'text': None}, {'text': 1}]
        for l in list_of_dicts:
            if l['text'] == 1:
                _dict.append({'text': "X"})
            else:
                _dict.append({'text': ""})
        return _dict
    elif mode == 'personal':
        le = len(list_of_dicts)
        r = 0
        for l in list_of_dicts:
            if l['text'] == 1:
                r += 1
            else:
                pass
        return(round(100*float(r)/le, 2))
