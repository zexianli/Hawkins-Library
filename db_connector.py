import MySQLdb as mariadb
from db_credentials import host, user, passwd, db

def connect_to_database(host = host, user = user, passwd = passwd, db = db) :
    db_connection = mariadb.connect(host, user, passwd, db)
    return db_connection

def execute_query(db_connection = None, query = None, query_params = ()):
    if db_connection is None:
        print("No connection to databse")
        return None
    
    if query is None or len(query.strip()) == 0:
        print("Query is empty")
        return None

    print("Executing %s with %s" % (query, query_params))
    cursor = db_connection.cursor()
    cursor.execute(query, query_params)
    db_connection.commit()
    return cursor
