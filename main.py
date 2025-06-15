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
        """Traduzir texto usando LibreTranslate API com melhor detecção"""
        try:
            # Se o texto for muito curto, retornar original
            if len(text.strip()) < 5:
                return text

            # Detectar se o texto já está em português (critério mais rigoroso)
            portuguese_words = ['o', 'a', 'de', 'do', 'da', 'em', 'um', 'uma', 'para', 'com', 'não', 'no', 'na', 'por', 'mais', 'que', 'se', 'como', 'este', 'esta', 'são', 'é', 'foi', 'tem', 'ter', 'ser', 'estar', 'fazer', 'sobre', 'entre', 'mas', 'ou', 'quando', 'onde', 'aqui', 'ali', 'hoje', 'ontem', 'amanhã']
            words = text.lower().split()
            portuguese_count = sum(1 for word in words if word in portuguese_words)

            # Se mais de 30% das palavras são portuguesas, não traduzir
            if len(words) > 0 and (portuguese_count / len(words)) > 0.3:
                return text

            # Dividir texto em partes menores para melhor tradução
            sentences = text.split('. ')
            translated_sentences = []

            for sentence in sentences:
                if len(sentence.strip()) < 5:
                    translated_sentences.append(sentence)
                    continue

                # Tentar usar LibreTranslate
                import requests
                import json

                url = "https://libretranslate.com/translate"
                data = {
                    "q": sentence.strip(),
                    "source": "auto",
                    "target": "pt",
                    "format": "text"
                }

                headers = {"Content-Type": "application/json"}

                try:
                    response = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)

                    if response.status_code == 200:
                        result = response.json()
                        translated_sentence = result.get("translatedText", sentence)
                        translated_sentences.append(translated_sentence)
                    else:
                        # Se falhar, usar fallback para esta sentença
                        translated_sentences.append(self.fallback_translate(sentence))
                except:
                    # Se falhar, usar fallback para esta sentença
                    translated_sentences.append(self.fallback_translate(sentence))

                # Pequeno delay para não sobrecarregar a API
                await asyncio.sleep(0.1)

            return '. '.join(translated_sentences)

        except Exception as e:
            print(f"Erro ao traduzir: {e}")
            return self.fallback_translate(text)

    def fallback_translate(self, text):
        """Tradução de fallback usando palavras-chave comuns expandida"""
        common_translations = {
            # Espaço e astronomia
            "space": "espaço", "NASA": "NASA", "earth": "Terra", "moon": "lua", "sun": "sol",
            "planet": "planeta", "galaxy": "galáxia", "telescope": "telescópio", "mission": "missão",
            "science": "ciência", "astronomy": "astronomia", "discovery": "descoberta",
            "asteroid": "asteroide", "comet": "cometa", "satellite": "satélite", "rocket": "foguete",
            "orbit": "órbita", "spacecraft": "espaçonave", "universe": "universo", "stellar": "estelar",
            "solar": "solar", "lunar": "lunar", "cosmic": "cósmico", "radiation": "radiação",
            "atmosphere": "atmosfera", "mars": "Marte", "venus": "Vênus", "jupiter": "Júpiter",
            "saturn": "Saturno", "mercury": "Mercúrio", "neptune": "Netuno", "uranus": "Urano",
            "star": "estrela", "constellation": "constelação", "nebula": "nebulosa",

            # Tecnologia e ciência
            "technology": "tecnologia", "research": "pesquisa", "study": "estudo", "data": "dados",
            "image": "imagem", "photo": "foto", "picture": "imagem", "video": "vídeo",
            "computer": "computador", "artificial": "artificial", "intelligence": "inteligência",
            "robot": "robô", "machine": "máquina", "algorithm": "algoritmo", "software": "software",
            "hardware": "hardware", "internet": "internet", "network": "rede", "digital": "digital",

            # Natureza e meio ambiente
            "nature": "natureza", "environment": "meio ambiente", "climate": "clima",
            "weather": "tempo", "ocean": "oceano", "sea": "mar", "river": "rio", "forest": "floresta",
            "animal": "animal", "plant": "planta", "tree": "árvore", "bird": "pássaro", "fish": "peixe",
            "water": "água", "air": "ar", "fire": "fogo", "ice": "gelo", "snow": "neve", "rain": "chuva",

            # Tempo e datas
            "today": "hoje", "yesterday": "ontem", "tomorrow": "amanhã", "now": "agora",
            "year": "ano", "month": "mês", "week": "semana", "day": "dia", "hour": "hora",
            "minute": "minuto", "second": "segundo", "time": "tempo", "date": "data",
            "morning": "manhã", "afternoon": "tarde", "evening": "noite", "night": "noite",

            # Palavras básicas
            "the": "o", "and": "e", "of": "de", "in": "em", "to": "para", "is": "é", "was": "foi",
            "are": "são", "were": "eram", "be": "ser", "have": "ter", "has": "tem", "had": "tinha",
            "will": "vai", "would": "seria", "could": "poderia", "should": "deveria", "can": "pode",
            "this": "este", "that": "aquele", "these": "estes", "those": "aqueles",
            "with": "com", "from": "de", "by": "por", "at": "em", "on": "em", "up": "para cima",
            "down": "para baixo", "out": "fora", "off": "desligado", "over": "sobre", "under": "sob",
            "again": "novamente", "further": "mais", "then": "então", "once": "uma vez",
            "here": "aqui", "there": "lá", "when": "quando", "where": "onde", "why": "por que",
            "how": "como", "all": "todos", "any": "qualquer", "both": "ambos", "each": "cada",
            "few": "poucos", "more": "mais", "most": "mais", "other": "outro", "some": "alguns",
            "such": "tal", "no": "não", "nor": "nem", "not": "não", "only": "apenas", "own": "próprio",
            "same": "mesmo", "so": "então", "than": "que", "too": "também", "very": "muito",
            "just": "apenas", "now": "agora", "new": "novo", "old": "velho", "first": "primeiro",
            "last": "último", "long": "longo", "great": "grande", "little": "pequeno", "good": "bom",
            "bad": "ruim", "right": "direito", "left": "esquerdo", "high": "alto", "low": "baixo",
            "large": "grande", "small": "pequeno", "big": "grande", "young": "jovem", "early": "cedo",
            "late": "tarde", "public": "público", "private": "privado", "important": "importante",
            "possible": "possível", "different": "diferente", "similar": "similar", "special": "especial",
            "amazing": "incrível", "beautiful": "bonito", "interesting": "interessante"
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
        """Buscar notícias da NASA com tradução melhorada"""
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
                    print(f"Traduzindo título: {title[:50]}...")
                    title_pt = await self.translate_text(title, "en", "pt")
                    print(f"Título traduzido: {title_pt[:50]}...")

                    print(f"Traduzindo explicação: {explanation[:50]}...")
                    explanation_pt = await self.translate_text(explanation, "en", "pt")
                    print(f"Explicação traduzida: {explanation_pt[:50]}...")
                except Exception as e:
                    print(f"Erro na tradução: {e}")
                    # Se falhar a tradução, usar texto original
                    title_pt = title
                    explanation_pt = explanation

                # Criar resumo mais elaborado (primeiras 300 caracteres)
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
            print(f"Erro ao buscar notícias da NASA: {e}")
        return None

    async def fetch_general_news(self):
        """Buscar notícias gerais com melhor apresentação"""
        try:
            # Alternar entre diferentes categorias para variedade
            categorias = {
                'science': '🔬 Ciência',
                'technology': '💻 Tecnologia', 
                'health': '🏥 Saúde'
            }
            categoria_key = random.choice(list(categorias.keys()))
            categoria_nome = categorias[categoria_key]

            url = f"https://newsapi.org/v2/top-headlines?country=br&category={categoria_key}&pageSize=5&apiKey={NEWS_API_KEY}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data['articles']:
                    # Pegar um artigo aleatório dos resultados
                    article = random.choice(data['articles'][:3])

                    title = article.get('title', 'Notícia')
                    description = article.get('description', '')
                    content = article.get('content', '')
                    url_link = article.get('url', '')
                    image = article.get('urlToImage', '')
                    source_name = article.get('source', {}).get('name', 'Fonte desconhecida')
                    published = article.get('publishedAt', '')

                    # Criar resumo melhor usando description e content
                    summary = description if description else "Clique no link para ler a notícia completa!"
                    if content and len(content) > len(summary):
                        # Usar content se for mais descritivo
                        summary = content.split('[+')[0].strip()  # Remove texto promocional do NewsAPI

                    # Limitar tamanho do resumo
                    if len(summary) > 250:
                        summary = summary[:250] + "..."

                    # Formatar data de publicação
                    published_formatted = ""
                    if published:
                        try:
                            from datetime import datetime
                            pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                            published_formatted = pub_date.strftime('%d/%m/%Y às %H:%M')
                        except:
                            published_formatted = published[:10]  # Apenas a data

                    return {
                        'title': title,
                        'summary': summary,
                        'url': url_link,
                        'image_url': image,
                        'source': categoria_nome,
                        'source_name': source_name,
                        'published': published_formatted,
                        'category': categoria_nome
                    }
        except Exception as e:
            print(f"Erro ao buscar notícias gerais: {e}")
        return None

    async def post_curated_news(self, channel):
        """Postar notícias curadas no canal com melhor apresentação"""
        try:
            # Alternar entre NASA e notícias gerais
            import random
            if random.choice([True, False]):
                news = await self.fetch_nasa_news()
                is_nasa = True
            else:
                news = await self.fetch_general_news()
                is_nasa = False

            if news:
                # Cores diferentes para diferentes tipos de notícias
                if is_nasa:
                    color = 0x0066cc  # Azul NASA
                    title_prefix = "🚀"
                else:
                    colors = {
                        '🔬 Ciência': 0x00cc66,
                        '💻 Tecnologia': 0x6600cc,
                        '🏥 Saúde': 0xcc0066
                    }
                    color = colors.get(news.get('category', ''), 0x1f8b4c)
                    title_prefix = news.get('category', '📰').split()[0]

                embed = discord.Embed(
                    title=f"{title_prefix} {news['title']}",
                    description=f"**{news['summary']}**",
                    color=color,
                    timestamp=datetime.now()
                )

                # Adicionar informações específicas baseadas no tipo
                if is_nasa:
                    embed.add_field(
                        name="📅 Data da Imagem/Descoberta",
                        value=news.get('date', 'Data não disponível'),
                        inline=True
                    )
                    if news.get('original_title'):
                        embed.add_field(
                            name="🔤 Título Original",
                            value=news['original_title'],
                            inline=True
                        )
                else:
                    if news.get('published'):
                        embed.add_field(
                            name="📅 Publicado em",
                            value=news['published'],
                            inline=True
                        )
                    if news.get('source_name'):
                        embed.add_field(
                            name="📰 Fonte",
                            value=news['source_name'],
                            inline=True
                        )

                # Adicionar tipo de notícia
                embed.add_field(
                    name="📊 Categoria",
                    value=news['source'],
                    inline=True
                )

                # Adicionar imagem se disponível
                if 'image_url' in news and news['image_url']:
                    embed.set_image(url=news['image_url'])

                # Adicionar link se disponível
                if 'url' in news and news['url']:
                    embed.add_field(
                        name="🔗 Leia a notícia completa",
                        value=f"[👆 Clique aqui para ler mais detalhes]({news['url']})",
                        inline=False
                    )

                # Adicionar thumbnail do KaBot
                if hasattr(channel.guild, 'me') and channel.guild.me.avatar:
                    embed.set_thumbnail(url=channel.guild.me.avatar.url)

                # Footer personalizado
                embed.set_footer(
                    text="📡 KaBot Radar de Informações | Criado por Kazinho",
                    icon_url="https://cdn.discordapp.com/emojis/1234567890123456789.png" if hasattr(channel.guild, 'me') and channel.guild.me.avatar else None
                )

                # Enviar mensagem com reações
                message = await channel.send(embed=embed)

                # Adicionar reações para engajamento
                await message.add_reaction('👍')  # Gostei
                await message.add_reaction('🤔')  # Interessante
                await message.add_reaction('📚')  # Quero saber mais
                if is_nasa:
                    await message.add_reaction('🚀')  # Espacial
                else:
                    await message.add_reaction('💡')  # Interessante

                print(f"Notícia postada com sucesso: {news['title'][:50]}...")

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
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Tratamento global de erros para comandos slash"""
    if isinstance(error, discord.app_commands.CommandInvokeError):
        if isinstance(error.original, discord.NotFound):
            print(f"Interação expirou para o comando: {interaction.command.name if interaction.command else 'desconhecido'}")
            return

    print(f"Erro no comando {interaction.command.name if interaction.command else 'desconhecido'}: {error}")

    try:
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ Ocorreu um erro inesperado. Tente novamente!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Ocorreu um erro inesperado. Tente novamente!", ephemeral=True)
    except:
        pass  # Se não conseguir enviar erro, apenas ignore

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

@bot.tree.command(name="sorteio", description="🎉 Sortear pessoas aleatórias do servidor")
@discord.app_commands.describe(quantidade="Quantas pessoas sortear (máximo 10)")
async def sorteio_slash(interaction: discord.Interaction, quantidade: discord.app_commands.Range[int, 1, 10] = 1):
    """Comando de sorteio com tratamento de erro melhorado"""
    import random

    try:
        # Responder imediatamente para evitar timeout
        await interaction.response.defer()

        # Pegar todos os membros do servidor que não são bots
        members = [member for member in interaction.guild.members if not member.bot]

        if not members:
            await interaction.followup.send("❌ Nenhum membro encontrado no servidor!", ephemeral=True)
            return

        # Se a quantidade for maior que o número de membros
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
            value=f"**Total de participantes:** {len(members)}\n**Pessoas sorteadas:** {quantidade}",
            inline=False
        )

        embed.set_footer(text="Sorteio realizado pelo KaBot | Criado por Kazinho")
        await interaction.followup.send(embed=embed)

    except discord.NotFound:
        # Interação não encontrada - não fazer nada
        print("Interação expirou ou não foi encontrada")
    except discord.InteractionResponded:
        # Interação já foi respondida - tentar usar followup
        try:
            await interaction.followup.send("❌ Erro ao realizar sorteio - interação já respondida!", ephemeral=True)
        except:
            print("Não foi possível enviar mensagem de erro")
    except Exception as e:
        print(f"Erro no sorteio: {e}")
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ Erro ao realizar sorteio!", ephemeral=True)
            else:
                await interaction.followup.send("❌ Erro ao realizar sorteio!", ephemeral=True)
        except:
            print("Não foi possível enviar mensagem de erro")

@bot.tree.command(name="traduzir", description="🌍 Traduzir texto para português")
@discord.app_commands.describe(texto="Texto que você quer traduzir para português")
async def traduzir_slash(interaction: discord.Interaction, texto: str):
    """Comando para traduzir texto"""
    try:
        await interaction.response.defer()

        # Forçar tradução para português, removendo a detecção automática
        import requests
        import json

        url = "https://libretranslate.com/translate"
        data = {
            "q": texto,
            "source": "auto",
            "target": "pt",
            "format": "text"
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(url, data=json.dumps(data), headers=headers, timeout=15)

        if response.status_code == 200:
            result = response.json()
            texto_traduzido = result.get("translatedText", texto)
        else:
            # Se falhar, usar tradução de fallback
            texto_traduzido = await kabot.translate_text(texto, "auto", "pt")

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
            value=f"```{texto_traduzido[:500] + '...' if len(texto_traduzido) > 500 else texto_traduzido}