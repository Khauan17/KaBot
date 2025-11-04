# cogs/ai_commands.py
import discord
from discord.ext import commands
from services.ai_service import AIService

class AICommands(commands.Cog):
    """Comandos de interação direta com a Inteligência Artificial."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Acessa o AIService que foi injetado na classe KaBot
        self.ai_service: AIService = bot.ai_service

    @commands.command(name='chat', help='Converse com o KaBot.')
    async def chat_prefix(self, ctx: commands.Context, *, prompt: str):
        """Comando de prefixo para chat."""
        await self._handle_chat(ctx, prompt)

    @discord.app_commands.command(name='chat', description='Converse com o KaBot.')
    @discord.app_commands.describe(prompt='Sua mensagem para o KaBot.')
    async def chat_slash(self, interaction: discord.Interaction, prompt: str):
        """Comando de barra para chat."""
        await interaction.response.defer()
        await self._handle_chat(interaction, prompt)

    async def _handle_chat(self, context_or_interaction, prompt: str):
        """Lógica unificada para comandos de chat (prefixo e barra)."""
        
        # Determinar se é um Context ou Interaction
        if isinstance(context_or_interaction, commands.Context):
            user_id = context_or_interaction.author.id
            send_func = context_or_interaction.send
            attachments = context_or_interaction.message.attachments
        else: # discord.Interaction
            user_id = context_or_interaction.user.id
            send_func = context_or_interaction.followup.send
            # Em comandos de barra, anexos não são diretamente suportados no prompt,
            # mas podemos verificar se a mensagem original tinha anexos se fosse um comando de contexto.
            # Para comandos de barra, a funcionalidade de visão será tratada no Evento on_message
            # ou em um comando de barra específico para visão, se necessário.
            attachments = [] 

        # Se houver anexos, vamos tratar a visão aqui (apenas para o comando de prefixo, por enquanto)
        image_bytes = None
        if attachments:
            for attachment in attachments:
                if 'image' in attachment.content_type:
                    # Baixa o primeiro anexo de imagem encontrado
                    image_bytes = await attachment.read()
                    prompt = f"**Análise de Imagem:** {prompt}" # Adiciona um contexto para a IA
                    break
        
        # Gera a resposta
        channel_id = context_or_interaction.channel.id
        response = await self.ai_service.generate_response(user_id, prompt, image_bytes, channel_id)
        
        # Envia a resposta
        await send_func(response)

async def setup(bot):
    """Adiciona o Cog ao bot."""
    await bot.add_cog(AICommands(bot))
