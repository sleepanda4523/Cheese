import os
from dotenv import load_dotenv
import discord
from discord.ext import commands 

load_dotenv()

# bot init 
bot_token = os.getenv('BOT_TOKEN')
intents = discord.Intents.all()

game = discord.Game("$도움말") 
bot = commands.Bot(command_prefix='$', intents=intents)

# get Cogs dir
cogs_path = 'Cogs'
abs_cogs_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), cogs_path)

# load Cogs
for ext in os.listdir(abs_cogs_path):
    if ext.endswith(".py"):
        bot.load_extension(f"Cogs.{ext.split('.')[0]}")

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=game,)
    print("Bot is ready")

@bot.command(name="도움말")
async def help(ctx):
    await ctx.send('아직 준비된 명령어가 없습니다.')

def main():
    bot.remove_command("help")
    bot.run(bot_token)
    return

if __name__ == "__main__":
    main()