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

    for item in soup.find_all('div', class_='news-overlay svelte-usyz6r'):
        title_tag = item.find('h1', class_='news-headline svelte-usyz6r')
        content_tag = item.find('div', class_='news-content svelte-usyz6r')
        link_tag = item.find('a', href=True)

        if title_tag and content_tag and link_tag:
            title = title_tag.get_text(strip=True)
            content = content_tag.get_text(strip=True)
            link = link_tag['href']
            if not link.startswith('http'):
                link = 'https://helldiverscompanion.com' + link
            articles.append((title, content, link))
        else:
            print("Missing title, content, or link in one of the articles.")
    
    print(f"Found {len(articles)} articles.")
    return articles

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    for channel_id in CHANNEL_IDS:
        channel = bot.get_channel(channel_id)
        if channel is not None:
            asyncio.ensure_future(channel.send("Bot has successfully booted up and is now online!"))
    check_news.start()

@tasks.loop(minutes=60)
async def check_news():
    articles = scrape_helldivers_news()
    new_articles = [article for article in articles if article[0] not in seen_articles]
    
    for channel_id in CHANNEL_IDS:
        channel = bot.get_channel(channel_id)
        if channel is None:
            print(f'Channel with ID {channel_id} not found')
            continue

        if not new_articles:
            await channel.send("No new articles found.")
            continue

        for title, content, link in new_articles:
            embed = discord.Embed(title=title, description=content, url=link, color=discord.Color.blue())
            embed.add_field(name="Read more", value=f"[Click here]({link})")
            await channel.send(embed=embed)
            seen_articles.add(title)

@check_news.before_loop
async def before_check_news():
    await bot.wait_until_ready()

bot.run(TOKEN)