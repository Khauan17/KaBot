
import discord
from datetime import datetime
import random

class CerebroConversacional:
    def __init__(self, bot):
        self.bot = bot
        self.respostas_padrao = [
            "Interessante! 🤔 Deixe-me pensar sobre isso...",
            "Que pergunta curiosa! 💭",
            "Hmm, isso me lembra de algo que aconteceu aqui antes...",
            "Ótima questão! 🌟 Vou consultar minhas lembranças.",
            "Isso desperta minha curiosidade! 🔍"
        ]
    
    async def processar_interacao(self, message):
        """Processa uma interação direta com o KaBot"""
        try:
            # Consultar memória de longo prazo para contexto
            memorias_relacionadas = await self.bot.memoria.buscar_memorias_relacionadas(
                message.content, limite=3
            )
            
            # Gerar resposta contextual
            resposta = await self.gerar_resposta(message, memorias_relacionadas)
            
            # Enviar resposta
            await message.reply(resposta)
            
        except Exception as e:
            print(f"❌ Erro no cérebro conversacional: {e}")
            await message.reply("🤔 Desculpe, tive um pequeno problema para processar isso. Pode tentar novamente?")
    
    async def gerar_resposta(self, message, memorias):
        """Gera uma resposta inteligente baseada no contexto e memórias"""
        conteudo = message.content.lower()
        
        # Remover menções do bot
        conteudo = conteudo.replace('<@1213518484370104331>', '').replace('kabot', '').strip()
        
        # Respostas específicas baseadas no conteúdo
        if any(palavra in conteudo for palavra in ['olá', 'oi', 'hello', 'hey']):
            return f"Olá, {message.author.mention}! 👋 Como posso ajudar você hoje?"
        
        elif any(palavra in conteudo for palavra in ['como', 'está', 'vai']):
            return "Estou sempre bem! 😊 Observando nossa comunidade e aprendendo coisas novas. E você, como está?"
        
        elif any(palavra in conteudo for palavra in ['obrigado', 'obrigada', 'thanks', 'valeu']):
            return "Por nada! 😊 Estou aqui para ajudar nossa comunidade a ficar ainda melhor!"
        
        elif 'lembrar' in conteudo or 'memória' in conteudo:
            if memorias:
                contexto = f"🧠 Baseado nas minhas lembranças, posso dizer que:\n\n"
                for memoria in memorias[:2]:
                    contexto += f"• {memoria['resumo'][:150]}...\n"
                return contexto
            else:
                return "🤔 Ainda não tenho lembranças específicas sobre isso, mas estou sempre aprendendo!"
        
        elif any(palavra in conteudo for palavra in ['help', 'ajuda', 'comandos']):
            return self.gerar_ajuda()
        
        else:
            # Resposta padrão com possível contexto de memórias
            resposta = random.choice(self.respostas_padrao)
            
            if memorias:
                resposta += f"\n\n💭 Isso me lembra de algo que aconteceu recentemente: {memorias[0]['resumo'][:100]}..."
            
            return resposta
    
    def gerar_ajuda(self):
        """Gera a mensagem de ajuda"""
        help_text = """
🤖 **KaBot - Seu Assistente Inteligente**

**Como interagir comigo:**
• Me mencione (@KaBot) ou escreva "kabot" no início da mensagem
• Faça perguntas sobre a comunidade
• Peça para eu lembrar de coisas passadas

**Comandos disponíveis:**
• `!ka memoria [quantidade]` - Ver minhas lembranças recentes
• `!ka status` - Ver status dos meus sistemas

**Minhas habilidades:**
🧠 Lembro de conversas e eventos importantes
📡 Trago notícias interessantes regularmente
💬 Participo de conversas de forma natural

Estou sempre aprendendo e evoluindo! 🌟
        """
        return help_text
