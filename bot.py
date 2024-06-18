import discord
from discord.ext import tasks, commands
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID = 1252701333111312445  # Replace with your designated channel ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Function to scrape the Helldivers Companion website
def scrape_helldivers_notifications():
    url = 'https://helldiverscompanion.com'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Logic to extract notifications from the website
    notifications = []

    # Example: Assuming the website has elements with class 'notification'
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
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print('Channel not found')
        return

    notifications = scrape_helldivers_notifications()
    for title, content in notifications:
        embed = discord.Embed(title=title, description=content, color=discord.Color.blue())
        await channel.send(embed=embed)

@check_notifications.before_loop
async def before_check_notifications():
    await bot.wait_until_ready()

bot.run(TOKEN)