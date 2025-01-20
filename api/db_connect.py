import psycopg2

def connect():
    conn = None
    print("Connecting to PostgreSQL server...")
    try:
        conn = psycopg2.connect(
            host='db',
            dbname='dance_motion_db',
            user='brian',
            password='password',
            port = 5432)
        print("Connection Successful")
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        # print(cursor.fetchone())
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if conn is not None:
            conn.close()
            print("Connection Closed")

def close_connection(conn):
    '''
    Closes a psycopg2 connection
    '''
    conn.cursor().close()
    conn.close()