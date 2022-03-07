import sqlite3
import time
import string

connection = None
cursor = None

def connect(path):
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return
   
def define_tables():
    global connection, cursor
    cursor.executescript('''
    drop table if exists editors;
    drop table if exists follows;
    drop table if exists watch;
    drop table if exists sessions;
    drop table if exists customers;
    drop table if exists recommendations;
    drop table if exists casts;
    drop table if exists movies;
    drop table if exists moviePeople;
    
    PRAGMA foreign_keys = ON;
    
    create table moviePeople (
      pid		char(4),
      name		text,
      birthYear	int,
      primary key (pid)
    );
    create table movies (
      mid		int,
      title		text,
      year		int,
      runtime	int,
      primary key (mid)
    );
    create table casts (
      mid		int,
      pid		char(4),
      role		text,
      primary key (mid,pid),
      foreign key (mid) references movies,
      foreign key (pid) references moviePeople
    );
    create table recommendations (
      watched	int,
      recommended	int,
      score		float,
      primary key (watched,recommended),
      foreign key (watched) references movies,
      foreign key (recommended) references movies
    );
    create table customers (
      cid		char(4),
      name		text,
      pwd		text,
      primary key (cid)
    );
    create table sessions (
      sid		int,
      cid		char(4),
      sdate		date,
      duration	int,
      primary key (sid,cid),
      foreign key (cid) references customers
            on delete cascade
    );
    create table watch (
      sid		int,
      cid		char(4),
      mid		int,
      duration	int,
      primary key (sid,cid,mid),
      foreign key (sid,cid) references sessions,
      foreign key (mid) references movies
    );
    create table follows (
      cid		char(4),
      pid		char(4),
      primary key (cid,pid),
      foreign key (cid) references customers,
      foreign key (pid) references moviePeople
    );
    create table editors (
      eid		char(4),
      pwd		text,
      primary key (eid)
    );''')
    connection.commit()
    return

def start_session(cid, count):
    global connection, cursor
    current_date = time.strftime("%Y-%m-%d %H:%M:%S")
    
    sid = count+1
    duration = None
    data = (sid, cid, current_date, duration)
    cursor.execute('INSERT INTO sessions (sid, cid, sdate, duration) VALUES (?,?,?,?);', data) 
    connection.commit()    
    return sid

def search_movie():
    global connection, cursor
    #ask the user for the keywords and add it to a list
    num_keywords = int(input('what is the number of key words you want to input?'))
    i = 0
    keywords = []
    while i < num_keywords:
        keyword = input("please enter the {} keyword: ".format(i+1))
        keywords.append(keyword)
    
    
    connection.commit()
    return
                                   
def main():
    global connection, cursor
    
    # connection and set up tables
    path = "./register.db"
    connect(path)
    define_tables()
    count = 1 # this is for unique session id
    
    #testing   
    
   
    
    connection.commit()
    connection.close()
main()
