from discord.ext import commands
import pandas as pd
import sqlite3
import os

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

def create_table_user(conn, cur, tablename='user'):
    if not check_table(cur, tablename):
        sql = f'CREATE TABLE {tablename} (userid INTEGER NOT NULL, name TEXT NOT NULL, age INTEGER, gender VARCHAR(1), constraint user_PK PRIMARY KEY (userid, name) )'
        cur.execute(sql)
        conn.commit()

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn, cur = connect()
        create_table_user(conn, cur)
        self.df = change_df(cur, tablename='user')
        db_close(conn, cur)
        
    @commands.command(name='역할')
    async def role(self, ctx):
        await ctx.send('testing')
        return
        
async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))