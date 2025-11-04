# events/lifecycle.py
import discord
from discord.ext import commands

class Lifecycle(commands.Cog):
    """Eventos de ciclo de vida do bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_connect(self):
        """Chamado quando o bot se conecta ao Discord."""
        print("🟢 Conectado ao Discord.")

    @commands.Cog.listener()
    async def on_disconnect(self):
        """Chamado quando o bot se desconecta do Discord."""
        print("🔴 Desconectado do Discord.")

async def setup(bot):
    """Adiciona o Cog ao bot."""
    await bot.add_cog(Lifecycle(bot))
