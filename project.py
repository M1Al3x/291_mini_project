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

def add_movie():
    global connection, cursor
    # define the varibles first
    option = input("to add a movie enter movie, to add a cast memeber enter cast:")
    if option.lower() == 'movie':
        movie_id = input('please enter a unique movie id: ')
        
        # find all the movie id's
        cursor.execute("select mid from movies;")
        all_mid = cursor.fetchall()
        i = 0
        not_found = True
        while i < len(all_mid) and not_found:
            if all_mid[i][0] == movie_id:
                not_found = False
            i = i+1
            
        if not_found:
            title = input('please enter the movie id')
            year = int(input('please enter the production year: '))
            runtime = int(input('please enter the runtime: '))
            
            data = (movie_id, title, year, runtime)
            cursor.execute('INSERT INTO movies (mid, title, year, runtime) VALUES (?,?,?,?);', data)             
        else:
            # the id entered it not unique go back to main screen
            print("the enterd movie id is not unique it already exists")
            return
        
    elif option.lower() == 'cast':
        cast_id = (int(input('please enter the cast members id: ')).lower(),)
        # find all cast members
        cursor.execute('SELECT pid FROM moviePeople WHERE pid = ?;', cast_id)  
        name_birth = cursor.fetchone()[0]
        if name_birth == []:
            # the cast memeber does not exist
            print("the cast memeber does not exist, please add them")
            pid = cast_id
            name = input("please enter the name to add to: ").lower()
            birthyear = int(input('please enter the birth year: '))
            data = (pid, name, birthyear)
            cursor.execute('INSERT INTO moviePeople (pid, name, birthYear) VALUES (?,?,?);', data) 
            print("you have added succefully!")            
            
        else:
            # the cast memeber exists
            name = name_birth[0]
            birthyear = name_birth[1]
            print("the name is {}, and the birthyear is {} is this ".format(name, birthyear))
            not_reject = input("confim that this is the cast member to add a role to, type yes or no: ").lower()
            if not_reject == 'yes':
                # add role to the cast memeber
                pid = cast_id
                role = input("please enter the role to add to: ").lower()
                mid = int(input('please enter the mid of the movie: '))
                data = (mid, pid, role)
                cursor.execute('INSERT INTO casts (mid, pid, role) VALUES (?,?,?);', data) 
                print("you have added succefully!")
            elif not_reject == 'no':
                print('you have rejected the cast memeber, now returning to the main page.')
            else:
                print('please enter a valid choice')
                
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
