from keep_alive import keep_alive
import discord
from discord.ext import commands
import os
import asyncio
import requests
import json
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
NASA_API_KEY = os.getenv("NASA_API_KEY")

# Inicializa Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Intents do bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!ka ', intents=intents)

# Controlador do bot
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
            print(f"Tabelas não existem, criar manualmente depois. Erro: {e}")
    
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
            print(f"Erro NASA: {e}")
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
        await ctx.send("Não consegui acessar a NASA agora :(")

# ⏳ Bot roda por 4h e desliga sozinho
async def limited_runtime():
    print("✅ Bot ligado. Funcionando por 4h...")
    await asyncio.sleep(4 * 3600)  # 4 horas
    print("🛑 Tempo esgotado. Desligando o bot automaticamente.")
    await bot.close()

@bot.event
async def on_ready():
    bot.loop.create_task(limited_runtime())
    print(f"🔵 Bot online como {bot.user}")

if __name__ == "__main__":
    keep_alive()
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"Erro no Discord: {e}")
