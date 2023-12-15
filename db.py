import sqlite3
import pandas as pd

class db:
    def __init__(self):
        self.conn = sqlite3.connect('db/utopia.db')
        self.cur = self.conn.cursor()

    def check_table(self, tablename):
        sql = f'SELECT * FROM sqlite_master WHERE type="table" AND name="{tablename}"'
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        
        if rows:
            return True
        else:
            return False
    
    def change_df(self, tablename):
        self.cur.execute(f'SELECT * FROM {tablename}')
        rows = self.cur.fetchall()
        cols = [column[0] for column in self.cur.description]
        df = pd.DataFrame.from_records(data=rows, columns=cols)    
        return df

    def close(self):
        self.cur.close()
        self.conn.commit()
        self.conn.close()