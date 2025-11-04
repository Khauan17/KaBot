# services/external_service.py
import requests
from core.config import Config
from google.genai import Client
from google.genai.errors import APIError

class ExternalService:
    """Gerencia a comunicação com APIs externas (NASA, News, YouTube)."""
    
    def __init__(self):
        self.nasa_api_key = Config.NASA_API_KEY
        self.youtube_api_key = Config.YOUTUBE_API_KEY
        self.news_api_key = Config.NEWS_API_KEY
        self.gemini_client = None
        
        if Config.GEMINI_API_KEY:
            try:
                self.gemini_client = Client()
            except Exception as e:
                print(f"❌ Erro ao inicializar o cliente Gemini para tradução: {e}")

    async def get_nasa_apod(self) -> str:
        """Busca a Imagem Astronômica do Dia (APOD) da NASA e traduz a descrição."""
        if not self.nasa_api_key:
            return "⚠️ Chave da NASA API não configurada. Não foi possível buscar a APOD."

        url = f"https://api.nasa.gov/planetary/apod?api_key={self.nasa_api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            title = data.get('title', 'Sem Título')
            explanation = data.get('explanation', 'Sem descrição.')
            image_url = data.get('url', '')
            
            # Traduz a explicação usando a IA
            translated_explanation = await self._translate_text(explanation, "Português")
            
            output = f"**🌌 Imagem Astronômica do Dia (APOD) - NASA**\n"
            output += f"**Título:** {title}\n"
            output += f"**Descrição (Traduzida):** {translated_explanation}\n"
            output += f"**Link:** {image_url}"
            
            return output
            
        except requests.exceptions.RequestException as e:
            return f"❌ Erro ao conectar com a NASA API: {e}"
        except Exception as e:
            return f"❌ Erro inesperado ao processar APOD: {e}"

    async def get_news_headline(self, category: str = 'general') -> str:
        """Busca a manchete de notícias e traduz para o português."""
        if not self.news_api_key:
            return "⚠️ Chave da News API não configurada. Não foi possível buscar notícias."

        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'apiKey': self.news_api_key,
            'country': 'us', # Buscando notícias dos EUA para garantir conteúdo em inglês para tradução
            'category': category
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = data.get('articles', [])
            if not articles:
                return f"⚠️ Nenhuma notícia encontrada para a categoria '{category}'."
                
            article = articles[0]
            title = article.get('title', 'Sem Título')
            description = article.get('description', 'Sem descrição.')
            
            # Traduz o título e a descrição
            translated_title = await self._translate_text(title, "Português")
            translated_description = await self._translate_text(description, "Português")
            
            output = f"**📰 Manchete de Notícias ({category.capitalize()})**\n"
            output += f"**Título:** {translated_title}\n"
            output += f"**Descrição:** {translated_description}\n"
            output += f"**Fonte:** {article.get('source', {}).get('name', 'Desconhecida')}"
            
            return output
            
        except requests.exceptions.RequestException as e:
            return f"❌ Erro ao conectar com a News API: {e}"
        except Exception as e:
            return f"❌ Erro inesperado ao processar notícias: {e}"

    async def _translate_text(self, text: str, target_language: str) -> str:
        """Função auxiliar para traduzir texto usando a API Gemini."""
        if not self.gemini_client:
            return f"[ERRO DE TRADUÇÃO: Cliente Gemini não inicializado] {text}"
            
        prompt = f"Traduza o seguinte texto para {target_language}. Mantenha o tom e o contexto originais, mas use uma linguagem natural e fluida:\n\n{text}"
        
        try:
            response = self.gemini_client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=prompt
            )
            return response.text
        except APIError as e:
            print(f"❌ Erro da API Gemini durante a tradução: {e}")
            return f"[ERRO DE TRADUÇÃO: Falha na API] {text}"
        except Exception as e:
            print(f"❌ Erro inesperado durante a tradução: {e}")
            return f"[ERRO DE TRADUÇÃO: Erro interno] {text}"

# Exemplo de uso (opcional, apenas para testes)
# async def main():
#     service = ExternalService()
#     print(await service.get_nasa_apod())
#     print(await service.get_news_headline('technology'))

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())
'''
    async def translate_text_explicit(self, text: str, source_lang: str, target_lang: str) -> str:
        """Função de tradução explícita para o comando de tradução."""
        if not self.gemini_client:
            return "[ERRO DE TRADUÇÃO: Cliente Gemini não inicializado]"

        prompt = f"Traduza o seguinte texto de '{source_lang}' para '{target_lang}'. Retorne apenas o texto traduzido, sem qualquer outra formatação ou comentário:\n\n{text}"

        try:
            response = self.gemini_client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=prompt
            )
            return response.text
        except APIError as e:
            print(f"❌ Erro da API Gemini durante a tradução explícita: {e}")
            return f"[ERRO DE TRADUÇÃO: Falha na API]"
        except Exception as e:
            print(f"❌ Erro inesperado durante a tradução explícita: {e}")
            return f"[ERRO DE TRADUÇÃO: Erro interno]"
'''
