import discord
from discord.ext import commands
import pandas as pd
import sqlite3
import os

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

def create_table_user(conn, cur, tablename='users'):
    if not check_table(cur, tablename):
        sql = f'CREATE TABLE {tablename} (userid INTEGER NOT NULL, name TEXT NOT NULL, age INTEGER, gender VARCHAR(1), constraint user_PK PRIMARY KEY (userid, name) )'
        cur.execute(sql)
        conn.commit()

# discord command
class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.table_name = 'users'
        conn, cur = connect()
        create_table_user(conn, cur, self.table_name)
        self.df = change_df(conn, self.table_name)
        db_close(conn, cur)
        
    @commands.command(name='역할')
    async def role(self, ctx, name:discord.Member = None, age:int = None, gender:str = None):
        #chack input
        if name == None or age == None or gender == None:
            embed = discord.Embed(title="경고", description="인자 값이 부족합니다. \n `$역할 [현재 닉네임] [나이] [성별]` 형태로 입력해주세요.", color=0xFE2E2E)
            return await ctx.send(embed=embed)
        
        gender = gender.upper()
        if not (gender == 'F' or gender == 'M'):
            embed = discord.Embed(title="경고", description="잘못된 성별 값입니다. 성별은 F(female), M(male)로 입력해주세요.", color=0xFE2E2E)
            return await ctx.send(embed=embed)
        
        # db update
        userid = name.id
        nickname = name.display_name
        guild = ctx.guild
        roles = ctx.guild.roles
        gender_str = {'M':'Male', 'F':"Female"}
        
        con, cur = connect()
        sql = f'SELECT EXISTS ( SELECT * FROM {self.table_name} WHERE userid = {userid} );'
        cur.execute(sql)
        if cur.fetchall()[0][0] == 0:
            cur.execute(f'INSERT INTO {self.table_name} VALUES(?,?,?,?);', (userid, nickname, age, gender))
            con.commit()

            #chack gender
            role = discord.utils.find(lambda r: r.name == gender_str[gender], ctx.guild.roles)
            if role == None:
                await guild.create_role(name=gender_str[gender], colour=discord.Colour(0x848484))
            
            role = discord.utils.get(ctx.guild.roles, name=gender_str[gender])
            await name.add_roles(role)
            
            embed = discord.Embed(title="역할 추가 완료", description=f"신규 유저 추가 완료. 반갑습니다 {name.mention}님!", color=0x00FFFF)
            await ctx.send(embed=embed)
        else :
            sql = f'UPDATE {self.table_name} SET age = {age}, gender = "{gender}" WHERE userid = {userid}'
            cur.execute(sql)
            con.commit()
            
            role = discord.utils.find(lambda r: r.name == gender_str[gender], ctx.guild.roles)
            if role == None:
                await guild.create_role(name=gender_str[gender], colour=discord.Colour(0x848484))
            
            role = discord.utils.get(ctx.guild.roles, name=gender_str[gender])
            await name.add_roles(role)
            
            embed = discord.Embed(title="역할 변경 완료", description=f"{name.mention}님 역할 업데이트 완료.", color=0x00FFFF)
            await ctx.send(embed=embed)
            
        db_close(con, cur)
        return
        
        
        
async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))