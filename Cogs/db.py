import sqlite3
import pandas as pd
import os

def connect(filename = './db/utopia.db'):
    conn = sqlite3.connect(filename)
    cur = conn.cursor()
    return conn, cur
    
def check_table(cur, tablename):
    sql = f'SELECT * FROM sqlite_master WHERE type="table" AND name="{tablename}"'
    cur.execute(sql)
    rows = cur.fetchall()
    
    if rows:
        return True
    else:
        return False

def change_df(cur, tablename):
    cur.execute(f'SELECT * FROM {tablename}')
    rows = cur.fetchall()
    cols = [column[0] for column in cur.description]
    df = pd.DataFrame.from_records(data=rows, columns=cols)    
    return df

def db_close(conn, cur):
    cur.close()
    conn.commit()
    conn.close()
    
conn, cur = connect()