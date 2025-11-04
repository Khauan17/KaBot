# events/chat_handler.py
import discord
from discord.ext import commands
from services.ai_service import AIService
from services.tool_service import ToolService
import random
import requests
import json

class ChatHandler(commands.Cog):
    """Lida com eventos de mensagem para interações de chat fora dos comandos."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai_service: AIService = bot.ai_service
        self.tool_service = ToolService() # Para a lógica de GIF de reação

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Processa mensagens para responder a menções e anexos de imagem."""
        
        # Ignora mensagens do próprio bot
        if message.author == self.bot.user:
            return

        # Verifica se o bot foi mencionado ou se é uma DM
        is_mentioned = self.bot.user.mentioned_in(message)
        is_dm = isinstance(message.channel, discord.DMChannel)
        
        if is_mentioned or is_dm:
            # Remove a menção do bot do conteúdo da mensagem
            prompt = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
            
            # Se a mensagem estiver vazia após remover a menção, e não houver anexos, ignora
            if not prompt and not message.attachments:
                return

            # Processamento de Imagem (Visão)
            image_bytes = None
            if message.attachments:
                for attachment in message.attachments:
                    # Verifica se o anexo é uma imagem
                    if 'image' in attachment.content_type:
                        # Baixa o primeiro anexo de imagem encontrado
                        try:
                            image_bytes = await attachment.read()
                            if not prompt:
                                prompt = "Descreva e analise esta imagem."
                            else:
                                prompt = f"Com base nesta imagem, responda: {prompt}"
                            break
                        except Exception as e:
                            print(f"❌ Erro ao baixar anexo de imagem: {e}")
                            # Continua sem a imagem se falhar
            
            # Indica que está processando
            async with message.channel.typing():
                # Gera a resposta
                response = await self.ai_service.generate_response(message.author.id, prompt, image_bytes, message.channel.id)
            
            # Envia a resposta
            await message.reply(response)
            return # Sai do on_message após responder à menção/DM

        # --- Lógica do Modo Macaco ---
        fun_cog = self.bot.get_cog('Fun') # Pega o Cog de diversão (agora chamado 'Fun')
        if fun_cog and fun_cog.monkey_mode_active.get(message.guild.id):
            
            # Garante que a contagem seja inicializada
            current_count = fun_cog.monkey_mode_counts.get(message.guild.id, 0)
            fun_cog.monkey_mode_counts[message.guild.id] = current_count + 1
            
            frequency = fun_cog.monkey_mode_frequency.get(message.guild.id, 5)

            if fun_cog.monkey_mode_counts[message.guild.id] >= frequency:
                # Coleta mensagens válidas no histórico (não-bot, não-comando, não vazio)
                valid_messages = []
                async for msg in message.channel.history(limit=50): # Limite para não sobrecarregar
                    if not msg.author.bot and not msg.content.startswith(self.bot.command_prefix) and msg.content:
                        valid_messages.append(msg.content)
                
                if valid_messages:
                    await message.channel.send(random.choice(valid_messages))
                else:
                    await message.channel.send(random.choice(["Uh uh ah ah!", "Banana!", "Macaco forte!"]))
                
                fun_cog.monkey_mode_counts[message.guild.id] = 0 # Reinicia a contagem
        
        # --- Lógica de Reação com GIF Aleatório ---
        content_lower = message.content.lower()
        triggers = {'triste': 'sad', 'chorando': 'crying', 'feliz': 'happy', 'kkk': 'laughing', 'bom dia': 'good morning'}
        
        # 5% de chance de reagir com GIF
        if random.random() < 0.05: 
            for trigger, search_term in triggers.items():
                if trigger in content_lower:
                    # Chama a função síncrona da ToolService em um thread
                    tool_output_json = await self.bot.loop.run_in_executor(None, self.tool_service.send_gif_tool, search_term)
                    tool_output = json.loads(tool_output_json)
                    
                    if tool_output.get('url'):
                        await message.channel.send(tool_output['url'])
                        break # Reage apenas uma vez por mensagem
                    break # Sai do loop de triggers se um for encontrado, mesmo que a busca falhe

async def setup(bot):
    """Adiciona o Cog ao bot."""
    await bot.add_cog(ChatHandler(bot))
