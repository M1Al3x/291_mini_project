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
                    password = input("Enter your password: ")
                print("Congratulations! Successful input!")  
            user_type = "u"
        elif editor_exists:
            if password == editor_exists[0][0]:
                print("Congratulations! Successful input!")
            else:
                while password != user_exists[0][0]:
                    password = input("Enter your password: ")
                print("Congratulations! Successful input!")  
            user_type = "e"                
        return user_type, username 
    else:
        username = input("Enter your username: ")
        cursor.execute("SELECT pwd FROM customers where cid = ?;", (username,))
        user_exists=cursor.fetchall()
        cursor.execute("SELECT pwd FROM editors where eid = ?;", (username,))
        editor_exists=cursor.fetchall()
        if user_exists or editor_exists:
            print("Unfortunately this username is already taken.")
            while user_exists or editor_exists:
                username = input("Enter your username: ")
                cursor.execute("SELECT pwd FROM customers where cid = ?;", (username,))
                user_exists=cursor.fetchall()
                cursor.execute("SELECT pwd FROM editors where eid = ?;", (username,))
                editor_exists=cursor.fetchall()
        name = input("Enter your name: ")
        pwd = input("Enter your pwd: ")
        insert_user = '''
                            INSERT INTO customers(cid, name, pwd) VALUES
                                (?, '?, ?);
                        '''        
        cursor.execute(insert_user, (username, name, pwd,))
        connection.commit()
        return "u", username       
if __name__ == "__main__":
    main()