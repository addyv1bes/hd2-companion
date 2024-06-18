import discord
from discord.ext import tasks, commands
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os
import asyncio

load_dotenv(dotenv_path='env.env')
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

CHANNEL_IDS = list(map(int, os.getenv('DISCORD_CHANNEL_IDS', '1237587996837023814,1252701333111312445').split(',')))

if TOKEN is None:
    raise ValueError("No DISCORD_BOT_TOKEN found in environment variables")

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

def scrape_helldivers_notifications():
    url = 'https://helldiverscompanion.com'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    notifications = []

    for item in soup.find_all(class_='notification'):
        title = item.find(class_='title').get_text(strip=True)
        content = item.find(class_='content').get_text(strip=True)
        notifications.append((title, content))

    return notifications

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    check_notifications.start()

@tasks.loop(minutes=10)
async def check_notifications():
    notifications = scrape_helldivers_notifications()

    for channel_id in CHANNEL_IDS:
        channel = bot.get_channel(channel_id)
        if channel is None:
            print(f'Channel with ID {channel_id} not found')
            continue

        for title, content in notifications:
            embed = discord.Embed(title=title, description=content, color=discord.Color.blue())
            await channel.send(embed=embed)

@check_notifications.before_loop
async def before_check_notifications():
    await bot.wait_until_ready()

bot.run(TOKEN)