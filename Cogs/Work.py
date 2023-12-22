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

    @commands.command(name='출근')
    async def attendance(self, ctx, name:discord.Member=None):
        if name is None:
            name = ctx.author

        userid = name.id
        nickname = name.nick if name.nick else name.name
        conn, cur = connect()
        sql = f'SELECT EXISTS ( SELECT * FROM users WHERE userid = {userid} );'
        cur.execute(sql)
        if cur.fetchall()[0][0] == 0:
            db_close(conn, cur)
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
            db_close(conn, cur)
            embed = discord.Embed(title="출석 완료", description=f"{name.mention} 출석 완료. \n 현재 출석 횟수 : {count} ", color=0x00FFFF)
            return await ctx.send(embed=embed)
    
    @commands.command(name='퇴근')
    async def leave_work(self, ctx, name:discord.Member=None):
        if name is None:
            name = ctx.author
            
        userid = name.id
        nickname = name.nick if name.nick else name.name
        conn, cur = connect()
        sql = f'SELECT EXISTS ( SELECT * FROM users WHERE userid = {userid} );'
        cur.execute(sql)
        if cur.fetchall()[0][0] == 0:
            db_close(conn, cur)
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
            sql = f'SELECT EXISTS ( SELECT * FROM {self.table_name} WHERE userid = {userid} );'
            cur.execute(sql)
            if cur.fetchall()[0][0] == 0:
                db_close(conn, cur)
                embed = discord.Embed(title="에러", description="출근 기록이 없습니다. \n `$출근` 명령어를 먼저 사용해주세요!", color=0xFE2E2E)
                return await ctx.send(embed=embed)
            sql = f'SELECT check_a FROM {self.table_name} WHERE userid = {userid}'
            cur.execute(sql)
            if int(cur.fetchall()[0][0]) == 0:
                db_close(conn, cur)
                embed = discord.Embed(title="에러", description="출근 기록이 없습니다. \n `$출근` 명령어를 먼저 사용해주세요!", color=0xFE2E2E)
                return await ctx.send(embed=embed)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = f'UPDATE {self.table_name} SET check_a=0,  last_quit="{now}" WHERE userid = {userid}'
            cur.execute(sql)
            conn.commit()
            db_close(conn, cur)
            embed = discord.Embed(title="퇴근 완료", description=f"{name.mention} 퇴근 완료. ", color=0x00FFFF)
            return await ctx.send(embed=embed)
            
    @commands.command(name='기록삭제')
    async def delete_work(self, ctx, name:discord.Member=None):
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
        # name update
        sql = f'SELECT name FROM users WHERE userid = {userid}'
        cur.execute(sql)
        if str(cur.fetchall()[0][0]) != nickname:
            sql = f'UPDATE users SET name="{nickname}" WHERE userid = {userid}'
            cur.execute(sql)
            conn.commit()
        sql = f'SELECT EXISTS ( SELECT * FROM {self.table_name} WHERE userid = {userid} );'
        cur.execute(sql)
        if cur.fetchall()[0][0] == 0:
            embed = discord.Embed(title="에러", description="출퇴근 기록이 없습니다.", color=0xFE2E2E)
            return await ctx.send(embed=embed)
        else :
            embed = discord.Embed(title="확인", description=f"정말 {name.mention} 유저의 출퇴근 기록을 삭제하실껀가요?\n (아래 이모지를 선택해주세요!)", color=0xFACC2E)
            check_msg = await ctx.send(embed=embed)
            await check_msg.add_reaction("⭕")
            await check_msg.add_reaction("❌")
            
            def check(reaction, user):
                return user == ctx.message.author and reaction.message.channel == ctx.message.channel and reaction.message.id == check_msg.id
            
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                embed = discord.Embed(title="에러", description=f"시간 초과. {ctx.author}님 다시 시도해주세요.", color=0xFE2E2E)
                return await ctx.send(embed=embed)
            else:
                if str(reaction.emoji) == '⭕':
                    sql = f'DELETE FROM {self.table_name} WHERE userid = {userid}'
                    cur.execute(sql)
                    conn.commit()
                    db_close(conn, cur)
                    await check_msg.clear_reactions()
                    embed = discord.Embed(title="출퇴근 기록 삭제 완료", description=f"{name.mention}유저의 출퇴근 기록을 삭제하였습니다!", color=0x00FFFF)
                    return await check_msg.edit(embed=embed)
                elif str(reaction.emoji) == '❌':
                    db_close(conn, cur)
                    await check_msg.clear_reactions()
                    embed = discord.Embed(title="출퇴근 기록 삭제 취소", description=f"해당 기능을 취소하셨어요..!", color=0x00FFFF)
                    return await check_msg.edit(embed=embed)
        return
async def setup(bot):
    await bot.add_cog(Work(bot))