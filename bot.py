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

seen_articles = set()

def scrape_helldivers_news():
    url = 'https://helldiverscompanion.com/news'
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    for item in soup.find_all(class_='news-item'):
        title = item.find(class_='news-title').get_text(strip=True)
        link = item.find('a')['href']
        content = item.find(class_='news-content').get_text(strip=True)
        articles.append((title, content, link))

    return articles

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    check_news.start()

@tasks.loop(minutes=60)
async def check_news():
    articles = scrape_helldivers_news()
    if not articles:
        print("No new articles found.")
        return

    for channel_id in CHANNEL_IDS:
        channel = bot.get_channel(channel_id)
        if channel is None:
            print(f'Channel with ID {channel_id} not found')
            continue

        for title, content, link in articles:
            if title in seen_articles:
                continue

            embed = discord.Embed(title=title, description=content, url=link, color=discord.Color.blue())
            embed.add_field(name="Read more", value=f"[Click here]({link})")
            await channel.send(embed=embed)
            seen_articles.add(title)

@check_news.before_loop
async def before_check_news():
    await bot.wait_until_ready()

bot.run(TOKEN)