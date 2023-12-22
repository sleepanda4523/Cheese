import discord
from discord.ext import commands
import pandas as pd
import sqlite3
import os
import asyncio
import datetime

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
        sql = f'CREATE TABLE {tablename} (userid INTEGER NOT NULL, name TEXT NOT NULL, count INTEGER, check_a INTEGER, first_work TEXT, last_work TEXT, last_quit TEXT, constraint work_FK FOREIGN KEY (userid, name) REFERENCES users(userid, name) )'
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

    @commands.command(name='출석')
    async def attendance(self, ctx, name:discord.Member=None):
        if name is None:
            name = ctx.author

        userid = name.id
        nickname = name.nick if name.nick else name.name
        conn, cur = connect()
        sql = f'SELECT EXISTS ( SELECT * FROM users WHERE userid = {userid} );'
        cur.execute(sql)
        if cur.fetchall()[0][0] == 0:
            embed = discord.Embed(title="에러", description="등록된 유저가 없습니다. \n `$역할` 명령어를 사용해주세요!", color=0xFE2E2E)
            return await ctx.send(embed=embed)
        else:
            # name update
            sql = f'SELECT name FROM users WHERE userid = {userid}'
            cur.execute(sql)
            if str(cur.fetchall()[0][0]) != nickname:
                sql = f'UPDATE users SET name="{nickname}" WHERE userid = {userid}'
                cur.execute(sql)
                conn.commit()
            # check works
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = f'SELECT EXISTS ( SELECT * FROM {self.table_name} WHERE userid = {userid} );'
            cur.execute(sql)
            count = -1
            if cur.fetchall()[0][0] == 0:
                cur.execute(f'INSERT INTO {self.table_name} VALUES(?,?,?,?,?,?,NULL);', (userid, nickname, 1, 1, now, now))
                conn.commit()
                count = 1
            else :
                sql = f'SELECT check_a, count FROM {self.table_name} WHERE userid = {userid}'
                cur.execute(sql)
                result = cur.fetchall()[0]
                chk = result[0]
                count = result[1]
                if chk == 1:
                    embed = discord.Embed(title="확인", description="저번 출근 이후 퇴근을 안눌렀어요. \n 다음에는 꼭 퇴근도 눌러주세요.", color=0xFACC2E)
                    msg = await ctx.send(embed=embed)
                    await asyncio.sleep(3)
                sql = f'UPDATE {self.table_name} SET check_a=1, count={count+1}, last_work="{now}" WHERE userid = {userid}'
                cur.execute(sql)
                conn.commit()
                embed = discord.Embed(title="출석 완료", description=f"{name.mention} 출석 완료. \n 현재 출석 횟수 : {count+1} ", color=0x00FFFF)
                return await msg.edit(embed=embed)
            embed = discord.Embed(title="출석 완료", description=f"{name.mention} 출석 완료. \n 현재 출석 횟수 : {count} ", color=0x00FFFF)
            return await ctx.send(embed=embed)
                
        
async def setup(bot):
    await bot.add_cog(Work(bot))