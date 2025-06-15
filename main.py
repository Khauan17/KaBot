
import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timedelta
import json

# Importar os módulos do KaBot
from kabot.cerebro_conversacional import CerebroConversacional
from kabot.sistema_memoria import SistemaMemoria
from kabot.radar_informacoes import RadarInformacoes

# Carregar variáveis de ambiente
load_dotenv()

class KaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix='!ka ',
            intents=intents,
            description='KaBot - Assistente inteligente e proativo para Discord'
        )
        
        # Inicializar os sistemas
        self.cerebro = CerebroConversacional(self)
        self.memoria = SistemaMemoria()
        self.radar = RadarInformacoes(self)
        
        # Configurar tarefas periódicas
        self.processamento_diario.start()
        self.busca_noticias.start()
    
    async def on_ready(self):
        print(f'🤖 {self.user} está online e pronto!')
        print(f'🧠 Cérebro Conversacional: Ativo')
        print(f'💾 Sistema de Memória: Ativo')
        print(f'📡 Radar de Informações: Ativo')
        
        # Inicializar banco de dados
        await self.memoria.inicializar_bd()
    
    async def on_message(self, message):
        # Não responder a si mesmo
        if message.author == self.user:
            return
        
        # Salvar mensagem na memória de curto prazo
        await self.memoria.salvar_mensagem(message)
        
        # Verificar se foi mencionado ou se deve responder
        if self.user in message.mentions or message.content.lower().startswith('kabot'):
            await self.cerebro.processar_interacao(message)
        
        # Processar comandos
        await self.process_commands(message)
    
    @tasks.loop(hours=24)
    async def processamento_diario(self):
        """Processa a memória diariamente às 2:00 AM"""
        print("🔄 Iniciando processamento diário da memória...")
        await self.memoria.processar_memoria_diaria()
        print("✅ Processamento diário concluído!")
    
    @processamento_diario.before_loop
    async def before_processamento_diario(self):
        await self.wait_until_ready()
        # Aguardar até as 2:00 AM
        now = datetime.now()
        next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        await asyncio.sleep((next_run - now).total_seconds())
    
    @tasks.loop(hours=4)
    async def busca_noticias(self):
        """Busca e compartilha notícias a cada 4 horas"""
        print("📡 Buscando novas informações...")
        await self.radar.buscar_e_compartilhar_noticias()
    
    @busca_noticias.before_loop
    async def before_busca_noticias(self):
        await self.wait_until_ready()

# Comandos do bot
@commands.command(name='memoria')
async def ver_memoria(ctx, quantidade: int = 5):
    """Mostra as últimas lembranças do KaBot"""
    bot = ctx.bot
    memorias = await bot.memoria.obter_memorias_recentes(quantidade)
    
    if not memorias:
        await ctx.send("🤔 Ainda não tenho lembranças armazenadas!")
        return
    
    embed = discord.Embed(
        title="🧠 Minhas Lembranças Recentes",
        color=0x00ff88,
        description="Aqui estão algumas coisas que lembro da nossa comunidade:"
    )
    
    for i, memoria in enumerate(memorias, 1):
        embed.add_field(
            name=f"📅 {memoria['data']}",
            value=memoria['resumo'][:200] + "..." if len(memoria['resumo']) > 200 else memoria['resumo'],
            inline=False
        )
    
    await ctx.send(embed=embed)

@commands.command(name='status')
async def status_kabot(ctx):
    """Mostra o status dos sistemas do KaBot"""
    bot = ctx.bot
    
    embed = discord.Embed(
        title="🤖 Status do KaBot",
        color=0x00ff88
    )
    
    embed.add_field(
        name="🧠 Cérebro Conversacional",
        value="✅ Ativo - Monitorando conversas",
        inline=False
    )
    
    embed.add_field(
        name="💾 Sistema de Memória",
        value="✅ Ativo - Coletando experiências",
        inline=False
    )
    
    embed.add_field(
        name="📡 Radar de Informações",
        value="✅ Ativo - Buscando novidades",
        inline=False
    )
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    # Criar e executar o bot
    bot = KaBot()
    
    # Adicionar comandos
    bot.add_command(ver_memoria)
    bot.add_command(status_kabot)
    
    try:
        bot.run(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")
