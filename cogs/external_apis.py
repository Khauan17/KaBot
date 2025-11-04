# cogs/external_apis.py
import discord
from discord.ext import commands
from services.external_service import ExternalService

class ExternalAPIs(commands.Cog):
    """Comandos que interagem com APIs externas (NASA, News, etc.)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.external_service = ExternalService()

    @commands.command(name='nasa', help='Busca a Imagem Astronômica do Dia (APOD) da NASA.')
    async def nasa_prefix(self, ctx: commands.Context):
        """Comando de prefixo para NASA APOD."""
        await self._handle_nasa(ctx)

    @discord.app_commands.command(name='nasa', description='Busca a Imagem Astronômica do Dia (APOD) da NASA.')
    async def nasa_slash(self, interaction: discord.Interaction):
        """Comando de barra para NASA APOD."""
        await interaction.response.defer()
        await self._handle_nasa(interaction)

    async def _handle_nasa(self, context_or_interaction):
        """Lógica unificada para comandos da NASA."""
        
        # Determinar a função de resposta
        if isinstance(context_or_interaction, commands.Context):
            send_func = context_or_interaction.send
        else: # discord.Interaction
            send_func = context_or_interaction.followup.send

        # Gera a resposta
        response = await self.external_service.get_nasa_apod()
        
        # Envia a resposta
        await send_func(response)

    @commands.command(name='news', help='Busca a manchete de notícias.')
    async def news_prefix(self, ctx: commands.Context, category: str = 'general'):
        """Comando de prefixo para notícias."""
        await self._handle_news(ctx, category)

    @discord.app_commands.command(name='news', description='Busca a manchete de notícias.')
    @discord.app_commands.describe(category='Categoria da notícia (ex: technology, sports, business).')
    async def news_slash(self, interaction: discord.Interaction, category: str = 'general'):
        """Comando de barra para notícias."""
        await interaction.response.defer()
        await self._handle_news(interaction, category)

    async def _handle_news(self, context_or_interaction, category: str):
        """Lógica unificada para comandos de notícias."""
        
        # Determinar a função de resposta
        if isinstance(context_or_interaction, commands.Context):
            send_func = context_or_interaction.send
        else: # discord.Interaction
            send_func = context_or_interaction.followup.send

        # Gera a resposta
        response = await self.external_service.get_news_headline(category)
        
        # Envia a resposta
        await send_func(response)

async def setup(bot):
    """Adiciona o Cog ao bot."""
    await bot.add_cog(ExternalAPIs(bot))
'''
    @commands.command(name='traduzir', help='Traduz um texto usando a IA. Ex: !ka traduzir pt-en Olá mundo')
    async def translate_prefix(self, ctx: commands.Context, lang_pair: str, *, text: str):
        """Comando de prefixo para tradução."""
        await self._handle_translate(ctx, lang_pair, text)

    @discord.app_commands.command(name='traduzir', description='Traduz um texto usando a IA.')
    @discord.app_commands.describe(lang_pair='Par de idiomas (ex: pt-en, en-es)', text='O texto a ser traduzido.')
    async def translate_slash(self, interaction: discord.Interaction, lang_pair: str, text: str):
        """Comando de barra para tradução."""
        await interaction.response.defer()
        await self._handle_translate(interaction, lang_pair, text)

    async def _handle_translate(self, context_or_interaction, lang_pair: str, text: str):
        """Lógica unificada para comandos de tradução."""
        
        # Determinar a função de resposta
        if isinstance(context_or_interaction, commands.Context):
            send_func = context_or_interaction.send
        else: # discord.Interaction
            send_func = context_or_interaction.followup.send

        try:
            source_lang, target_lang = lang_pair.split('-')
        except ValueError:
            return await send_func("Formato de idioma inválido. Use `origem-destino` (ex: `pt-en`).")

        # Gera a resposta
        response = await self.external_service.translate_text_explicit(text, source_lang, target_lang)
        
        # Envia a resposta
        await send_func(response)
'''
