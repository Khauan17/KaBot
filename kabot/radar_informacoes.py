
import requests
import os
import discord
from datetime import datetime
import random

class RadarInformacoes:
    def __init__(self, bot):
        self.bot = bot
        self.nasa_api_key = os.getenv('NASA_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.canal_noticias_id = None  # Será configurado dinamicamente
        
    async def buscar_e_compartilhar_noticias(self):
        """Busca e compartilha notícias curadas"""
        try:
            # Buscar notícias da NASA
            noticias_nasa = await self.buscar_noticias_nasa()
            
            # Buscar notícias gerais
            noticias_gerais = await self.buscar_noticias_gerais()
            
            # Combinar e selecionar as melhores
            todas_noticias = noticias_nasa + noticias_gerais
            
            if todas_noticias:
                # Selecionar uma notícia aleatória para compartilhar
                noticia = random.choice(todas_noticias)
                await self.compartilhar_noticia(noticia)
            
        except Exception as e:
            print(f"❌ Erro no radar de informações: {e}")
    
    async def buscar_noticias_nasa(self):
        """Busca notícias da NASA"""
        try:
            # API de fotos astronômicas do dia
            url = f"https://api.nasa.gov/planetary/apod?api_key={self.nasa_api_key}&count=3"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                dados = response.json()
                noticias = []
                
                for item in dados:
                    if 'title' in item and 'explanation' in item:
                        noticia = {
                            'titulo': f"🚀 NASA: {item['title']}",
                            'resumo': item['explanation'][:200] + "..." if len(item['explanation']) > 200 else item['explanation'],
                            'link': item.get('url', 'https://nasa.gov'),
                            'tipo': 'nasa',
                            'imagem': item.get('url') if item.get('media_type') == 'image' else None
                        }
                        noticias.append(noticia)
                
                return noticias
                
        except Exception as e:
            print(f"❌ Erro ao buscar notícias NASA: {e}")
        
        return []
    
    async def buscar_noticias_gerais(self):
        """Busca notícias gerais de ciência e tecnologia"""
        try:
            # Buscar notícias de ciência
            url = f"https://newsapi.org/v2/top-headlines?category=science&language=pt&pageSize=5&apiKey={self.news_api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                dados = response.json()
                noticias = []
                
                for article in dados.get('articles', []):
                    if article.get('title') and article.get('description'):
                        noticia = {
                            'titulo': f"🔬 {article['title']}",
                            'resumo': article['description'][:200] + "..." if len(article['description']) > 200 else article['description'],
                            'link': article.get('url', ''),
                            'tipo': 'ciencia',
                            'imagem': article.get('urlToImage')
                        }
                        noticias.append(noticia)
                
                return noticias
                
        except Exception as e:
            print(f"❌ Erro ao buscar notícias gerais: {e}")
        
        return []
    
    async def compartilhar_noticia(self, noticia):
        """Compartilha uma notícia curada no Discord"""
        try:
            # Encontrar um canal adequado para postar
            canal = await self.encontrar_canal_noticias()
            
            if not canal:
                print("⚠️ Nenhum canal disponível para postar notícias")
                return
            
            # Criar embed rico
            embed = discord.Embed(
                title=noticia['titulo'],
                description=noticia['resumo'],
                color=0x00ff88 if noticia['tipo'] == 'nasa' else 0x0099ff,
                timestamp=datetime.now()
            )
            
            if noticia['link']:
                embed.add_field(
                    name="🔗 Leia mais",
                    value=f"[Clique aqui]({noticia['link']})",
                    inline=False
                )
            
            if noticia.get('imagem'):
                embed.set_image(url=noticia['imagem'])
            
            embed.set_footer(text="KaBot Radar de Informações 📡")
            
            # Adicionar reações para engajamento
            message = await canal.send(embed=embed)
            await message.add_reaction('👍')
            await message.add_reaction('🤔')
            await message.add_reaction('🔖')
            
            print(f"📡 Notícia compartilhada: {noticia['titulo'][:50]}...")
            
        except Exception as e:
            print(f"❌ Erro ao compartilhar notícia: {e}")
    
    async def encontrar_canal_noticias(self):
        """Encontra um canal adequado para postar notícias"""
        try:
            # Procurar por canais específicos de notícias
            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    # Procurar canais com nomes relacionados a notícias
                    if any(palavra in channel.name.lower() for palavra in ['noticias', 'news', 'info', 'geral', 'principal']):
                        # Verificar se o bot tem permissão para enviar mensagens
                        if channel.permissions_for(guild.me).send_messages:
                            return channel
            
            # Se não encontrar canal específico, usar o primeiro canal disponível
            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        return channel
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao encontrar canal: {e}")
            return None
