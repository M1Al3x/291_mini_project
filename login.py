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
    );
    create table started_watching (
      sid		int,
      cid		char(4),
      mid		int,
      sdate		date,
      primary key (sid,cid,mid),
      foreign key (sid,cid) references sessions,
      foreign key (mid) references movies
    );''')
    connection.commit()
    return

def insert_values():
    global connection, cursor
    sql_file = open("prj-test.sql")
    sql_as_string = sql_file.read()
    cursor.executescript(sql_as_string)
    connection.commit()
    return

def login():
    global connection, cursor
    user_type = "undef"
    login_signup = input("Do you want to login or sign-up?(l/s): ")
    while login_signup.lower()!="l" and login_signup.lower()!="s":
        login_signup = input("Do you want to login or sign-up?(l/s): ")
    if login_signup.lower()=="l":
        username = input("Enter your username: ")
        cursor.execute("SELECT pwd FROM customers where cid = ?;", (username,))
        user_exists=cursor.fetchall()
        cursor.execute("SELECT pwd FROM editors where eid = ?;", (username,))
        editor_exists=cursor.fetchall()
        print(user_exists)
        print(editor_exists)
        if not user_exists and not editor_exists:
            print("Unfortunately there is no user with such username")
            while not user_exists and not editor_exists:
                username = input("Enter your username: ")
                cursor.execute("SELECT pwd FROM customers where cid = ?;", (username,))
                user_exists=cursor.fetchall()
                cursor.execute("SELECT pwd FROM editors where eid = ?;", (username,))
                editor_exists=cursor.fetchall()                
        password = input("Enter your password: ")
        if user_exists:
            if password == user_exists[0][0]:
                print("Congratulations! Successful input!")
            else:
                while password != user_exists[0][0]:
                    print("Sorry! Incorrect password!")
                    password = input("Enter your password: ")
                print("Congratulations! Successful input!")  
            user_type = "u"
        elif editor_exists:
            if password == editor_exists[0][0]:
                print("Congratulations! Successful input!")
            else:
                while password != user_exists[0][0]:
                    print("Sorry! Incorrect password!")
                    password = input("Enter your password: ")
                print("Congratulations! Successful input!")  
            user_type = "e"
        print("To exit program type 'exit' at any stage of the program. To logout - type 'logout'!")  
        return user_type, username 
    else:
        username = input("Enter your username: ")
        cursor.execute("SELECT pwd FROM customers where cid = ?;", (username,))
        user_exists=cursor.fetchall()
        cursor.execute("SELECT pwd FROM editors where eid = ?;", (username,))
        editor_exists=cursor.fetchall()
        if user_exists or editor_exists:
            while user_exists or editor_exists:
                print("Unfortunately this username is already taken.")
                username = input("Enter your username: ")
                cursor.execute("SELECT pwd FROM customers where cid = ?;", (username,))
                user_exists=cursor.fetchall()
                cursor.execute("SELECT pwd FROM editors where eid = ?;", (username,))
                editor_exists=cursor.fetchall()
        name = input("Enter your name: ")
        pwd = input("Enter your pwd: ")
        insert_user = '''
                            INSERT INTO customers(cid, name, pwd) VALUES
                                (?, ?, ?);
                        '''        
        print("Congratulations! Successful input!")  
        print("To exit program type 'exit' at any stage of the program. To logout - type 'logout'!")  
        cursor.execute(insert_user, (username, name, pwd,))
        connection.commit()
        return "u", username  

def start_session(cid, count):
    global connection, cursor
    current_date = time.strftime("%Y-%m-%d %H:%M:%S")
    sid = 1
    get_sid = 1
    while get_sid:
        cursor.execute("SELECT * FROM sessions where sid = ?;", (sid,))
        get_sid=cursor.fetchall()
        sid = sid + 1
    duration = None
    data = (sid, cid, current_date, duration)
    cursor.execute('INSERT INTO sessions (sid, cid, sdate, duration) VALUES (?,?,?,?);', data) 
    connection.commit()    
    return sid


def search_movie():
    global connection, cursor
    #ask the user for the keywords and add it to a list
    movies = search_by_key_words() 
    print("Movies by the given search: ")
    index = 0
    indexEd = 0
    i = "n"
    indexToCheck = -1
    while(i!="c"):
        if i=="n":
            while(index < len(movies) and index < indexEd + 5):
                print(str(index+1) + ". " + movies[index][0] + ", " + str(movies[index][1]) + " year, " + str(movies[index][2]) + " minutes")
                index = index + 1
        i = input("In order to view detailed information about movie enter its number. If you want to see next movies in the search, enter 'n'. If you want to serach another movie press s: ")
        if i=="s":
            movies = search_by_key_words() 
            print("Movies by the given search: ")
            index = 0
            indexEd = 0
            i = "n"
            indexToCheck = -1
        else:
            while indexEd < index:
                if i == str(indexEd+1):
                    indexToCheck = indexEd
                    i = "c"
                    break
                indexEd = indexEd + 1
    if i=="c":
        seeDetailedInfo("c100",movies[indexEd])
    connection.commit()
    return

def search_by_key_words():
    keywords = input("Enter keywords for searching movie: ")
    keywords_list = keywords.split()
    keywords_list_updated = ()
    for keyword in keywords_list:
        keyword = "%" + keyword + "%"
        keywords_list_updated = keywords_list_updated + (keyword,)
        keywords_list_updated = keywords_list_updated + (keyword,)
        keywords_list_updated = keywords_list_updated + (keyword,)
        keywords_list_updated = keywords_list_updated + (keyword,)
    select_string = '''Select m1.title, m1.year, m1.runtime,m1.mid, (
                     '''
    for index in range(len(keywords_list)):
        if index != len(keywords_list) - 1:
            select_string = select_string + '''(m1.title like ?  or m1.year like ? 
                                                or EXISTS
                                               (SELECT m2.mid
                                               from movies m2, casts c, moviePeople p 
                                               where m2.mid = c.mid 
                                               and p.pid = c.pid
                                               and m2.mid = m1.mid 
                                               and (p.name like ?
                                                     or c.role like ?)))
                                                +
                                            '''
        else:
            select_string = select_string + '''(m1.title like ?  or m1.year like ? 
                                               or EXISTS
                                               (SELECT m2.mid
                                               from movies m2, casts c, moviePeople p 
                                               where m2.mid = c.mid 
                                               and p.pid = c.pid
                                               and m2.mid = m1.mid 
                                               and (p.name like ?
                                                     or c.role like ?)))) as 'cntGrp'
                                               from movies m1
                                               where cntGrp>=1
                                               order by cntGrp DESC;  
                                            '''  
    cursor.execute(select_string, keywords_list_updated)
    movies = cursor.fetchall()
    return movies
    
def seeDetailedInfo(cid, movie):
    print("Detailed information for " + movie[0] + ", " + str(movie[1]) + " year, " + str(movie[2]) + " minutes")
    mid = movie[3]
    cursor.execute('''SELECT COUNT(DISTINCT w.cid)
                      from movies m, watch w
                      where m.mid = w.mid
                      and m.mid = ?
                      and w.duration*2>=m.runtime''', (mid,)) 
    watched_by = cursor.fetchone()
    print("The movie is watched by " + str(watched_by[0]) + " customers.")
    print("Cast: ")
    cursor.execute('''SELECT p.name, c.role, p.pid
                      from movies m, casts c, moviePeople p
                      where m.mid = c.mid
                      and c.pid = p.pid
                      and m.mid = ?''', (mid,))
    cast = cursor.fetchall()
    index = 0
    while(index < len(cast)):
        print(str(index+1) + ". " + cast[index][0] + " played " + str(cast[index][1]))
        index = index + 1
    inpMovie = ''
    while inpMovie != 'w':
        inpMovie = input("Do you want to subscribe on anyone? If yes, enter a number of cast member. If you want to start watching movie, enter 'w': ")
        index = 0
        subscr = False
        while(index < len(cast)):
            if(str(index+1) == inpMovie):
                cursor.execute('''Select * from follows where cid = ? and pid = ?;''', (cid,  cast[index][2]))
                is_followed = cursor.fetchall()
                print(is_followed)
                if not is_followed:
                    cursor.execute('''Insert into follows(cid, pid) Values (?, ?);''', (cid,  cast[index][2]))
                    print("Successfully subscribed")
                else:
                    print("Already subscribed")
                subscr = True
                break
            index = index + 1
        if subscr == False and inpMovie != 'w':
            print("Incorrect input")
    connection.commit()
    return

def display_watched_movies(sid, cid):
    while(1): 
        cursor.execute('''Select movies.title, movies.mid, started_watching.sdate, movies.runtime  from started_watching, movies where cid = ? and movies.mid = started_watching.mid and started_watching.sid = ?;''', (cid, sid,))
        print("Movies that you are watching right now: ")
        watching = cursor.fetchall()
        index = 0        
        while(index < len(watching)):
            print(str(index+1) + ". " + watching[index][0])
            index = index + 1 
        stopWatching = input("Do you want to stop watching movies? If so, enter a number that you would like to stop wtaching: ")
        while(index < len(watching)):
            if stopWatching == str(index+1):
                current_date = time.strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('''Insert into watch(sid, cid, mid, duration) Values (?, ?, ?, MIN(DATEDIFF(minute, ?, ?), ?));''', (sid, cid, watching[index][1], watching[index][2], current_date,watching[index][3] ))
                cursor.execute('''Delete from started_watching where cid = ? and mid = ? and sid = ?''', (cid,  watching[index][1], sid,))
                break
            index = index + 1
            if index == len(watching):
                print("You entered invalid index")
        
    
    
    

                                   
def main():
    global connection, cursor
    
    # connection and set up tables
    path = "./register.db"
    connect(path)
    define_tables()
    insert_values()
    search_movie()
    count = 1 # this is for unique session id
    
    #testing   
    
   
    
    connection.commit()
    connection.close()
if __name__ == "__main__":
    main()




                                        
                                        
                                  
