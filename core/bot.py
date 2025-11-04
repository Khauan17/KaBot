# core/bot.py - Corrigido
import discord
from discord.ext import commands, tasks
from datetime import datetime
from core.config import Config
from core.db_manager import DBManager
from services.ai_service import AIService
from services.tool_service import ToolService
import os

class KaBot(commands.Bot):
    """Classe principal do KaBot, herda de commands.Bot."""
    
    def __init__(self, db_manager: DBManager, ai_service: AIService = None, tool_service: ToolService = None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(command_prefix='!ka ', intents=intents, help_command=None)
        
        self.start_time = datetime.now()
        self.version = "6.0 (Refatorado)" # Nova versão
        self.db_manager = db_manager
        self.ai_service = ai_service
        self.active_chat_channels = {} # Para gerenciar chats ativos, se necessário

    async def setup_hook(self):
        """Chamado antes do bot se conectar ao Discord."""
        print("--- Configurando o Bot ---")
        
        # 1. Carregar a instrução de sistema da IA
        await self.ai_service.load_system_instruction()
        
        # 2. Carregar extensões (Cogs e Eventos)
        await self._load_extensions()
        
        # 3. Iniciar tarefas em loop
        self.check_aniversario.start()
        
        print("--------------------------")

    async def on_ready(self):
        """Chamado quando o bot está pronto."""
        print(f"🔵 Bot online como {self.user}")
        print(f"🔵 Versão: {self.version}")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"As Aventuras de Kazinho | v{self.version}"))
        
        # Sincronizar comandos de barra
        try:
            synced = await self.tree.sync()
            print(f"Sincronizados {len(synced)} comandos de barra.")
        except Exception as e:
            print(f"Erro ao sincronizar comandos: {e}")

    @tasks.loop(hours=1)
    async def check_aniversario(self):
        """Verifica se é o aniversário do criador."""
        now = datetime.now()
        if now.hour == 12:
            channel = self.get_channel(Config.ANIVERSARY_CHANNEL_ID)
            if not channel: return
            user = self.get_user(Config.CREATOR_ID)
            if not user: return
            
            month, day = Config.ANIVERSARY_DATE
            if now.month == month and now.day == day:
                await channel.send(f"🎂 **BORA COMEMORAR!** 🥳🎉🎈\nHoje é o dia do meu mestre {user.mention}!\nMandem parabéns!")

    async def _load_extensions(self):
        """Carrega todos os Cogs e Eventos."""
        print("--- Carregando Módulos ---")
        
        # Graças ao os.chdir() no main.py, o diretório de trabalho já é 'kabot_refactor'
        # Portanto, os caminhos para os Cogs e Eventos são relativos a ele.
        cogs_path = './cogs'
        events_path = './events'

        # Carrega Cogs de comandos
        print(f"Procurando Cogs em: {os.path.abspath(cogs_path)}")
        for filename in os.listdir(cogs_path):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    await self.load_extension(f'cogs.{module_name}')
                    print(f"[OK] Cog: {module_name}")
                except Exception as e:
                    print(f"[ERRO] Falha ao carregar Cog {module_name}: {e}")
                    
        # Carrega Cogs de eventos
        print(f"Procurando Eventos em: {os.path.abspath(events_path)}")
        for filename in os.listdir(events_path):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    await self.load_extension(f'events.{module_name}')
                    print(f"[OK] Evento: {module_name}")
                except Exception as e:
                    print(f"[ERRO] Falha ao carregar Evento {module_name}: {e}")
                    
        print("--------------------------")
