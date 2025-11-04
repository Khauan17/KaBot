# main.py
import discord
from discord.ext import commands, tasks
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from database import test_supabase_connection, get_bot_persona

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

BOT_VERSION = "5.5" # Atualizado para a versão 5.5
CREATOR_ID = 857228143478571029
ANIVERSARY_DATE = (5, 17)
ANIVERSARY_CHANNEL_ID = 1165064927430574100

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class KaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!ka ', intents=intents, help_command=None)
        self.start_time = datetime.now()
        self.version = BOT_VERSION
        self.creator_id = CREATOR_ID
        self.bot_persona = "" 
        self.active_chat_channels = {} 

bot = KaBot()

@bot.event
async def on_ready():
    print(f"🔵 Bot online como {bot.user}")
    print(f"🔵 Versão: {bot.version}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"As Aventuras de Kazinho | v{bot.version}"))
    check_aniversario.start()
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos de barra.")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")

@tasks.loop(hours=1)
async def check_aniversario():
    now = datetime.now()
    if now.hour == 12:
        channel = bot.get_channel(ANIVERSARY_CHANNEL_ID)
        if not channel: return
        user = bot.get_user(CREATOR_ID)
        if not user: return
        if now.month == ANIVERSARY_DATE[0] and now.day == ANIVERSARY_DATE[1]:
            await channel.send(f"🎂 **BORA COMEMORAR!** 🥳🎉🎈\nHoje é o dia do meu mestre {user.mention}!\nMandem parabéns!")

async def load_extensions():
    print("--- Carregando Módulos ---")
    # Carrega Cogs de comandos
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"[OK] Cog: {filename}")
            
    # Carrega Cogs de eventos (agora em pasta separada 'events')
    for filename in os.listdir('./events'):
        if filename.endswith('.py'):
            await bot.load_extension(f'events.{filename[:-3]}')
            print(f"[OK] Evento: {filename}")
    print("--------------------------")

async def main():
    async with bot:
        if not await test_supabase_connection():
            print("ERRO: O bot não pode iniciar sem a conexão com o banco de dados.")
            return

        bot.bot_persona = await get_bot_persona()
        print("📝 Personalidade do bot carregada com sucesso.")

        await load_extensions()
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except discord.LoginFailure:
        print("ERRO CRÍTICO: O token do Discord está incorreto. Verifique o seu .env!")
    except Exception as e:
        print(f"Erro geral ao iniciar o bot: {e}")