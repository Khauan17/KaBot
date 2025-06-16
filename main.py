from keep_alive import keep_alive
import discord
from discord.ext import commands, tasks
import os
import asyncio
import requests
import json
import random
from datetime import datetime, timedelta
import schedule
import time
from threading import Thread
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações usando variáveis de ambiente
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
NASA_API_KEY = os.getenv("NASA_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Inicializar Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurar intents do Discord
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!ka ', intents=intents)

class KaBot:
    def __init__(self):
        self.setup_database()
        self.learning_patterns = {}
        self.user_interactions = {}
        self.kazinho_facts = [
            "Meu criador Kazinho é um gênio da programação! 🧠",
            "Kazinho me criou com muito carinho e dedicação! ❤️",
            "O Kazinho sempre tem as melhores ideias para me melhorar! 💡",
            "Sabia que o aniversário do Kazinho é dia 17/05/2008? 🎉"
        ]
    
    def setup_database(self):
        """Criar tabelas necessárias no Supabase"""
        try:
            supabase.table('short_term_memory').select('*').limit(1).execute()
        except Exception as e:
            print(f"Tabelas não existem, criando. Erro original: {e}")
            # Implemente a criação das tabelas aqui
            # Exemplo:
            # supabase.from_('short_term_memory').insert({}).execute() # Cria a tabela se não existir
            pass

    async def fetch_nasa_news(self):
        """Buscar notícias da NASA (sem tradução)"""
        try:
            url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&count=1"
            response = requests.get(url, timeout=15)
            response.raise_for_status()  # Lança exceção para status de erro (4xx ou 5xx)

            data = response.json()
            if isinstance(data, list) and data:  # Verifica se é uma lista não vazia
                data = data[0]
                return {
                    'title': data.get('title', 'Notícia da NASA'),
                    'summary': data.get('explanation', '')[:300] + "..." if data.get('explanation') else '',
                    'image_url': data.get('url', ''),
                    'source': '🚀 NASA',
                    'date': data.get('date', datetime.now().strftime('%Y-%m-%d'))
                }
            else:
                print("Resposta da NASA inesperada ou vazia.")
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição à API da NASA: {e}")
        except (KeyError, IndexError) as e:
            print(f"Erro ao processar a resposta da NASA: {e}")
        except Exception as e:
            print(f"Erro inesperado ao buscar notícias da NASA: {e}")
        return None

# Instância do KaBot
kabot = KaBot()

# Resto do seu código (comandos do bot, eventos, etc.)
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


if __name__ == "__main__":
    keep_alive()
    try:
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure as e:
        print(f"Erro ao fazer login no Discord: {e}")
        print("Verifique se o token do Discord está correto e se o bot tem as permissões necessárias.")
    except Exception as e:
        print(f"Erro inesperado ao iniciar o bot: {e}")
