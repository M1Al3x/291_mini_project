import sqlite3
import time
import string

connection = None
cursor = None
current_session = None

def connect(path):
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return
   
def define_tables():
    global connection, cursor
    #  drop table if exists started_watching;
    cursor.executescript('''
    drop table if exists started_watching;
    drop table if exists start_session;
    
    PRAGMA foreign_keys = ON;
    
    create table started_watching (
      sid		int,
      cid		char(4),
      mid		int,
      sdate		datetime,
      primary key (sid,cid,mid),
      foreign key (sid,cid) references sessions,
      foreign key (mid) references movies
    );
    
    create table start_session (
      sid		int,
      startdate		datetime,
      primary key (sid)
    );''')
    connection.commit()
    return

def insert_values(file_name):
    global connection, cursor
    sql_file = open(file_name)
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
        username = username.lower()
        if len(username) > 4:
            print('please enter a correct username!\nyou will be returned to the homescreen now')
        cursor.execute("SELECT pwd FROM customers where lower(cid) = ?;", (username,))
        user_exists=cursor.fetchall()
        cursor.execute("SELECT pwd FROM editors where lower(eid) = ?;", (username,))
        editor_exists=cursor.fetchall()
        if not user_exists and not editor_exists:
            print("Unfortunately there is no user with such username")
            while not user_exists and not editor_exists:
                username = input("Enter your username: ")               
                cursor.execute("SELECT pwd FROM customers where lower(cid) = ?;", (username,))
                user_exists=cursor.fetchall()
                cursor.execute("SELECT pwd FROM editors where lower(eid) = ?;", (username,))
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
                while password != editor_exists[0][0]:
                    print("Sorry! Incorrect password!")
                    password = input("Enter your password: ")
                print("Congratulations! Successful input!")  
            user_type = "e" 
        return user_type, username 
    else:
        username = input("Enter your username: ")
        username = username.lower()
        while len(username)>4:
            print("\nUsername should contain maximum 4 characters!!!\n")
            username = input("Enter your username: ")
            username = username.lower()            
        cursor.execute("SELECT pwd FROM customers where lower(cid) = ?;", (username,))
        user_exists=cursor.fetchall()
        cursor.execute("SELECT pwd FROM editors where lower(eid) = ?;", (username,))
        editor_exists=cursor.fetchall()
        if user_exists or editor_exists:
            while user_exists or editor_exists:
                print("Unfortunately this username is already taken.")
                username = input("Enter your username: ")
                username = username.lower()
                cursor.execute("SELECT pwd FROM customers where lower(cid) = ?;", (username,))
                user_exists=cursor.fetchall()
                cursor.execute("SELECT pwd FROM editors where lower(eid) = ?;", (username,))
                editor_exists=cursor.fetchall()
        name = input("Enter your name: ")
        pwd = input("Enter your pwd: ")
        insert_user = '''
                            INSERT INTO customers(cid, name, pwd) VALUES
                                (?, ?, ?);
                        '''        
        print("\nCongratulations! Successful input!")  
        cursor.execute(insert_user, (username, name, pwd,))
        connection.commit()
        return "u", username  

def start_session(cid):
    global connection, cursor
    current_date = time.strftime("%Y-%m-%d")
    current_date_time = time.strftime("%Y-%m-%d %H:%M:%S")
    sid = 1
    get_sid = 1
    while get_sid:
        cursor.execute("SELECT * FROM sessions where sid = ?;", (sid,))
        get_sid=cursor.fetchall()
        if not get_sid:
            break
        sid = sid + 1
        
    # get all the customers 
    cursor.execute("SELECT cid FROM customers where cid = ?;", (cid,))
    get_cid =cursor.fetchall()
    if get_cid == []:
        print('the customer does not exist!')
        return
    
    duration = None
    data = (sid, cid, current_date, duration)
    cursor.execute('INSERT INTO sessions (sid, cid, sdate, duration) VALUES (?,?,?,?);', data) 
    data = (sid, current_date_time)
    cursor.execute('INSERT INTO start_session (sid, startdate) VALUES (?,?);', data)
    data = (sid, cid, current_date_time, duration)
    print("\nSuccessfuly started a session!")
    connection.commit()    
    return data

def end_session(sid, cid):
    global connection, cursor
    
    # end all movies watching currently
    cursor.execute('''Select movies.title, movies.mid, started_watching.sdate, movies.runtime  from started_watching, movies where cid = ? and movies.mid = started_watching.mid and started_watching.sid = ?;''', (cid, sid,))
    watching = cursor.fetchall()
    index = 0   
    current_date = time.strftime("%Y-%m-%d %H:%M:%S")
    
    
    while(index < len(watching)):
        cursor.execute('''Select * from watch where sid = ? and cid=? and mid=?;''', (sid,cid, watching[index][1],))
        check_session = cursor.fetchall()
        cursor.execute('''Delete from started_watching where cid = ? and mid = ? and sid = ?;''', (cid,  watching[index][1], sid,)) 
        cursor.execute('''Delete from watch where sid = ? and cid=? and mid=?;''', (sid,cid, watching[index][1],))
        if not check_session:  
            cursor.execute('''Insert into watch(sid, cid, mid, duration) Values (?, ?, ?, MIN((JulianDay(?) - JulianDay(?))*24*60, ?));''', (sid, cid, watching[index][1], current_date, watching[index][2], watching[index][3], ))
        else:
            cursor.execute('''Insert into watch(sid, cid, mid, duration) Values (?, ?, ?, MIN((JulianDay(?) - JulianDay(?))*24*60+?, ?));''', (sid, cid, watching[index][1], current_date, watching[index][2], check_session[0][3], watching[index][3], ))
             
        index = index + 1    
        
    # get all the duration of the movies watched in this session
    cursor.execute('select startdate from start_session where sid = ?;', (sid,))
    startdate = cursor.fetchall()
    startdate = startdate[0][0]
    cursor.execute('update sessions set duration = (JulianDay(?) - JulianDay(?))*24*60 where sid = ?;', (startdate, current_date, sid))
    cursor.execute('delete from start_session where sid = ?;', (sid,))
    connection.commit()    
    return

def search_movie(sid, cid):
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
        i = input("In order to view detailed information about movie enter its number.\nIf you want to see next movies in the search, enter 'n'. \nIf you want to serach another movie press s. \nif you want to return to homepage enter 'q': ")
        if i=="s":
            movies = search_by_key_words() 
            print("Movies by the given search: ")
            index = 0
            indexEd = 0
            i = "n"
            indexToCheck = -1
        if i == 'q':
            # end the loop
            print("you will be returned to the homepage!")
            return
        else:
            while indexEd < index:
                if i == str(indexEd+1):
                    indexToCheck = indexEd
                    i = "c"
                    break
                indexEd = indexEd + 1
        
    if i=="c":
        seeDetailedInfo(sid,cid,movies[indexEd])
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
    select_string = '''Select m1.title, m1.year, m1.runtime,m1.mid, (
                     '''
    for index in range(len(keywords_list)):
        if index != len(keywords_list) - 1:
            select_string = select_string + '''(m1.title like ? 
                                                or EXISTS
                                               (SELECT m2.mid
                                               from movies m2, casts c, moviePeople p 
                                               where m2.mid = c.mid 
                                               and p.pid = c.pid
                                               and m2.mid = m1.mid 
                                               and (lower(p.name) like ?
                                                     or lower(c.role) like ?)))
                                                +
                                            '''
        else:
            select_string = select_string + '''(m1.title like ? 
                                               or EXISTS
                                               (SELECT m2.mid
                                               from movies m2, casts c, moviePeople p 
                                               where m2.mid = c.mid 
                                               and p.pid = c.pid
                                               and m2.mid = m1.mid 
                                               and (lower(p.name) like ?
                                                     or lower(c.role) like ?)))) as 'cntGrp'
                                               from movies m1
                                               where cntGrp>=1
                                               order by cntGrp DESC;  
                                            '''  
    cursor.execute(select_string, keywords_list_updated)
    movies = cursor.fetchall()
    return movies
    
def seeDetailedInfo(sid, cid, movie):
    inpMovie = ''
    while inpMovie != 'w' and inpMovie != 'q':
        print("\n\nDetailed information for " + movie[0] + ", " + str(movie[1]) + " year, " + str(movie[2]) + " minutes")
        mid = movie[3]
        cursor.execute('''SELECT COUNT(DISTINCT w.cid)
                          from movies m, watch w
                          where m.mid = w.mid
                          and m.mid = ?
                          and w.duration*2>=m.runtime''', (mid,)) 
        watched_by = cursor.fetchone()
        print("\nThe movie is watched by " + str(watched_by[0]) + " customers.\n")
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
        print("\n")
        inpMovie = ''
        inpMovie = input("If you want to go back to main screen - enter 'q'. \nDo you want to subscribe on anyone? If yes, enter a number of cast member. \nIf you want to start watching movie, enter 'w':")
        index = 0
        subscr = False
        while(index < len(cast)):
            if(str(index+1) == inpMovie):
                cursor.execute('''Select * from follows where cid = ? and pid = ?;''', (cid,  cast[index][2]))
                is_followed = cursor.fetchall()
                if not is_followed:
                    cursor.execute('''Insert into follows(cid, pid) Values (?, ?);''', (cid,  cast[index][2]))
                    print("\nSuccessfully subscribed")
                else:
                    print("Already subscribed")
                subscr = True
                break
            index = index + 1
        if subscr == False and inpMovie != 'w':
            print("Incorrect input")
    current_date = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''Select * from started_watching where sid = ? and cid = ? and mid = ?;''', (sid, cid, mid,))
    check_add_movie = cursor.fetchall()
    if not check_add_movie:
        cursor.execute('''Insert into started_watching(sid, cid, mid, sdate) Values (?, ?, ?, ?);''', (sid, cid, mid, current_date,))    
        print("\nYou are watching a movie now!\n")
    else:
        print("\nYou are already watching this movie\n")
    connection.commit()
    return

def display_watched_movies(sid, cid):
    stopWatching = ""
    while stopWatching != "m":
        cursor.execute('''Select movies.title, movies.mid, started_watching.sdate, movies.runtime  from started_watching, movies where cid = ? and movies.mid = started_watching.mid and started_watching.sid = ?;''', (cid, sid,))
        print("\nMovies that you are watching right now:\n")
        watching = cursor.fetchall()
        index = 0        
        while(index < len(watching)):
            print(str(index+1) + ". " + watching[index][0])
            index = index + 1 
        stopWatching = input("Do you want to stop watching movies? If so, enter a number that you would like to stop watching. If you want to go to main menu - press m: ")
        stopWatching = stopWatching.lower()
        index = 0
        while(index < len(watching)):
            if stopWatching == str(index+1):
                current_date = time.strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('''Select * from watch where sid = ? and cid=? and mid=?;''', (sid,cid, watching[index][1],))
                check_session = cursor.fetchall()
                cursor.execute('''Delete from watch where sid = ? and cid=? and mid=?;''', (sid,cid, watching[index][1],))
                cursor.execute('''Delete from started_watching where cid = ? and mid = ? and sid = ?;''', (cid,  watching[index][1], sid,)) 
                if not check_session:  
                    cursor.execute('''Insert into watch(sid, cid, mid, duration) Values (?, ?, ?, MIN((JulianDay(?) - JulianDay(?))*24*60, ?));''', (sid, cid, watching[index][1], current_date, watching[index][2], watching[index][3], ))
                else:
                    cursor.execute('''Insert into watch(sid, cid, mid, duration) Values (?, ?, ?, MIN((JulianDay(?) - JulianDay(?))*24*60+?, ?));''', (sid, cid, watching[index][1], current_date, watching[index][2], check_session[0][3], watching[index][3], ))                
                break
            index = index + 1
        if index == len(watching):
            print("You entered invalid index")            
        
            
def add_movie():
    global connection, cursor
    # define the varibles first
    movie_id = input('please enter a unique movie id: ')
    
    if movie_id.isdigit():
        movie_id = int(movie_id)
    else:
        print('please enter a integer, you will be returned to home screen')
        return
    
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
        title = input('please enter the title: ')
        year = input('please enter the production year: ')
        if year.isdigit():
            year = int(year)
        else:
            print('please enter a integer, you will be returned to home screen')
            return            
        
        runtime = input('please enter the runtime: ')
        
        if runtime.isdigit():
            runtime = int(runtime)
        else:
            print('please enter a integer, you will be returned to home screen')
            return                        
        
        data = (movie_id, title, year, runtime)
        cursor.execute('INSERT INTO movies (mid, title, year, runtime) VALUES (?,?,?,?);', data)
        cursor.execute("select * from movies where mid=? ;", (movie_id,))
        movies = cursor.fetchall()
        print("you have added succefully! this is what is added:", movies)
        
        continue_program = True
        while continue_program:
            cast_id = input("please enter the cast members id or to quit adding cast member enter 'q': ").lower()
            if cast_id != 'q':
                if 4 >= len(cast_id):
                    # find all cast members
                    cursor.execute('SELECT name, birthYear FROM moviePeople WHERE pid = ?;', (cast_id,))  
                    name_birth = cursor.fetchall()
             
                    if name_birth == []:
                        # the cast memeber does not exist
                        print("the cast memeber does not exist, please add them")
                        pid = cast_id
                        name = input("please enter the name to add to: ").lower()
                        birthyear = int(input('please enter the birth year: '))
                        if birthyear.isdigit():
                            birthyear = int(birthyear)
                            data = (pid, name, birthyear)
                            cursor.execute('INSERT INTO moviePeople (pid, name, birthYear) VALUES (?,?,?);', data) 
                            connection.commit()
                            print("you have added succefully!")                              
                        else:
                            print('please eneter a year number, you will be returned to the main page')           
                        
                    else:
                        cursor.execute('SELECT pid FROM casts WHERE pid = ? and mid = ?;', (cast_id, movie_id,))  
                        casts = cursor.fetchall()   
                        
                        if casts == []:
                            name_birth = name_birth[0]
                            # the cast memeber exists
                            name = name_birth[0]
                            birthyear = name_birth[1]
                            print("the name is {}, and the birthyear is {} is this ".format(name, birthyear))
                            not_reject = input("confim that this is the cast member to add a role to, type yes or no: ").lower()
                            if not_reject == 'yes':
                                # add role to the cast memeber
                                pid = cast_id
                                role = input("please enter the role to add to: ").lower()
                                mid = movie_id
                                data = (mid, pid, role)
                                cursor.execute('INSERT INTO casts (mid, pid, role) VALUES (?,?,?);', data) 
                                print("you have added succefully!")
                            elif not_reject == 'no':
                                print('you have rejected the cast memeber, now returning to the main page.')
                            else:
                                print('please enter a valid choice')
                        else:
                            print('this memeber is already playing a role in this movie please pick a different one')
                else:
                    print('please enter a pid that is less than 4 charcters')
            else:
                connection.commit()
                return
        
    else:
        # the id entered it not unique go back to main screen
        print("the enterd movie id is not unique it already exists")
        connection.commit()
        return
     
    connection.commit()
    return  

def update_recommendation():
    global connection, cursor
    selection = input('type 1 for monthly report, 2 for annual, 3 for all time report: ')
    # see the selection
    current_date = time.strftime("%Y-%m-%d")
    
    if selection == '1':
        cursor.execute('''select w1.mid, w2.mid, count(Distinct w1.cid) from watch w1, watch w2, sessions s1, sessions s2, movies m1, movies m2
                          where w1.mid != w2.mid 
                          and w1.cid = w2.cid
                          and s1.sid = w1.sid
                          and m1.mid = w1.mid
                          and m2.mid = w2.mid
                          and s2.sid = w2.sid
                          and w1.duration*2 >= m1.runtime
                          and w2.duration*2 >= m2.runtime
                          and 30 >= (JulianDay(?) - JulianDay(s1.sdate))
                          and 30 >= (JulianDay(?) - JulianDay(s2.sdate))
                          group by w1.mid, w2.mid
                          order by count(Distinct w1.cid) desc;
                          ''', (current_date, current_date,)) 
        
    elif selection == '2':
        cursor.execute('''select w1.mid, w2.mid, count(Distinct w1.cid) from watch w1, watch w2, sessions s1, sessions s2, movies m1, movies m2
                          where w1.mid <> w2.mid 
                          and w1.cid = w2.cid
                          and s1.sid = w1.sid
                          and m1.mid = w1.mid
                          and w1.duration*2 >= m1.runtime
                          and m2.mid = w2.mid
                          and s2.sid = w2.sid
                          and w2.duration*2 >= m2.runtime
                          and 365 >= (JulianDay(?) - JulianDay(s1.sdate))
                          and 365 >= (JulianDay(?) - JulianDay(s2.sdate))
                          group by w1.mid, w2.mid
                          order by count(Distinct w1.cid) desc;
                          ''', (current_date, current_date,))  
    elif selection == '3':
        cursor.execute('''select w1.mid, w2.mid, count(Distinct w1.cid) from watch w1, watch w2, movies m1, movies m2
                          where w1.mid <> w2.mid 
                          and w1.cid = w2.cid
                          and m1.mid = w1.mid
                          and w1.duration*2 >= m1.runtime
                          and m2.mid = w2.mid
                          and w2.duration*2 >= m2.runtime
                          group by w1.mid, w2.mid
                          order by count(Distinct w1.cid) desc;''')  
    else:
        print('print this is not a valid choice, you will be returned to the main page')
        return
    
    # see what pairs are in the reconmendations and which ones are not in
    all_pairs = cursor.fetchall()

    display_pairs = []
    for pair in all_pairs:
        mid1 = pair[0]
        mid2 = pair[1]
        cursor.execute('select watched, recommended, score from recommendations where watched = ? and recommended = ?;', (mid1, mid2,))
        temp_pair = cursor.fetchall()
        if temp_pair != []:
            temp_pair = temp_pair[0]
            display_pairs.append([mid1, mid2, pair[2], 'in', temp_pair[2]])
        else:
            display_pairs.append([mid1, mid2, pair[2], 'not in', None])    
    
    # display all the pairs
    print('pair num: mid of movie1 | mid of movie2 | count | indicator | score')
    index = 0
    while index < len(display_pairs):
        print('pair {:<3}: {:<13} | {:<13} | {:<5} | {:<9} | {}'.format(index, display_pairs[index][0], display_pairs[index][1], display_pairs[index][2], display_pairs[index][3], display_pairs[index][4]))
        index = index +1
    
    countinue_program = True
    while countinue_program:
        pair_number = input('1.to select a pair enter the pair number.\n2.to quit update recommendations enter q.\nplease select an option: ')
        if pair_number == 'q':
            countinue_program = False
        
        else:
            if pair_number.isdigit():
                if int(pair_number) >= len(display_pairs) or int(pair_number) < 0:
                    # check to see if it is in the range or not
                    print('please eneter a valid option!')
                else:
                    pair_number = int(pair_number)
                    if display_pairs[pair_number][3] == 'not in':
                        option = input('this pair is not in the recommendations, add or not add(y/n): ')
                        if option.lower() == 'y':
                            score = input('please enter the score to be added to this pair for recommendations: ')
                            testing = False
                            try:
                                float(score)
                                testing = True
                            except ValueError:
                                    testing =  False
                            if testing:
                                score = float(score)                            
                                cursor.execute('INSERT INTO recommendations (watched, recommended, score) VALUES (?,?,?);', (display_pairs[pair_number][0],display_pairs[pair_number][1], score,))
                                print('added successful!')
                            else:
                                print('pleaseeeee enter a decimal!!!')                            
                    else:   # it is in the reconmmendations 
                        option = input('this pair is in the recommendations, delete or return and not delete or update score (y/n/u): ')
                        if option.lower() == 'y':
                            cursor.execute('delete from recommendations where watched = ? and recommended = ?;', (display_pairs[pair_number][0], display_pairs[pair_number][1],))
                            print('deleted successful!')
                        if option.lower() == 'u':
                            score = input('please enter the new score: ')
                            testing = False
                            try:
                                float(score)
                                testing = True
                            except ValueError:
                                    testing =  False
                            if testing:
                                score = float(score)
                                cursor.execute('update recommendations set score = ? where watched = ? and recommended = ?;', (score, display_pairs[pair_number][0], display_pairs[pair_number][1],))
                                print('updated the score successful!')  
                            else:
                                print('pleaseeeee enter a decimal!!!')
            else:
                print('please eneter a valid option!')
        connection.commit()
    return

def control():
    continue_program = True
    while continue_program:
        print('welcome to the program please login')
        option = input("To exit program type 'exit'. to login type anything and we will take you to log in!: ")
        if option.lower() == 'exit':
            continue_program = False
            return

        user_type, cid = login()
        session_data = None
        continue_login = True
        while continue_login:
            if user_type == 'e':
                # editor account
                option = input("\n\nyou are loged into a editor account, to add a movie or cast member enter 1\nto update a recommendation enter 2\nto logout - type 'logout'\nto exit type 'exit'\nenter your choice: ")
                if option == '1':
                    add_movie()
                elif option == '2':
                    update_recommendation()
                elif option.lower() == 'logout':
                    continue_login = False
                elif option.lower() == 'exit':
                    continue_login = False
                    continue_program = False
                    print('thank you for user the program you will be exited and logged out!!')
                else:
                    print('please enter a valid choice')
            else:
                # customer account
                temp_str_list = ['\nto start a session type 1', "\nto search for movies type 2 \nto end watching a movie type 3 \nto end the session type 4\nto logout - type 'logout\nto exit type 'exit'\nenter your choice: "]
                if session_data == None:
                    option = input('\nyou are loged into a customer account'+temp_str_list[0]+temp_str_list[1])
                else:
                    option = input('\nyou are loged into a customer account and you started a session!!!\n\n'+temp_str_list[1])
                
                if option.lower() == 'exit':
                    continue_login = False
                    continue_program = False
                    if session_data != None:
                        end_session(session_data[0], session_data[1])
                    print('thank you for user the program you will be exited and logged out!!')                
                elif session_data == None and (option == '2' or option == '3' or option == '4'):
                    print('please start a session before doing thease operations')                
                else:
                    if option == '1':
                        if session_data != None:
                            print('you currently have a session on going please select another operation!')
                        else:
                            session_data = start_session(cid)
                    elif option == '2':
                        sid = session_data[0]
                        search_movie(sid, cid)
                    elif option == '3':
                        display_watched_movies(sid, cid)
                    elif option == '4':
                        end_session(session_data[0], session_data[1])
                        session_data = None
                    elif option.lower() == 'logout':
                        print('you will be logged out, the session will be ended automatically!')
                        if session_data != None:
                            end_session(session_data[0], session_data[1])                        
                        continue_login = False
                    elif option.lower() == 'exit':
                        continue_login = False
                        continue_program = False
                        end_session(session_data[0], session_data[1])
                        print('thank you for user the program you will be exited and logged out!!')                
                    else:
                        print('please enter a valid choice')
            
                         
def main():
    global connection, cursor
    # connection and set up tables
    data_base_name = input('please enter the data base name: ')
    path = "./{}".format(data_base_name)
    # path = "./register.db"
    connect(path)
    define_tables()
    # insert_values("prj-test.sql")
    
    control()
    
    
    connection.commit()
    connection.close()
if __name__ == "__main__":
    main()
