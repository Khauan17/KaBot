
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

bot = commands.Bot(command_prefix='!ka ', intents=intents)

class KaBot:
    def __init__(self):
        self.setup_database()
    
    def setup_database(self):
        """Criar tabelas necessárias no Supabase"""
        try:
            # Tabela para memória de curto prazo (mensagens brutas)
            supabase.table('short_term_memory').select('*').limit(1).execute()
        except:
            print("Tabelas já existem ou foram criadas automaticamente")
    
    async def translate_text(self, text, source_lang="auto", target_lang="pt"):
        """Traduzir texto usando LibreTranslate API"""
        try:
            # Se o texto for muito curto ou já em português, retornar original
            if len(text.strip()) < 5:
                return text
            
            # Tentar usar LibreTranslate
            import requests
            import json
            
            url = "https://libretranslate.com/translate"
            data = {
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "format": "text"
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get("translatedText", text)
                return translated_text
            else:
                print(f"Erro na API de tradução: {response.status_code}")
                return self.fallback_translate(text)
                
        except Exception as e:
            print(f"Erro ao traduzir: {e}")
            return self.fallback_translate(text)
    
    def fallback_translate(self, text):
        """Tradução de fallback usando palavras-chave comuns"""
        common_translations = {
            "space": "espaço",
            "NASA": "NASA",
            "earth": "Terra",
            "moon": "lua",
            "sun": "sol",
            "planet": "planeta",
            "galaxy": "galáxia",
            "telescope": "telescópio",
            "mission": "missão",
            "science": "ciência",
            "astronomy": "astronomia",
            "discovery": "descoberta",
            "asteroid": "asteroide",
            "comet": "cometa",
            "satellite": "satélite",
            "rocket": "foguete",
            "orbit": "órbita",
            "spacecraft": "espaçonave",
            "universe": "universo",
            "stellar": "estelar",
            "solar": "solar",
            "lunar": "lunar",
            "cosmic": "cósmico",
            "radiation": "radiação",
            "atmosphere": "atmosfera",
            "the": "o/a",
            "and": "e",
            "of": "de",
            "in": "em",
            "to": "para",
            "is": "é",
            "was": "foi",
            "are": "são",
            "were": "eram",
            "this": "este/esta",
            "that": "aquele/aquela",
            "with": "com",
            "from": "de",
            "by": "por",
            "an": "um/uma",
            "as": "como",
            "for": "para",
            "on": "em",
            "at": "em"
        }
        
        translated = text
        for eng, pt in common_translations.items():
            # Substituir palavras completas, não partes de palavras
            import re
            pattern = r'\b' + re.escape(eng) + r'\b'
            translated = re.sub(pattern, pt, translated, flags=re.IGNORECASE)
        
        return translated
    
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
                "username": message.author.display_name[:50],  # Limitar tamanho
                "content": message.content[:1000],  # Limitar tamanho para evitar problemas
                "timestamp": message.created_at.isoformat(),
                "message_id": str(message.id)
            }
            
            result = supabase.table('short_term_memory').insert(data).execute()
            
        except Exception as e:
            # Silenciar erros de salvamento para não poluir o log
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
            # Retornar lista vazia se não houver memórias ainda
            return []
    
    async def fetch_nasa_news(self):
        """Buscar notícias da NASA"""
        try:
            url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&count=1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()[0]
                
                title = data.get('title', 'Notícia da NASA')
                explanation = data.get('explanation', '')
                image_url = data.get('url', '')
                
                # Traduzir título e explicação para português
                try:
                    title_pt = await self.translate_text(title, "en", "pt")
                    explanation_pt = await self.translate_text(explanation, "en", "pt")
                except:
                    # Se falhar a tradução, usar texto original
                    title_pt = title
                    explanation_pt = explanation
                
                # Criar resumo breve (primeiras 200 caracteres)
                summary = explanation_pt[:200] + "..." if len(explanation_pt) > 200 else explanation_pt
                
                return {
                    'title': title_pt,
                    'summary': summary,
                    'image_url': image_url,
                    'source': 'NASA',
                    'date': data.get('date', datetime.now().strftime('%Y-%m-%d'))
                }
        except Exception as e:
            print(f"Erro ao buscar notícias da NASA: {e}")
        return None
    
    async def fetch_general_news(self):
        """Buscar notícias gerais"""
        try:
            # Alternar entre diferentes categorias para variedade
            categorias = ['science', 'technology', 'health']
            categoria = random.choice(categorias)
            
            url = f"https://newsapi.org/v2/top-headlines?country=br&category={categoria}&pageSize=5&apiKey={NEWS_API_KEY}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['articles']:
                    # Pegar um artigo aleatório dos resultados
                    article = random.choice(data['articles'][:3])
                    
                    title = article.get('title', 'Notícia')
                    description = article.get('description', '')
                    url_link = article.get('url', '')
                    image = article.get('urlToImage', '')
                    
                    return {
                        'title': f"📰 {title}",
                        'summary': description if description else "Clique no link para ler mais!",
                        'url': url_link,
                        'image_url': image,
                        'source': f'Notícias de {categoria.title()}',
                        'published': article.get('publishedAt', '')
                    }
        except Exception as e:
            print(f"Erro ao buscar notícias gerais: {e}")
        return None
    
    async def post_curated_news(self, channel):
        """Postar notícias curadas no canal"""
        try:
            # Alternar entre NASA e notícias gerais
            import random
            if random.choice([True, False]):
                news = await self.fetch_nasa_news()
            else:
                news = await self.fetch_general_news()
            
            if news:
                embed = discord.Embed(
                    title=f"📰 {news['title']}",
                    description=news['summary'],
                    color=0x1f8b4c,
                    timestamp=datetime.now()
                )
                
                embed.set_footer(text=f"Fonte: {news['source']} | KaBot criado por Kazinho")
                
                if 'image_url' in news and news['image_url']:
                    embed.set_image(url=news['image_url'])
                
                if 'url' in news and news['url']:
                    embed.add_field(
                        name="🔗 Leia mais",
                        value=f"[Clique aqui para ler a notícia completa]({news['url']})",
                        inline=False
                    )
                
                await channel.send(embed=embed)
                print(f"Notícia postada: {news['title']}")
            
        except Exception as e:
            print(f"Erro ao postar notícia: {e}")
    
    async def monkey_mode(self, channel):
        """Modo Monkey - repete uma mensagem aleatória de forma natural"""
        try:
            # Buscar mensagens recentes do banco
            query = supabase.table('short_term_memory').select('*')
            if hasattr(channel, 'guild') and channel.guild:
                query = query.eq('guild_id', str(channel.guild.id))
            
            # Pegar mensagens dos últimos 3 dias que não sejam comandos
            from datetime import datetime, timedelta
            tres_dias_atras = (datetime.now() - timedelta(days=3)).isoformat()
            
            result = query.gte('timestamp', tres_dias_atras).order('timestamp', desc=True).limit(50).execute()
            messages = result.data
            
            if not messages:
                return
            
            # Filtrar mensagens válidas (não comandos, não muito curtas)
            valid_messages = [
                msg for msg in messages 
                if len(msg.get('content', '')) > 10 
                and not msg.get('content', '').startswith('/')
                and not msg.get('content', '').startswith('!')
                and 'http' not in msg.get('content', '').lower()
                and len(msg.get('content', '').split()) >= 3
            ]
            
            if not valid_messages:
                return
            
            # Escolher uma mensagem aleatória
            import random
            chosen_message = random.choice(valid_messages)
            original_content = chosen_message['content']
            
            # Transformar a mensagem para parecer mais natural/IA
            transformed = await self.transform_message_ai_style(original_content)
            
            # Enviar com um delay pequeno para parecer mais natural
            await asyncio.sleep(random.uniform(1, 3))
            await channel.send(transformed)
            
        except Exception as e:
            print(f"Erro no monkey mode: {e}")
    
    async def transform_message_ai_style(self, original_message):
        """Retorna a mensagem de forma mais natural"""
        import random
        
        # Simplesmente adicionar um emoji ocasionalmente
        emojis = ["💭", "🤔", "✨", "💡", "🎯"]
        
        # 70% das vezes retornar sem modificação, 30% com emoji
        if random.random() < 0.7:
            return original_message
        else:
            return f"{random.choice(emojis)} {original_message}"

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
            'news_channel_id': 1383152826099826818  # Canal específico do seu servidor
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
    print("Radar de Informações ativado!")

@bot.event
async def on_message(message):
    # Ignorar mensagens do próprio bot
    if message.author == bot.user:
        return
    
    # Salvar mensagem na memória de curto prazo
    await kabot.save_message_to_memory(message)
    
    # Sistema Monkey - contar mensagens
    if message.guild:
        config = get_server_config(message.guild.id)
        
        if config['monkey_enabled']:
            global message_counter
            message_counter += 1
            
            # A cada X mensagens (configurável), ativar o monkey mode
            if message_counter >= config['monkey_interval']:
                message_counter = 0
                await kabot.monkey_mode(message.channel)
    
    # Processar comandos
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
    await interaction.response.send_message("🔍 Buscando notícias frescas...")
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
        ("🎉 /sorteio", "Sortear entre membros ou cargos"),
        ("🌍 /traduzir", "Traduzir texto para português"),
        ("🧠 /quiz", "Iniciar um quiz de conhecimentos gerais"),
        ("👑 /assistindo", "Alterar status do bot (Kazinho only)"),
        ("👑 /perfil", "Alterar avatar do bot (Kazinho only)"),
        ("👑 /mensagem", "Enviar mensagem em canal (Kazinho only)")
    ]
    
    for command, description in commands_list:
        embed.add_field(name=command, value=description, inline=False)
    
    embed.set_footer(text="KaBot - Seu assistente inteligente e curioso!")
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
        "🧬 Você compartilha 50% do seu DNA com uma banana!"
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
        "O que é que fica maior quanto mais você tira? 🕳️\nUm buraco! 😄"
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
        "🔥 Acredite em si mesmo e você já terá percorrido metade do caminho!"
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
        "🦄 MAGIA PURA! Você tem o poder de tornar o impossível possível! ✨"
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
    import random
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

@bot.tree.command(name="sorteio", description="🎉 Sortear entre membros ou cargos")
async def sorteio_slash(interaction: discord.Interaction, tipo: str, valor: str):
    """Comando de sorteio"""
    import random
    
    try:
        if tipo == "cargo":
            # Buscar cargo por nome
            role = discord.utils.get(interaction.guild.roles, name=valor)
            if not role:
                await interaction.response.send_message(f"❌ Cargo '{valor}' não encontrado!", ephemeral=True)
                return
            
            members = [member for member in role.members if not member.bot]
            if not members:
                await interaction.response.send_message("❌ Nenhum membro encontrado neste cargo!", ephemeral=True)
                return
            
            winner = random.choice(members)
            
            embed = discord.Embed(
                title="🎉 Resultado do Sorteio",
                description=f"**Ganhador:** {winner.mention}\n**Cargo:** {role.name}\n**Participantes:** {len(members)}",
                color=0xffd700
            )
            
        elif tipo == "usuarios":
            # Extrair mentions da string
            user_ids = []
            words = valor.split()
            for word in words:
                if word.startswith('<@') and word.endswith('>'):
                    try:
                        user_id = int(word.strip('<@!>'))
                        user = interaction.guild.get_member(user_id)
                        if user and not user.bot:
                            user_ids.append(user)
                    except:
                        pass
            
            if not user_ids:
                await interaction.response.send_message("❌ Nenhum usuário válido mencionado! Use: @usuario1 @usuario2", ephemeral=True)
                return
            
            winner = random.choice(user_ids)
            
            embed = discord.Embed(
                title="🎉 Resultado do Sorteio",
                description=f"**Ganhador:** {winner.mention}\n**Participantes:** {len(user_ids)}",
                color=0xffd700
            )
            
        embed.set_footer(text="Sorteio realizado pelo KaBot | Criado por Kazinho")
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        print(f"Erro no sorteio: {e}")
        await interaction.response.send_message("❌ Erro ao realizar sorteio!", ephemeral=True)

@sorteio_slash.autocomplete('tipo')
async def sorteio_tipo_autocomplete(interaction: discord.Interaction, current: str):
    choices = [
        discord.app_commands.Choice(name="Cargo (sortear entre membros de um cargo)", value="cargo"),
        discord.app_commands.Choice(name="Usuários (sortear entre usuários mencionados)", value="usuarios")
    ]
    return [choice for choice in choices if current.lower() in choice.name.lower()]

@bot.tree.command(name="traduzir", description="🌍 Traduzir texto para português")
@discord.app_commands.describe(texto="Texto que você quer traduzir para português")
async def traduzir_slash(interaction: discord.Interaction, texto: str):
    """Comando para traduzir texto"""
    try:
        # Usar a função de tradução do KaBot
        texto_traduzido = await kabot.translate_text(texto, "auto", "pt")
        
        embed = discord.Embed(
            title="🌍 Tradução",
            color=0x3498db
        )
        
        embed.add_field(
            name="📝 Texto Original",
            value=texto[:500] + "..." if len(texto) > 500 else texto,
            inline=False
        )
        
        embed.add_field(
            name="🇧🇷 Tradução",
            value=texto_traduzido[:500] + "..." if len(texto_traduzido) > 500 else texto_traduzido,
            inline=False
        )
        
        embed.set_footer(text="Tradução feita pelo KaBot")
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        print(f"Erro no comando traduzir: {e}")
        await interaction.response.send_message("❌ Erro ao traduzir texto!", ephemeral=True)

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
            "pergunta": "Qual é o maior oceano do mundo?",
            "opcoes": ["A) Atlântico", "B) Índico", "C) Ártico", "D) Pacífico"],
            "resposta": "D",
            "explicacao": "O Oceano Pacífico é o maior oceano do mundo!"
        },
        {
            "pergunta": "Quantos ossos tem o corpo humano adulto?",
            "opcoes": ["A) 196", "B) 206", "C) 216", "D) 226"],
            "resposta": "B",
            "explicacao": "O corpo humano adulto tem 206 ossos!"
        },
        {
            "pergunta": "Qual é a velocidade da luz?",
            "opcoes": ["A) 300.000 km/s", "B) 250.000 km/s", "C) 350.000 km/s", "D) 400.000 km/s"],
            "resposta": "A",
            "explicacao": "A luz viaja a aproximadamente 300.000 km/s no vácuo!"
        }
    ]
    
    import random
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
    
    # Aguardar resposta do usuário
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
