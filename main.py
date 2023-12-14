import os
from dotenv import load_dotenv
import discord
from discord.ext import commands 

load_dotenv()

# bot init 
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
game = discord.Game("!사용방법") 
bot = commands.Bot(command_prefix='!',activity=game, intents=intents)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

def main():
    bot_token = os.environ['BOT_TOKEN']
    bot.run(bot_token)
    return

if __name__ == "__main__":
    main()