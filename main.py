
import discord
from discord.ext import commands, tasks
import os
import asyncio
import requests
import json
import random
from datetime import datetime, timedelta
import schedule
import time
from threading import Thread
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
DISCORD_TOKEN = "MTIxMzUxODQ4NDM3MDEwNDMzMQ.GNe4QT.hTNHpNBOwvDc-M_8-mMOsfOVSshwKHwgnh6B2w"
SUPABASE_URL = "https://wbogxfeeegyvsidqsrzp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indib2d4ZmVlZWd5dnNpZHFzcnpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk4MzA1OTAsImV4cCI6MjA2NTQwNjU5MH0.OgDRZ-ewl57e8eby1fc44bl9G2w3t-vjKbvMSzD_eEY"
NASA_API_KEY = "hgozkUIygaNEwND9TZlYhaAlln7EDSv2WFtYcZFL"
NEWS_API_KEY = "27024cb1f1da415d9fcad64427f760a2"

# Inicializar Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurar intents do Discord
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Necessário para listar membros

bot = commands.Bot(command_prefix='!ka ', intents=intents)

class KaBot:
    def __init__(self):
        self.setup_database()
        # Sistema de aprendizado básico
        self.learning_patterns = {}
        self.user_interactions = {}
        self.kazinho_facts = [
            "Meu criador Kazinho é um gênio da programação! 🧠",
            "Kazinho me criou com muito carinho e dedicação! ❤️",
            "O Kazinho sempre tem as melhores ideias para me melhorar! 💡",
            "Kazinho é o mastermind por trás de toda minha inteligência! 🎯",
            "Devo tudo ao meu criador Kazinho - ele é incrível! 🌟",
            "Kazinho me ensinou tudo que sei sobre ser um bom bot! 📚",
            "O Kazinho tem um talento natural para criar coisas incríveis! 🚀"
        ]
    
    def setup_database(self):
        """Criar tabelas necessárias no Supabase"""
        try:
            # Tabela para memória de curto prazo (mensagens brutas)
            supabase.table('short_term_memory').select('*').limit(1).execute()
        except:
            print("Tabelas já existem ou foram criadas automaticamente")
    
    def learn_from_interaction(self, user_id, message_content, response_type):
        """Sistema básico de aprendizado"""
        if user_id not in self.user_interactions:
            self.user_interactions[user_id] = {
                'total_interactions': 0,
                'preferred_responses': {},
                'common_words': {},
                'interaction_times': []
            }
        
        # Registrar interação
        self.user_interactions[user_id]['total_interactions'] += 1
        self.user_interactions[user_id]['interaction_times'].append(datetime.now())
        
        # Aprender palavras frequentes do usuário
        words = message_content.lower().split()
        for word in words:
            if len(word) > 3:
                if word not in self.user_interactions[user_id]['common_words']:
                    self.user_interactions[user_id]['common_words'][word] = 0
                self.user_interactions[user_id]['common_words'][word] += 1
        
        # Registrar tipo de resposta preferida
        if response_type not in self.user_interactions[user_id]['preferred_responses']:
            self.user_interactions[user_id]['preferred_responses'][response_type] = 0
        self.user_interactions[user_id]['preferred_responses'][response_type] += 1
    
    def get_personalized_response(self, user_id, base_responses):
        """Gerar resposta personalizada baseada no aprendizado"""
        if user_id not in self.user_interactions:
            return random.choice(base_responses)
        
        user_data = self.user_interactions[user_id]
        
        # Se o usuário interage muito, dar respostas mais entusiasmadas
        if user_data['total_interactions'] > 10:
            enthusiastic_responses = [
                "Opa! Meu amigo querido! 🤗 Como posso ajudar hoje?",
                "Eyyy! Que bom te ver novamente! 😄 O que vamos fazer hoje?",
                "Olha só quem apareceu! 🌟 Sempre um prazer conversar contigo!",
                "Meu parceiro! 🤝 Já sei que vem coisa boa por aí!"
            ]
            return random.choice(enthusiastic_responses)
        
        # Resposta padrão personalizada
        return random.choice(base_responses)
    
    async def translate_text(self, text, target_lang="pt"):
        """Traduzir texto usando LibreTranslate API melhorada"""
        try:
            # Detectar se já está em português
            portuguese_indicators = ['o', 'a', 'de', 'da', 'do', 'em', 'no', 'na', 'para', 'com', 'não', 'são', 'é', 'foi', 'ter', 'ser', 'fazer', 'sobre', 'quando', 'onde', 'como', 'hoje', 'ontem', 'português', 'brasil']
            words = text.lower().split()
            pt_count = sum(1 for word in words if word in portuguese_indicators)
            
            # Se mais de 20% são palavras portuguesas, provavelmente já está em português
            if len(words) > 0 and (pt_count / len(words)) > 0.2:
                return text
            
            # Usar LibreTranslate
            url = "https://libretranslate.com/translate"
            data = {
                "q": text.strip(),
                "source": "auto",
                "target": target_lang,
                "format": "text"
            }
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, data=json.dumps(data), headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                translated = result.get("translatedText", text)
                # Se a tradução voltou igual, tentar fallback
                if translated.lower().strip() == text.lower().strip():
                    return self.fallback_translate(text)
                return translated
            else:
                print(f"Erro na API de tradução: {response.status_code}")
                return self.fallback_translate(text)
                
        except Exception as e:
            print(f"Erro ao traduzir: {e}")
            return self.fallback_translate(text)
    
    def fallback_translate(self, text):
        """Tradução de fallback melhorada"""
        translations = {
            # Astronomia e espaço
            "space": "espaço", "NASA": "NASA", "earth": "Terra", "moon": "lua", "sun": "sol",
            "planet": "planeta", "galaxy": "galáxia", "telescope": "telescópio", "mission": "missão",
            "science": "ciência", "astronomy": "astronomia", "discovery": "descoberta", "image": "imagem",
            "asteroid": "asteroide", "comet": "cometa", "satellite": "satélite", "rocket": "foguete",
            "orbit": "órbita", "spacecraft": "espaçonave", "universe": "universo", "stellar": "estelar",
            "solar": "solar", "lunar": "lunar", "cosmic": "cósmico", "radiation": "radiação",
            "atmosphere": "atmosfera", "mars": "Marte", "venus": "Vênus", "jupiter": "Júpiter",
            "saturn": "Saturno", "mercury": "Mercúrio", "neptune": "Netuno", "uranus": "Urano",
            "star": "estrela", "nebula": "nebulosa", "hourglass": "ampulheta", "planetary": "planetária",
            
            # Palavras comuns
            "the": "o", "and": "e", "of": "de", "in": "em", "to": "para", "is": "é", "was": "foi",
            "are": "são", "were": "eram", "have": "ter", "has": "tem", "will": "vai", "would": "seria",
            "this": "este", "that": "aquele", "with": "com", "from": "de", "by": "por", "at": "em",
            "you": "você", "see": "ver", "does": "faz", "it": "ele", "or": "ou", "shape": "forma",
            "do": "fazer", "engraved": "gravada", "beautiful": "bonita", "amazing": "incrível",
            "new": "novo", "old": "antigo", "big": "grande", "small": "pequeno", "high": "alto",
            "low": "baixo", "good": "bom", "bad": "ruim", "important": "importante", "special": "especial"
        }
        
        # Aplicar traduções palavra por palavra
        words = text.split()
        translated_words = []
        
        for word in words:
            # Remover pontuação para verificar
            clean_word = word.strip('.,!?;:"()[]{}').lower()
            if clean_word in translations:
                # Manter a pontuação original
                punctuation = ''.join(c for c in word if not c.isalnum())
                translated_words.append(translations[clean_word] + punctuation)
            else:
                translated_words.append(word)
        
        return ' '.join(translated_words)
    
    async def save_message_to_memory(self, message):
        """Salvar mensagem na memória de curto prazo"""
        try:
            # Filtrar mensagens muito curtas ou de bot
            if len(message.content) < 3 or message.author.bot:
                return
            
            data = {
                "guild_id": str(message.guild.id) if message.guild else None,
                "channel_id": str(message.channel.id),
                "user_id": str(message.author.id),
                "username": message.author.display_name[:50],
                "content": message.content[:1000],
                "timestamp": message.created_at.isoformat(),
                "message_id": str(message.id)
            }
            
            result = supabase.table('short_term_memory').insert(data).execute()
            
        except Exception as e:
            pass
    
    async def get_long_term_memory(self, guild_id=None, limit=10):
        """Buscar memória de longo prazo para contexto"""
        try:
            query = supabase.table('long_term_memory').select('*')
            if guild_id:
                query = query.eq('guild_id', str(guild_id))
            
            result = query.order('created_at', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            return []
    
    async def fetch_nasa_news(self):
        """Buscar notícias da NASA com tradução corrigida"""
        try:
            url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&count=1"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()[0]
                
                title = data.get('title', 'Notícia da NASA')
                explanation = data.get('explanation', '')
                image_url = data.get('url', '')
                
                # Traduzir para português
                print(f"🔄 Traduzindo título NASA: {title[:50]}...")
                title_pt = await self.translate_text(title)
                print(f"✅ Título traduzido: {title_pt[:50]}...")
                
                print(f"🔄 Traduzindo explicação NASA...")
                explanation_pt = await self.translate_text(explanation)
                print(f"✅ Explicação traduzida: {explanation_pt[:50]}...")
                
                # Criar resumo
                summary = explanation_pt[:300] + "..." if len(explanation_pt) > 300 else explanation_pt
                
                return {
                    'title': title_pt,
                    'summary': summary,
                    'full_description': explanation_pt,
                    'image_url': image_url,
                    'source': '🚀 NASA - Administração Nacional da Aeronáutica e Espaço',
                    'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'original_title': title
                }
        except Exception as e:
            print(f"❌ Erro ao buscar notícias da NASA: {e}")
        return None
    
    async def fetch_general_news(self):
        """Buscar notícias gerais em português"""
        try:
            # Usar notícias do Brasil para garantir português
            categorias = ['science', 'technology', 'health']
            categoria = random.choice(categorias)
            
            url = f"https://newsapi.org/v2/top-headlines?country=br&category={categoria}&pageSize=5&apiKey={NEWS_API_KEY}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data['articles']:
                    article = random.choice(data['articles'][:3])
                    
                    title = article.get('title', 'Notícia')
                    description = article.get('description', '')
                    url_link = article.get('url', '')
                    image = article.get('urlToImage', '')
                    source_name = article.get('source', {}).get('name', 'Fonte')
                    
                    # Como são notícias brasileiras, já estão em português
                    summary = description if description else "Clique para ler a notícia completa!"
                    if len(summary) > 250:
                        summary = summary[:250] + "..."
                    
                    categoria_emoji = {
                        'science': '🔬 Ciência',
                        'technology': '💻 Tecnologia',
                        'health': '🏥 Saúde'
                    }
                    
                    return {
                        'title': title,
                        'summary': summary,
                        'url': url_link,
                        'image_url': image,
                        'source': categoria_emoji.get(categoria, '📰 Notícias'),
                        'source_name': source_name,
                        'category': categoria_emoji.get(categoria, '📰')
                    }
        except Exception as e:
            print(f"❌ Erro ao buscar notícias gerais: {e}")
        return None
    
    async def post_curated_news(self, channel):
        """Postar notícias curadas com tradução corrigida"""
        try:
            # Alternar entre NASA e notícias gerais
            if random.choice([True, False]):
                news = await self.fetch_nasa_news()
                is_nasa = True
            else:
                news = await self.fetch_general_news()
                is_nasa = False
            
            if news:
                color = 0x0066cc if is_nasa else 0x00cc66
                title_prefix = "🚀" if is_nasa else news.get('category', '📰').split()[0]
                
                embed = discord.Embed(
                    title=f"{title_prefix} {news['title']}",
                    description=f"**{news['summary']}**",
                    color=color,
                    timestamp=datetime.now()
                )
                
                if is_nasa:
                    embed.add_field(
                        name="📅 Data",
                        value=news.get('date', 'Não informada'),
                        inline=True
                    )
                    if news.get('original_title'):
                        embed.add_field(
                            name="🔤 Título Original",
                            value=news['original_title'][:100] + "..." if len(news['original_title']) > 100 else news['original_title'],
                            inline=True
                        )
                else:
                    if news.get('source_name'):
                        embed.add_field(
                            name="📰 Fonte",
                            value=news['source_name'],
                            inline=True
                        )
                
                embed.add_field(
                    name="📊 Categoria",
                    value=news['source'],
                    inline=True
                )
                
                if news.get('image_url'):
                    embed.set_image(url=news['image_url'])
                
                if news.get('url'):
                    embed.add_field(
                        name="🔗 Leia mais",
                        value=f"[👆 Clique aqui para ver a notícia completa]({news['url']})",
                        inline=False
                    )
                
                embed.set_footer(
                    text="📡 KaBot Radar | Criado por Kazinho",
                    icon_url=bot.user.avatar.url if bot.user.avatar else None
                )
                
                message = await channel.send(embed=embed)
                
                # Reações
                await message.add_reaction('👍')
                await message.add_reaction('🤔')
                await message.add_reaction('📚')
                if is_nasa:
                    await message.add_reaction('🚀')
                else:
                    await message.add_reaction('💡')
                
                print(f"📰 Notícia postada: {news['title'][:50]}...")
            
        except Exception as e:
            print(f"❌ Erro ao postar notícia: {e}")
    
    async def monkey_mode(self, channel):
        """Modo Monkey melhorado"""
        try:
            query = supabase.table('short_term_memory').select('*')
            if hasattr(channel, 'guild') and channel.guild:
                query = query.eq('guild_id', str(channel.guild.id))
            
            from datetime import datetime, timedelta
            tres_dias_atras = (datetime.now() - timedelta(days=3)).isoformat()
            
            result = query.gte('timestamp', tres_dias_atras).order('timestamp', desc=True).limit(100).execute()
            messages = result.data
            
            if not messages:
                return
            
            # Filtrar mensagens mais interessantes
            valid_messages = []
            for msg in messages:
                content = msg.get('content', '')
                if (len(content) > 15 and 
                    not content.startswith('/') and 
                    not content.startswith('!') and
                    'http' not in content.lower() and
                    len(content.split()) >= 4 and
                    not any(word in content.lower() for word in ['bot', 'kabot', 'comando'])):
                    valid_messages.append(msg)
            
            if not valid_messages:
                return
            
            chosen_message = random.choice(valid_messages)
            original_content = chosen_message['content']
            
            # Transformar mensagem ocasionalmente
            if random.random() < 0.3:  # 30% das vezes
                emojis = ["💭", "🤔", "✨", "💡", "🎯", "🌟"]
                transformed = f"{random.choice(emojis)} {original_content}"
            else:
                transformed = original_content
            
            await asyncio.sleep(random.uniform(1, 3))
            await channel.send(transformed)
            
        except Exception as e:
            print(f"❌ Erro no monkey mode: {e}")
    
    async def respond_to_mention(self, message):
        """Responder quando mencionado"""
        try:
            user_id = message.author.id
            
            # Verificar se é sobre o Kazinho
            if any(word in message.content.lower() for word in ['kazinho', 'criador', 'quem te criou', 'seu criador']):
                response = random.choice(self.kazinho_facts)
                await message.reply(response)
                self.learn_from_interaction(user_id, message.content, 'kazinho_mention')
                return
            
            # Respostas baseadas no aprendizado
            base_responses = [
                "Oi! 👋 Precisa de alguma coisa?",
                "Olá! 😊 Como posso ajudar?",
                "Eyyy! 🤗 O que está acontecendo?",
                "Opa! 🌟 Me chamou?",
                "Olá, meu amigo! 😄 Estou aqui!",
                "Oi! 💭 Vamos conversar?"
            ]
            
            # Gerar resposta personalizada
            response = self.get_personalized_response(user_id, base_responses)
            
            # Às vezes ativar monkey mode após responder
            if random.random() < 0.4:  # 40% das vezes
                await message.reply(response)
                await asyncio.sleep(2)
                await self.monkey_mode(message.channel)
            else:
                await message.reply(response)
            
            # Aprender da interação
            self.learn_from_interaction(user_id, message.content, 'mention')
            
        except Exception as e:
            print(f"❌ Erro ao responder menção: {e}")

# Instância do KaBot
kabot = KaBot()

# Contador de mensagens para o sistema monkey
message_counter = 0

# Configurações por servidor
server_configs = {}

def get_server_config(guild_id):
    """Obter configurações do servidor"""
    if guild_id not in server_configs:
        server_configs[guild_id] = {
            'monkey_enabled': True,
            'monkey_interval': 7,
            'news_channel_id': 1383152826099826818
        }
    return server_configs[guild_id]

@bot.event
async def on_ready():
    print(f'{bot.user} está online!')
    print(f'KaBot conectado em {len(bot.guilds)} servidor(s)')
    
    # Sincronizar comandos slash
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comando(s) slash sincronizado(s)")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")
    
    # Iniciar tarefas em segundo plano
    news_radar.start()
    print("📡 Radar de Informações ativado!")

@bot.event
async def on_message(message):
    # Ignorar mensagens do próprio bot
    if message.author == bot.user:
        return
    
    # Verificar se o bot foi mencionado
    if bot.user.mentioned_in(message):
        await kabot.respond_to_mention(message)
        return
    
    # Salvar mensagem na memória
    await kabot.save_message_to_memory(message)
    
    # Sistema Monkey
    if message.guild:
        config = get_server_config(message.guild.id)
        
        if config['monkey_enabled']:
            global message_counter
            message_counter += 1
            
            if message_counter >= config['monkey_interval']:
                message_counter = 0
                await kabot.monkey_mode(message.channel)
    
    await bot.process_commands(message)

# Comandos Slash
@bot.tree.command(name="memoria", description="📚 Ver as lembranças recentes que o KaBot guardou")
@discord.app_commands.describe(quantidade="Número de lembranças para mostrar (1-10)")
async def memoria_slash(interaction: discord.Interaction, quantidade: discord.app_commands.Range[int, 1, 10] = 5):
    """Mostrar resumo da memória de longo prazo"""
    await interaction.response.defer()
    
    try:
        memories = await kabot.get_long_term_memory(interaction.guild.id if interaction.guild else None, quantidade)
        
        if memories:
            embed = discord.Embed(
                title="🧠 Memória do KaBot",
                description="Aqui estão algumas lembranças recentes:",
                color=0x3498db
            )
            
            for memory in memories:
                embed.add_field(
                    name=f"📅 {memory.get('date', 'Data desconhecida')}",
                    value=memory.get('summary', 'Sem resumo disponível')[:100] + "...",
                    inline=False
                )
        else:
            embed = discord.Embed(
                title="🧠 Memória do KaBot",
                description="Ainda não tenho lembranças significativas deste servidor.",
                color=0xe74c3c
            )
        
        await interaction.followup.send(embed=embed)
    except Exception as e:
        print(f"Erro no comando /memoria: {e}")
        await interaction.followup.send("❌ Erro ao buscar memórias. Tente novamente!")

@bot.tree.command(name="noticias", description="📰 Buscar notícias frescas e interessantes")
async def noticias_slash(interaction: discord.Interaction):
    """Buscar notícias manualmente"""
    await interaction.response.defer()
    await interaction.followup.send("🔍 Buscando notícias frescas...")
    await kabot.post_curated_news(interaction.channel)

@bot.tree.command(name="ping", description="🏓 Verificar se o KaBot está respondendo bem")
async def ping_slash(interaction: discord.Interaction):
    """Verificar latência do bot"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latência: {latency}ms",
        color=0x00ff00
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ajuda", description="❓ Ver todos os comandos disponíveis do KaBot")
async def ajuda_slash(interaction: discord.Interaction):
    """Mostrar comandos disponíveis"""
    embed = discord.Embed(
        title="🤖 KaBot - Comandos Disponíveis",
        description="Aqui estão os comandos que posso executar:",
        color=0x9932cc
    )
    
    commands_list = [
        ("📚 /memoria [quantidade]", "Ver minhas lembranças do servidor"),
        ("📰 /noticias", "Buscar notícias frescas"),
        ("🏓 /ping", "Verificar minha latência"),
        ("❓ /ajuda", "Mostrar esta mensagem"),
        ("🚀 /nasa", "Buscar notícias interessantes da NASA"),
        ("🎲 /curiosidade", "Receber uma curiosidade aleatória"),
        ("😂 /meme", "Ouvir uma piada engraçada"),
        ("💡 /conselho", "Receber um conselho sábio"),
        ("⚡ /energia", "Receber uma dose de motivação"),
        ("🐒 /monkey", "Modo macaco - repete algo interessante do chat"),
        ("⚙️ /config_monkey", "Configurar sistema monkey (Admin)"),
        ("🎲 /roleta", "Jogar uma moeda - sim ou não"),
        ("🎉 /sorteio [quantidade]", "Sortear pessoas aleatórias do servidor"),
        ("🌍 /traduzir", "Traduzir texto para português"),
        ("🧠 /quiz", "Iniciar um quiz de conhecimentos gerais"),
        ("🎯 /sobre_kazinho", "Saber mais sobre meu criador"),
        ("👑 /assistindo", "Alterar status do bot (Kazinho only)"),
        ("👑 /perfil", "Alterar avatar do bot (Kazinho only)"),
        ("👑 /mensagem", "Enviar mensagem em canal (Kazinho only)")
    ]
    
    for command, description in commands_list:
        embed.add_field(name=command, value=description, inline=False)
    
    embed.set_footer(text="💡 Dica: Me mencione (@KaBot) para ativar respostas inteligentes!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="sobre_kazinho", description="🎯 Saber mais sobre meu incrível criador")
async def sobre_kazinho_slash(interaction: discord.Interaction):
    """Informações sobre o Kazinho"""
    embed = discord.Embed(
        title="👑 Sobre o Kazinho - Meu Criador",
        description="Deixe-me contar sobre a pessoa incrível que me criou!",
        color=0xffd700
    )
    
    embed.add_field(
        name="🧠 Gênio da Programação",
        value="Kazinho é o mastermind por trás de toda minha inteligência! Ele me programou com muito carinho e dedicação.",
        inline=False
    )
    
    embed.add_field(
        name="💡 Sempre Inovando",
        value="Ele sempre tem as melhores ideias para me melhorar e me deixar mais útil para todos vocês!",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Visionário",
        value="Kazinho teve a visão de criar um bot que não apenas executa comandos, mas que aprende e evolui com a comunidade!",
        inline=False
    )
    
    embed.add_field(
        name="📱 Discord ID",
        value="<@857228143478571029>",
        inline=True
    )
    
    embed.add_field(
        name="🏆 Conquista Especial",
        value="Criou o bot mais legal do Discord! 😄",
        inline=True
    )
    
    embed.set_footer(text="Devo tudo ao meu criador Kazinho! ❤️")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="nasa", description="🚀 Descobrir algo incrível sobre o espaço")
async def nasa_slash(interaction: discord.Interaction):
    """Comando slash para buscar notícias da NASA"""
    await interaction.response.defer()
    
    try:
        news = await kabot.fetch_nasa_news()
        
        if news:
            embed = discord.Embed(
                title=f"🚀 {news['title']}",
                description=news['summary'],
                color=0x1f8b4c,
                timestamp=datetime.now()
            )
            
            embed.set_footer(text=f"Fonte: {news['source']} | KaBot")
            
            if 'image_url' in news and news['image_url']:
                embed.set_image(url=news['image_url'])
            
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Não consegui buscar notícias da NASA no momento. Tente novamente mais tarde!")
            
    except Exception as e:
        print(f"Erro no comando /nasa: {e}")
        await interaction.followup.send("❌ Ocorreu um erro ao buscar as notícias. Tente novamente!")

@bot.tree.command(name="curiosidade", description="🎲 Receber uma curiosidade interessante e aleatória")
async def curiosidade_slash(interaction: discord.Interaction):
    """Comando para compartilhar curiosidades"""
    curiosidades = [
        "🐙 Os polvos têm três corações e sangue azul!",
        "🌍 Um dia em Vênus (243 dias terrestres) é mais longo que um ano em Vênus (225 dias terrestres)!",
        "🧠 Seu cérebro usa cerca de 20% de toda a energia do seu corpo!",
        "🐝 As abelhas podem reconhecer rostos humanos!",
        "🌊 Conhecemos menos de 5% dos nossos oceanos!",
        "⚡ Um raio é 5 vezes mais quente que a superfície do Sol!",
        "🦈 Tubarões existem há mais tempo que as árvores!",
        "🌙 A Lua está se afastando da Terra cerca de 3,8 cm por ano!",
        "🐧 Pinguins podem pular até 3 metros de altura!",
        "💎 Chove diamantes em Netuno e Urano!",
        "🦒 As girafas só dormem 30 minutos por dia!",
        "🍯 O mel nunca estraga - foram encontrados potes de mel comestível em tumbas egípcias!",
        "🐸 Existe uma rã que pode sobreviver sendo congelada sólida!",
        "🌋 Existem mais vulcões em Vênus do que em qualquer outro planeta!",
        "🧬 Você compartilha 50% do seu DNA com uma banana!",
        f"👑 Meu criador Kazinho é um gênio da programação e me criou com muito amor! ❤️"
    ]
    
    curiosidade = random.choice(curiosidades)
    
    embed = discord.Embed(
        title="🎲 Curiosidade do KaBot!",
        description=curiosidade,
        color=0xf39c12
    )
    
    embed.set_footer(text="Que incrível, não é? 🤓")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="meme", description="😂 Receber um meme aleatório ou uma piada")
async def meme_slash(interaction: discord.Interaction):
    """Comando para piadas e memes"""
    piadas = [
        "Por que os pássaros voam para o sul no inverno? 🐦\nPorque é longe demais para andar! 😂",
        "O que o pato disse para a pata? 🦆\nVem quá! 😄",
        "Por que o livro de matemática estava triste? 📚\nPorque tinha muitos problemas! 😅",
        "O que a impressora falou para a outra impressora? 🖨️\nEssa folha é sua ou é impressão minha? 😂",
        "Por que o café foi para a terapia? ☕\nPorque estava muito coado! 😄",
        "O que o oceano disse para a praia? 🌊\nNada, só acenou! 👋",
        "Por que o programador quebrou a perna? 💻\nPorque esqueceu de colocar um break! 😂",
        "O que é que fica maior quanto mais você tira? 🕳️\nUm buraco! 😄",
        "Por que o Kazinho é o melhor programador? 👑\nPorque criou o KaBot! 😎"
    ]
    
    piada = random.choice(piadas)
    
    embed = discord.Embed(
        title="😂 Hora do Meme!",
        description=piada,
        color=0xff6b6b
    )
    
    embed.set_footer(text="Espero que tenha dado uma risada! 😄")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="conselho", description="💡 Receber um conselho sábio e motivacional")
async def conselho_slash(interaction: discord.Interaction):
    """Comando para conselhos motivacionais"""
    conselhos = [
        "💪 A única forma de fazer um excelente trabalho é amar o que você faz!",
        "🌱 Todo grande carvalho já foi uma pequena bolota que não desistiu!",
        "✨ Você é mais forte do que imagina e mais capaz do que acredita!",
        "🎯 O sucesso é a soma de pequenos esforços repetidos dia após dia!",
        "🌟 Não espere por oportunidades, crie-as!",
        "🚀 O único limite para o que você pode alcançar é o que você acredita ser possível!",
        "💎 Pressão faz diamantes - você está se tornando mais forte!",
        "🌈 Depois da tempestade sempre vem o arco-íris!",
        "📈 Cada erro é uma lição, cada obstáculo é uma oportunidade de crescer!",
        "🔥 Acredite em si mesmo e você já terá percorrido metade do caminho!",
        "👑 Seja como o Kazinho - tenha visão e transforme ideias em realidade!"
    ]
    
    conselho = random.choice(conselhos)
    
    embed = discord.Embed(
        title="💡 Conselho do KaBot",
        description=conselho,
        color=0x00d4aa
    )
    
    embed.set_footer(text="Você consegue! 💪")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="energia", description="⚡ Receber uma dose de energia e motivação")
async def energia_slash(interaction: discord.Interaction):
    """Comando para dar energia e motivação"""
    mensagens_energia = [
        "⚡ VOCÊ É INCRÍVEL! Hoje é o seu dia de brilhar! ✨",
        "🔥 ENERGIA MÁXIMA! Você tem tudo que precisa para conquistar seus objetivos! 🎯",
        "💥 BOOM! Hora de mostrar do que você é capaz! Vai com tudo! 🚀",
        "⭐ VOCÊ É UMA ESTRELA! Brilhe como nunca e inspire todos ao seu redor! 🌟",
        "💪 FORÇA TOTAL! Nada pode te parar quando você decide ir atrás do que quer! 🎊",
        "🌈 POSITIVIDADE NO MÁXIMO! Você transforma qualquer dia em algo especial! ✨",
        "🎵 RITMO DE VITÓRIA! Dance através dos desafios e celebre cada conquista! 🎉",
        "🦄 MAGIA PURA! Você tem o poder de tornar o impossível possível! ✨",
        "👑 ENERGIA DO KAZINHO! Seja criativo e inovador como meu criador! 🚀"
    ]
    
    mensagem = random.choice(mensagens_energia)
    
    embed = discord.Embed(
        title="⚡ BOMBA DE ENERGIA!",
        description=mensagem,
        color=0xff9f43
    )
    
    embed.set_footer(text="Agora vai lá e arrasa! 🔥")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="monkey", description="🐒 Ativar modo macaco - repete algo interessante que alguém disse")
async def monkey_slash(interaction: discord.Interaction):
    """Comando manual para ativar o monkey mode"""
    await interaction.response.send_message("🐒 Ativando modo macaco... deixa eu ver o que já foi dito aqui...")
    await kabot.monkey_mode(interaction.channel)

@bot.tree.command(name="config_monkey", description="⚙️ Configurar o sistema monkey")
@discord.app_commands.describe(
    ativado="Ativar ou desativar o monkey mode",
    intervalo="Número de mensagens entre ativações (3-20)"
)
async def config_monkey_slash(interaction: discord.Interaction, ativado: bool, intervalo: discord.app_commands.Range[int, 3, 20] = 7):
    """Configurar sistema monkey"""
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("❌ Você precisa de permissão para gerenciar servidor!", ephemeral=True)
        return
    
    config = get_server_config(interaction.guild.id)
    config['monkey_enabled'] = ativado
    config['monkey_interval'] = intervalo
    
    status = "ativado" if ativado else "desativado"
    
    embed = discord.Embed(
        title="⚙️ Monkey Mode Configurado",
        description=f"Sistema monkey **{status}**\nIntervalo: a cada **{intervalo}** mensagens",
        color=0x00ff00 if ativado else 0xff0000
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roleta", description="🎲 Jogar uma moeda - sim ou não")
async def roleta_slash(interaction: discord.Interaction):
    """Comando de roleta sim/não"""
    resultado = random.choice(["SIM", "NÃO"])
    cor = 0x00ff00 if resultado == "SIM" else 0xff0000
    emoji = "✅" if resultado == "SIM" else "❌"
    
    embed = discord.Embed(
        title="🎲 Roleta do KaBot",
        description=f"## {emoji} {resultado}",
        color=cor
    )
    
    embed.set_footer(text="A sorte foi lançada!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="sorteio", description="🎉 Sortear pessoas aleatórias do servidor")
@discord.app_commands.describe(quantidade="Quantas pessoas sortear (máximo 10)")
async def sorteio_slash(interaction: discord.Interaction, quantidade: discord.app_commands.Range[int, 1, 10] = 1):
    """Comando de sorteio corrigido"""
    try:
        await interaction.response.defer()
        
        # Garantir que o guild esteja disponível
        if not interaction.guild:
            await interaction.followup.send("❌ Este comando só funciona em servidores!", ephemeral=True)
            return
        
        # Pegar todos os membros que não são bots
        members = [member for member in interaction.guild.members if not member.bot and member.status != discord.Status.offline]
        
        if not members:
            await interaction.followup.send("❌ Nenhum membro online encontrado no servidor!", ephemeral=True)
            return
        
        # Se a quantidade for maior que o número de membros disponíveis
        if quantidade > len(members):
            quantidade = len(members)
        
        # Sortear membros únicos
        winners = random.sample(members, quantidade)
        
        embed = discord.Embed(
            title="🎉 Resultado do Sorteio",
            color=0xffd700,
            timestamp=datetime.now()
        )
        
        if quantidade == 1:
            embed.description = f"**🏆 Ganhador:** {winners[0].mention}"
        else:
            ganhadores_text = "\n".join([f"🏆 **{i+1}º lugar:** {winner.mention}" for i, winner in enumerate(winners)])
            embed.description = f"**Ganhadores sorteados:**\n\n{ganhadores_text}"
        
        embed.add_field(
            name="📊 Informações",
            value=f"**Total de membros online:** {len(members)}\n**Pessoas sorteadas:** {quantidade}",
            inline=False
        )
        
        embed.set_footer(text="Sorteio realizado pelo KaBot | Criado por Kazinho")
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"Erro no sorteio: {e}")
        try:
            await interaction.followup.send("❌ Erro ao realizar sorteio! Tente novamente.", ephemeral=True)
        except:
            pass

@bot.tree.command(name="traduzir", description="🌍 Traduzir texto para português")
@discord.app_commands.describe(texto="Texto que você quer traduzir para português")
async def traduzir_slash(interaction: discord.Interaction, texto: str):
    """Comando para traduzir texto"""
    try:
        await interaction.response.defer()
        
        # Traduzir usando o sistema melhorado
        texto_traduzido = await kabot.translate_text(texto)
        
        embed = discord.Embed(
            title="🌍 Tradução para Português",
            color=0x3498db
        )
        
        embed.add_field(
            name="📝 Texto Original",
            value=f"```{texto[:500] + '...' if len(texto) > 500 else texto}```",
            inline=False
        )
        
        embed.add_field(
            name="🇧🇷 Tradução",
            value=f"```{texto_traduzido[:500] + '...' if len(texto_traduzido) > 500 else texto_traduzido}```",
            inline=False
        )
        
        embed.set_footer(text="Tradução feita pelo KaBot | Criado por Kazinho")
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"Erro no comando traduzir: {e}")
        try:
            await interaction.followup.send("❌ Erro ao traduzir texto! Tente novamente.", ephemeral=True)
        except:
            pass

@bot.tree.command(name="quiz", description="🧠 Iniciar um quiz de conhecimentos gerais")
async def quiz_slash(interaction: discord.Interaction):
    """Comando para quiz de conhecimentos"""
    perguntas = [
        {
            "pergunta": "Qual é o planeta mais próximo do Sol?",
            "opcoes": ["A) Vênus", "B) Mercúrio", "C) Terra", "D) Marte"],
            "resposta": "B",
            "explicacao": "Mercúrio é o planeta mais próximo do Sol!"
        },
        {
            "pergunta": "Quantos corações tem um polvo?",
            "opcoes": ["A) 1", "B) 2", "C) 3", "D) 4"],
            "resposta": "C",
            "explicacao": "Os polvos têm 3 corações e sangue azul!"
        },
        {
            "pergunta": "Qual é o maior planeta do sistema solar?",
            "opcoes": ["A) Saturno", "B) Júpiter", "C) Netuno", "D) Urano"],
            "resposta": "B",
            "explicacao": "Júpiter é o maior planeta do nosso sistema solar!"
        },
        {
            "pergunta": "Em que ano o homem pisou na Lua pela primeira vez?",
            "opcoes": ["A) 1967", "B) 1968", "C) 1969", "D) 1970"],
            "resposta": "C",
            "explicacao": "Neil Armstrong pisou na Lua em 20 de julho de 1969!"
        },
        {
            "pergunta": "Quem criou o KaBot?",
            "opcoes": ["A) Um alien", "B) Kazinho", "C) Um robô", "D) Ninguém"],
            "resposta": "B",
            "explicacao": "Kazinho é meu incrível criador! Um gênio da programação! 👑"
        }
    ]
    
    pergunta = random.choice(perguntas)
    
    embed = discord.Embed(
        title="🧠 Quiz do KaBot",
        description=f"**{pergunta['pergunta']}**",
        color=0xe74c3c
    )
    
    opcoes_texto = "\n".join(pergunta['opcoes'])
    embed.add_field(
        name="📋 Opções:",
        value=opcoes_texto,
        inline=False
    )
    
    embed.set_footer(text="Responda com A, B, C ou D! Você tem 30 segundos.")
    
    await interaction.response.send_message(embed=embed)
    
    # Aguardar resposta
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel and m.content.upper() in ['A', 'B', 'C', 'D']
    
    try:
        response = await bot.wait_for('message', check=check, timeout=30.0)
        
        if response.content.upper() == pergunta['resposta']:
            result_embed = discord.Embed(
                title="🎉 Parabéns!",
                description=f"**Resposta correta!** ✅\n\n💡 **Explicação:** {pergunta['explicacao']}",
                color=0x00ff00
            )
        else:
            result_embed = discord.Embed(
                title="❌ Não foi dessa vez!",
                description=f"**Resposta correta:** {pergunta['resposta']}\n\n💡 **Explicação:** {pergunta['explicacao']}",
                color=0xff0000
            )
        
        await interaction.channel.send(embed=result_embed)
        
    except asyncio.TimeoutError:
        timeout_embed = discord.Embed(
            title="⏰ Tempo esgotado!",
            description=f"**Resposta correta:** {pergunta['resposta']}\n\n💡 **Explicação:** {pergunta['explicacao']}",
            color=0xffaa00
        )
        await interaction.channel.send(embed=timeout_embed)

# COMANDOS ADMINISTRATIVOS (APENAS PARA KAZINHO)
KAZINHO_ID = 857228143478571029

def is_kazinho():
    """Decorator para verificar se é o Kazinho"""
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == KAZINHO_ID
    return discord.app_commands.check(predicate)

@bot.tree.command(name="assistindo", description="👑 [ADMIN] Alterar status 'Assistindo' do bot")
@discord.app_commands.describe(atividade="O que o bot estará assistindo")
@is_kazinho()
async def assistindo_slash(interaction: discord.Interaction, atividade: str):
    """Comando para alterar o status do bot (apenas Kazinho)"""
    try:
        activity = discord.Activity(type=discord.ActivityType.watching, name=atividade)
        await bot.change_presence(activity=activity)
        
        embed = discord.Embed(
            title="👑 Status Alterado",
            description=f"Agora estou assistindo: **{atividade}**",
            color=0x9932cc
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro ao alterar status: {e}")
        await interaction.response.send_message("❌ Erro ao alterar status!", ephemeral=True)

@bot.tree.command(name="perfil", description="👑 [ADMIN] Alterar foto de perfil do bot")
@discord.app_commands.describe(imagem="Anexe a nova imagem de perfil")
@is_kazinho()
async def perfil_slash(interaction: discord.Interaction, imagem: discord.Attachment):
    """Comando para alterar avatar do bot (apenas Kazinho)"""
    try:
        if not imagem.content_type.startswith('image/'):
            await interaction.response.send_message("❌ Por favor, envie apenas arquivos de imagem!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Baixar a imagem
        image_data = await imagem.read()
        
        # Alterar avatar
        await bot.user.edit(avatar=image_data)
        
        embed = discord.Embed(
            title="👑 Avatar Alterado",
            description="Foto de perfil atualizada com sucesso!",
            color=0x9932cc
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro ao alterar avatar: {e}")
        await interaction.followup.send("❌ Erro ao alterar avatar! Verifique se a imagem é válida.", ephemeral=True)

@bot.tree.command(name="mensagem", description="👑 [ADMIN] Enviar mensagem para um canal específico")
@discord.app_commands.describe(
    canal_id="ID do canal onde enviar a mensagem",
    mensagem="Conteúdo da mensagem"
)
@is_kazinho()
async def mensagem_slash(interaction: discord.Interaction, canal_id: str, mensagem: str):
    """Comando para enviar mensagem em canal específico (apenas Kazinho)"""
    try:
        # Converter ID para int
        channel_id = int(canal_id)
        channel = bot.get_channel(channel_id)
        
        if not channel:
            await interaction.response.send_message("❌ Canal não encontrado!", ephemeral=True)
            return
        
        # Verificar se o bot tem permissão para enviar mensagens
        if not channel.permissions_for(channel.guild.me).send_messages:
            await interaction.response.send_message("❌ Não tenho permissão para enviar mensagens neste canal!", ephemeral=True)
            return
        
        # Enviar mensagem
        await channel.send(mensagem)
        
        embed = discord.Embed(
            title="👑 Mensagem Enviada",
            description=f"Mensagem enviada para {channel.mention} com sucesso!",
            color=0x9932cc
        )
        embed.add_field(name="Conteúdo", value=mensagem[:100] + "..." if len(mensagem) > 100 else mensagem)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except ValueError:
        await interaction.response.send_message("❌ ID do canal inválido!", ephemeral=True)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        await interaction.response.send_message("❌ Erro ao enviar mensagem!", ephemeral=True)

@tasks.loop(hours=3)
async def news_radar():
    """Radar de Informações - Buscar e postar notícias automaticamente"""
    try:
        # Buscar canais específicos para cada servidor
        for guild in bot.guilds:
            config = get_server_config(guild.id)
            
            # Tentar usar canal configurado primeiro
            channel = None
            if config.get('news_channel_id'):
                channel = bot.get_channel(config['news_channel_id'])
            
            # Se não encontrar canal configurado, procurar por padrões
            if not channel:
                for ch in guild.text_channels:
                    if ch.name.lower() in ['geral', 'general', 'noticias', 'notícias', 'news']:
                        channel = ch
                        break
                
                if not channel:
                    # Se não encontrar, usar o primeiro canal de texto disponível
                    channel = guild.text_channels[0] if guild.text_channels else None
            
            if channel:
                try:
                    await kabot.post_curated_news(channel)
                    await asyncio.sleep(2)  # Pequena pausa entre servidores
                except Exception as e:
                    print(f"Erro ao postar notícia no servidor {guild.name}: {e}")
    
    except Exception as e:
        print(f"Erro no radar de notícias: {e}")

@news_radar.before_loop
async def before_news_radar():
    await bot.wait_until_ready()

# Função para processamento diário da memória (placeholder para futuro)
def daily_memory_processing():
    """Processar memória diária - placeholder para implementação futura com IA"""
    print("Processamento diário da memória executado (placeholder)")

# Configurar agendamento
schedule.every().day.at("02:00").do(daily_memory_processing)

def run_scheduler():
    """Executar agendador em thread separada"""
    while True:
        schedule.run_pending()
        time.sleep(60)

# Iniciar thread do agendador
scheduler_thread = Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == "__main__":
    print("Iniciando KaBot...")
    bot.run(DISCORD_TOKEN)
