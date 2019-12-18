import sqlite3
from sqlite3 import Error

DB_FILE = "my.db"

def create_db(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(create_table_sql):
    conn=create_connection(DB_FILE)
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_user(name, email, username, password):
    conn=create_connection(DB_FILE)
    values = (name, email, username, password)
    print(values)
    sql = '''INSERT INTO users(name, email, username, password) VALUES(?, ?, ?, ?)'''
    cur = conn.cursor()
    print(sql)
    cur.execute(sql, values)
    conn.commit()
    return cur.lastrowid

def create_an_article(title, body, author):
    conn=create_connection(DB_FILE)
    values = (title, body, author)
    sql = '''INSERT INTO articles(title, body, author) VALUES(?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    return cur.lastrowid

def update_an_article(title, body, id):
    conn=create_connection(DB_FILE)
    values = (title, body, id)
    sql = '''UPDATE articles SET title=?, body=? WHERE id=?'''
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()

def get_all_users():
    conn=create_connection(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    return rows

def get_user(username):
    conn=create_connection(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    rows = cur.fetchone()
    return rows

def get_all_articles():
    conn=create_connection(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM articles")
    rows = cur.fetchall()
    return rows

def get_an_article(id):
    conn=create_connection(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM articles WHERE id=?", (id,))
    row = cur.fetchone()
    return row

def delete_an_article(id):
    conn=create_connection(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM articles WHERE id=?", id)
    conn.commit()

def main():
    database = "my.db"
    create_db(database)
    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        name text NOT NULL,
                                        email text NOT NULL,
                                        username text NOT NULL,
                                        password text(100),
                                        register_date DATETIME DEFAULT CURRENT_TIMESTAMP
                                    ); """

    sql_create_articles_table = """CREATE TABLE IF NOT EXISTS articles (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    title text(200) NOT NULL,
                                    author text(100) NOT NULL,
                                    body text NOT NULL,
                                    current_date DATETIME DEFAULT CURRENT_TIMESTAMP
                                );"""
    # create a database connection
    #conn = create_connection(database)
    conn = True #print(conn)

    # create tables
    if conn is not None:
        # create projects table
        create_table(sql_create_users_table)

        # create tasks table
        create_table(sql_create_articles_table)
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()

    #print(create_user(conn, 'name2', 'email', 'username', 'password'))
    #print(get_all_articles())
    #print(create_an_article(conn, 'new_title', "tesxt test"*50, "Will Smith"))
    #update_an_article(conn, 'new_title', 'body', 2)
    #update_an_article(conn, 'new_title', 'body', 1)
    #update_an_article(conn, 'new_title', 'body', 3)
