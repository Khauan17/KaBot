from keep_alive import keep_alive
import discord
from discord.ext import commands
import os
import asyncio
import requests
import random
from datetime import datetime, time as dtime
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
NASA_API_KEY = os.getenv("NASA_API_KEY")

# Inicializar Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!ka ', intents=intents)

class KaBot:
    def __init__(self):
        self.setup_database()
        self.kazinho_facts = [
            "Meu criador Kazinho é um gênio da programação! 🧠",
            "Kazinho me criou com muito carinho e dedicação! ❤️",
            "O Kazinho sempre tem as melhores ideias para me melhorar! 💡",
            "Sabia que o aniversário do Kazinho é dia 17/05/2008? 🎉"
        ]

    def setup_database(self):
        try:
            supabase.table('short_term_memory').select('*').limit(1).execute()
        except Exception as e:
            print(f"Tabelas não existem. Erro: {e}")

    async def fetch_nasa_news(self):
        try:
            url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&count=1"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and data:
                data = data[0]
                return {
                    'title': data.get('title', 'Notícia da NASA'),
                    'summary': data.get('explanation', '')[:300] + "...",
                    'image_url': data.get('url', ''),
                    'source': '🚀 NASA',
                    'date': data.get('date', datetime.now().strftime('%Y-%m-%d'))
                }
        except Exception as e:
            print(f"Erro ao buscar notícia da NASA: {e}")
        return None

kabot = KaBot()

@bot.command(name='oi')
async def oi(ctx):
    await ctx.send("Olá! Tudo bem?")

@bot.command(name='nasa')
async def nasa_news(ctx):
    news = await kabot.fetch_nasa_news()
    if news:
        embed = discord.Embed(
            title=news['title'],
            description=news['summary'],
            color=discord.Color.blue(),
            timestamp=datetime.strptime(news['date'], '%Y-%m-%d')
        )
        embed.set_image(url=news['image_url'])
        embed.set_footer(text=news['source'])
        await ctx.send(embed=embed)
    else:
        await ctx.send("Não foi possível obter as notícias da NASA.")

# 🕒 Desligar fora do horário (BR)
async def auto_shutdown():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.now().time()  # Horário local (Brasil)
        if not (dtime(12, 0) <= now <= dtime(14, 0) or dtime(18, 0) <= now <= dtime(20, 0)):
            print("⏰ Fora do horário (12–14h / 18–20h BRT). Desligando...")
            await bot.close()
        await asyncio.sleep(60)

@bot.event
async def on_ready():
    bot.loop.create_task(auto_shutdown())
    print("✅ Bot online! Horário permitido: 12h–14h e 18h–20h (Brasília)")

if __name__ == "__main__":
    keep_alive()
    try:
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure as e:
        print(f"Erro ao fazer login: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
