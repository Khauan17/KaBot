# cogs/admin.py - Corrigido
import discord
from discord.ext import commands
import random
from core.db_manager import DBManager # Importa o DBManager

class Admin(commands.Cog):
    """Comandos de administração e controle do bot."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_manager: DBManager = bot.db_manager # Acessa o DBManager injetado

    @commands.command(name='iachat', help='Ativa ou desativa o modo de chat da IA no canal atual.')
    @commands.is_owner() # Somente o criador pode usar
    async def toggle_chat_mode(self, ctx, status: str):
        if status.lower() in ('ativar', 'on'):
            self.bot.active_chat_channels[ctx.channel.id] = True
            await ctx.send("🤖 **Modo de chat da IA ativado!** Eu vou responder a mensagens neste canal ao ser mencionado ou em resposta às minhas mensagens.")
        elif status.lower() in ('desativar', 'off'):
            self.bot.active_chat_channels[ctx.channel.id] = False
            await ctx.send("😴 **Modo de chat da IA desativado.** Voltando ao modo normal.")
        else:
            await ctx.send("Comando inválido. Use `!ka iachat ativar` ou `!ka iachat desativar`.")

    @commands.command(name='gravar', help='Instrui a IA a gravar uma informação importante na sua memória.')
    @commands.is_owner() # Somente o criador pode usar
    async def record_memory(self, ctx, *, content: str):
        await self.db_manager.save_memory(ctx.author.id, self.bot.user.id, content)
        await ctx.send("📝 **Memória gravada!** A partir de agora, eu me lembrarei disso.")

    @commands.command(name='sorteio', help='Faz um sorteio entre todos os membros de um canal.')
    @commands.has_permissions(mention_everyone=True) # Permissão para mencionar a todos, que é o que o sorteio faz
    @commands.guild_only() # Garante que o comando só rode em servidores
    async def sorteio(self, ctx):
        await ctx.send("Contando os participantes...")
        
        # Filtra membros que não são bots e que podem ver o canal
        # O problema era que ctx.guild.members pode não estar preenchido se o bot não tiver a intent 'members'
        # Mas como a intent foi adicionada, o problema mais provável é a lentidão.
        # Vamos garantir que a lista de membros seja atualizada.
        
        # O comando original não usava fetch_members, mas para garantir, vamos usar.
        # No entanto, a intent 'members' já deve resolver. O problema pode ser a permissão.
        
        # Vamos manter a lógica original, pois a intent 'members' está ativada.
        members = [member for member in ctx.guild.members if not member.bot and member.permissions_in(ctx.channel).read_messages]
        
        if not members:
            return await ctx.send("Não há membros elegíveis para o sorteio neste canal.")
            
        vencedor = random.choice(members)
        await ctx.send(f"🎉 **E o sortudo da vez é: {vencedor.mention}!** Parabéns! 🎉")

    @commands.command(name='status', hidden=True, help='Define o status de atividade do bot.')
    @commands.is_owner() # Apenas o criador pode usar
    async def set_status(self, ctx, *, status_text: str):
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{status_text} | v{self.bot.version}")
        await self.bot.change_presence(activity=activity)
        await ctx.send(f"Status do bot alterado para: {status_text}", delete_after=5)

    @commands.command(name='msg', hidden=True, help='Envia uma mensagem para um canal específico.')
    @commands.is_owner() # Apenas o criador pode usar
    async def send_message_to_channel(self, ctx, channel: discord.TextChannel, *, message: str):
        try:
            await channel.send(message)
            await ctx.send(f"Mensagem enviada para {channel.mention}.", delete_after=5)
        except Exception as e:
            await ctx.send(f"Falha ao enviar mensagem: {e}")

async def setup(bot):
    """Adiciona o Cog ao bot."""
    await bot.add_cog(Admin(bot))
