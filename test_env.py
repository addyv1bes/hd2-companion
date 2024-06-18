from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='env.env')

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if TOKEN is None:
    print("TOKEN is None")
else:
    print("TOKEN is loaded successfully:", TOKEN)