# cogs/fun.py - Corrigido
import discord
from discord.ext import commands
from discord import Interaction, ButtonStyle
from discord.ui import View, Button
import random
import os
import requests
import json
from services.tool_service import ToolService # Para usar a lógica de GIF

class Fun(commands.Cog):
    """Comandos de diversão e entretenimento."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tool_service = ToolService() # Reutiliza a lógica de GIF
        self.monkey_mode_active = {}
        self.monkey_mode_frequency = {}
        self.monkey_mode_counts = {}
        self.memes = [
            "O que o tomate foi fazer no banco? Foi tirar extrato! 🍅💸",
            "Sabe por que o Mário não pode ser mecânico? Porque ele sempre 'super-pula' as peças! 🍄🔧",
            "Por que o pão de sal não briga com ninguém? Porque ele é pacífico... 🍞☮️",
            "Onde o hino nacional é cantado? No meio do hino nacional! 🎶",
            "O que o pato disse para a pata? Vem Quá! 🦆",
            "É pavê ou pra comer? Nem sei, só sei programar. 😅",
            "Onde o Batman guarda as suas moedas? No Bat-cão... porque o cofrinho dele é o Bat-móvel. 🦇💰"
        ]

    @commands.command(name='meme', help='Conta uma piada engraçada.')
    async def meme(self, ctx):
        await ctx.send(random.choice(self.memes))
            
    @commands.command(name='roleta', help='Gira uma roleta e te dá um número de 1 a 100.')
    async def roleta(self, ctx):
        await ctx.send(f"A roleta girou e o número da sorte é: **{random.randint(1, 100)}**!")
        
    @commands.command(name='abracar', help='Dá um abraço em um membro do servidor.')
    async def abracar(self, ctx, membro: discord.Member):
        if membro == ctx.author:
            await ctx.send("Abraçando a si mesmo? Toma um abraço meu. 🤗")
        else:
            await ctx.send(f"Opa, {ctx.author.mention} deu um abraço apertado em {membro.mention}! 🤗")
        
    @commands.command(name='jokenpo', aliases=['ppt'], help='Joga pedra, papel ou tesoura comigo.')
    async def jokenpo(self, ctx):
        view = View(timeout=30)
        choices = ["pedra", "papel", "tesoura"]
        
        async def button_callback(interaction: Interaction):
            if interaction.user != ctx.author: 
                return await interaction.response.send_message("Opa, esse jogo não é seu!", ephemeral=True)
            user_choice = interaction.data['custom_id']
            bot_choice = random.choice(choices)
            result_text = ""
            if user_choice == bot_choice: result_text = f"Empate! Nós dois escolhemos **{user_choice}**."
            elif (user_choice, bot_choice) in [("pedra", "tesoura"), ("papel", "pedra"), ("tesoura", "papel")]: result_text = f"Vitória! Eu escolhi **{bot_choice}** e você **{user_choice}**."
            else: result_text = f"Derrota! Eu escolhi **{bot_choice}** e você **{user_choice}**. Eu sou o mais forte!"
            for item in view.children: item.disabled = True
            await interaction.response.edit_message(content=result_text, view=view)
            view.stop()
            
        pedra = Button(label="Pedra", emoji="🗿", style=ButtonStyle.secondary, custom_id="pedra")
        papel = Button(label="Papel", emoji="📄", style=ButtonStyle.secondary, custom_id="papel")
        tesoura = Button(label="Tesoura", emoji="✂️", style=ButtonStyle.secondary, custom_id="tesoura")
        pedra.callback = papel.callback = tesoura.callback = button_callback
        
        view.add_item(pedra); view.add_item(papel); view.add_item(tesoura)
        await ctx.send("Vamos jogar! Escolha uma opção:", view=view)

    @commands.command(name='gif', help='Busca um GIF aleatório sobre um tema.')
    async def gif(self, ctx, *, search_term: str):
        # Chama a função síncrona da ToolService em um thread
        tool_output_json = await self.bot.loop.run_in_executor(None, self.tool_service.send_gif_tool, search_term)
        tool_output = json.loads(tool_output_json)
        
        if tool_output.get("url"):
            await ctx.send(tool_output['url'])
        elif tool_output.get("result"):
            await ctx.send(tool_output['result'])
        else:
            await ctx.send(tool_output.get("error", "Erro desconhecido ao buscar GIF."))

    @commands.command(name='monkey', help='Ativa o modo macaco. Use 0 para desativar.')
    async def monkey_mode(self, ctx, frequency: int):
        if not ctx.guild: return await ctx.send("Este comando só funciona em servidores.")
        if frequency > 0:
            self.monkey_mode_active[ctx.guild.id] = True
            self.monkey_mode_frequency[ctx.guild.id] = frequency
            self.monkey_mode_counts[ctx.guild.id] = 0
            await ctx.send(f"Modo Macaco ativado! Vou repetir mensagens a cada {frequency} mensagens. 🐒")
        else:
            self.monkey_mode_active[ctx.guild.id] = False
            await ctx.send("Modo Macaco desativado. 😌")

async def setup(bot):
    """Adiciona o Cog ao bot."""
    await bot.add_cog(Fun(bot))
