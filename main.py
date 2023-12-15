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


# load Cogs
@bot.event
async def setup_hook() -> None:
    cogs_path = 'Cogs'
    for ext in os.listdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), cogs_path)):
        if ext.endswith(".py") and 'db' not in ext:
            await bot.load_extension(f"Cogs.{ext.split('.')[0]}")
    print('extension Load OK')

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=game)
    print("Bot is ready")

@bot.command(name="도움말")
async def help(ctx):
    await ctx.send('아직 준비된 명령어가 없습니다.')

def main():
    bot.remove_command("help")
    bot.run(bot_token)

if __name__ == "__main__":
    main()