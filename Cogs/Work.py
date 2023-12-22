import discord
from discord.ext import commands
import pandas as pd
import sqlite3
import os
import asyncio

# sqlite func
def connect(filename = './db/utopia.db'):
    conn = sqlite3.connect(os.path.abspath(filename))
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

def change_df(conn, tablename):
    df = pd.read_sql(f'SELECT * FROM {tablename}', conn, index_col=None)    
    return df

def db_close(conn, cur):
    cur.close()
    conn.commit()
    conn.close()

def create_table_user(conn, cur, tablename='works'):
    if not check_table(cur, tablename):
        sql = "PRAGMA foreign_keys"
        cur.execute(sql)
        conn.commit()
        sql = f'CREATE TABLE {tablename} (userid INTEGER NOT NULL, name TEXT NOT NULL, count INTEGER, first_work TEXT, last_work TEXT, last_quit, constraint work_FK FOREIGN KEY (userid, name) REFERENCES users(userid, name) )'
        cur.execute(sql)
        conn.commit()

class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.table_name = 'works'
        conn, cur = connect()
        create_table_user(conn, cur, self.table_name)
        self.df = change_df(conn, self.table_name)
        db_close(conn, cur)
        
async def setup(bot):
    await bot.add_cog(Work(bot))