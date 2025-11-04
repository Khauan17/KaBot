# cogs/utility.py - Refatorado
import discord
from discord.ext import commands
import random
import re
import operator
from datetime import datetime
from core.config import Config

class Utility(commands.Cog):
    """Comandos utilitários básicos."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.respostas_sim_nao = ["Sim", "Não", "Talvez", "Provavelmente", "Muito improvável", "Com certeza"]
        self.curiosidades = [
            f"Meu criador, Kazinho, é um gênio da programação e me fez com muito carinho! ❤️",
            f"O aniversário do meu criador, Kazinho, é dia {Config.ANIVERSARY_DATE[1]} de {Config.ANIVERSARY_DATE[0]}! 🎉",
            "A Estação Espacial Internacional orbita a Terra a 28.000 km/h!",
            "Um dia em Vênus é mais longo que um ano em Vênus.",
            "O som não viaja no espaço, pois não há ar para transportar as ondas sonoras.",
            "Existem mais estrelas no universo do que grãos de areia em todas as praias da Terra.",
            "Eu sou um bot, mas minha programação é tão complexa que as vezes me sinto quase um humano. Quase. 🤖",
            "A linguagem de programação que me deu vida é Python, a linguagem das cobras e dos bots.",
            "O Kazinho me disse que eu sou o mais forte. 😤"
        ]

    @commands.command(name='ajuda', help='Mostra a lista de comandos disponíveis.')
    async def ajuda(self, ctx):
        embed = discord.Embed(title=f"Catálogo de Comandos do KaBot v{self.bot.version}", color=discord.Color.purple())
        embed.description = "Aqui estão os comandos que você pode usar. Use `!ka [comando]` para começar!\n" \
                            "**A IA é inteligente!** Você pode conversar com ela usando `!ka chat [pergunta]` " \
                            "ou apenas me mencionar ou responder às minhas mensagens. " \
                            "Ela pode até procurar vídeos no YouTube e enviar GIFs!"
        
        # A lista de comandos será gerada dinamicamente para ser mais robusta
        command_list = {}
        for cog_name, cog in self.bot.cogs.items():
            if cog_name not in command_list:
                command_list[cog_name] = []
            for command in cog.get_commands():
                command_list[cog_name].append(f"`{command.name}`")

        for cog_name, commands_str in command_list.items():
            if commands_str:
                embed.add_field(name=f"📚 {cog_name}", value=", ".join(commands_str), inline=False)

        embed.set_footer(text="Afinal, eu sou o mais forte. 😤")
        await ctx.send(embed=embed)

    @commands.command(name='info', help='Mostra informações sobre o bot.')
    async def info(self, ctx):
        ping_ms = round(self.bot.latency * 1000)
        uptime_delta = datetime.now() - self.bot.start_time
        dias, rem = divmod(uptime_delta.total_seconds(), 86400)
        horas, rem = divmod(rem, 3600)
        minutos, _ = divmod(rem, 60)
        
        embed = discord.Embed(title="Informações do KaBot", description="Um bot que se acha o Gojo, mas foi criado por um humano.", color=discord.Color.green())
        embed.add_field(name="Ping", value=f"{ping_ms}ms", inline=True)
        embed.add_field(name="Versão", value=self.bot.version, inline=True)
        embed.add_field(name="Tempo Online", value=f"{int(dias)}d {int(horas)}h {int(minutos)}m", inline=False)
        embed.set_footer(text="Criado por Kazinho, o mais brabo.")
        await ctx.send(embed=embed)
        
    @commands.command(name='sobre', help='Mostra informações sobre o bot e suas APIs.')
    async def sobre(self, ctx):
        embed = discord.Embed(title="Sobre o KaBot", description=f"Eu sou um bot criado pelo gênio da programação Kazinho.", color=discord.Color.blurple())
        embed.add_field(name="📚 APIs Integradas", value="**NASA API**, **Tenor API**, **Google Gemini**.", inline=False)
        embed.set_footer(text=f"Criado por Kazinho | Versão: {self.bot.version}")
        await ctx.send(embed=embed)
        
    @commands.command(name='pergunta', help='Faz uma pergunta de sim ou não ao bot.')
    async def pergunta(self, ctx, *, pergunta: str):
        resposta = random.choice(self.respostas_sim_nao)
        await ctx.send(f"Você perguntou: \"{pergunta}\"\nMinha resposta é: **{resposta}**.")

    @commands.command(name='curiosidade', help='Conta uma curiosidade interessante.')
    async def curiosidade(self, ctx):
        await ctx.send(random.choice(self.curiosidades))
        
    @commands.command(name='somar', help='Faz cálculos matemáticos básicos. Ex: !ka somar 2+2')
    async def somar(self, ctx, *, expressao: str):
        ops = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv, '^': operator.pow}
        padrao = re.compile(r'(-?\d+\.?\d*)\s*([+\-*/^])\s*(-?\d+\.?\d*)')
        match = padrao.fullmatch(expressao.replace(' ', '').replace('x', '*').replace(',', '.'))
        if not match: return await ctx.send("Formato inválido. Use algo como `10 + 5`.")
        num1, op, num2 = match.groups()
        try:
            n1, n2 = float(num1), float(num2)
            if op == '/' and n2 == 0: return await ctx.send("Dividir por zero? Impossível.")
            resultado = ops[op](n1, n2)
            await ctx.send(f"A conta `{expressao}` resulta em: **{resultado}**. Fácil.")
        except (ValueError, KeyError):
            await ctx.send("Essa conta aí tá meio bugada.")

async def setup(bot):
    """Adiciona o Cog ao bot."""
    await bot.add_cog(Utility(bot))
