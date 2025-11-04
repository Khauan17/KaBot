# services/tool_service.py
import os
import requests
import json
from googleapiclient.discovery import build
from core.config import Config

class ToolService:
    """Encapsula a lógica para as ferramentas que a IA pode chamar (YouTube, Tenor)."""
    
    def __init__(self):
        self.youtube_api_key = Config.YOUTUBE_API_KEY
        self.tenor_api_key = Config.TENOR_API_KEY

    def search_youtube_tool(self, query: str):
        """Busca um vídeo no YouTube com base em uma consulta (query). Retorna a URL do vídeo."""
        if not self.youtube_api_key:
            return json.dumps({"error": "A chave da API do YouTube não está configurada."})
        
        try:
            # A biblioteca googleapiclient é síncrona, o que é aceitável para chamadas de ferramenta síncronas.
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            request = youtube.search().list(part='snippet', q=query, type='video', maxResults=1)
            response = request.execute()
            if response['items']:
                video_id = response['items'][0]['id']['videoId']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                return json.dumps({"url": video_url, "title": response['items'][0]['snippet']['title']})
            else:
                return json.dumps({"result": "Nenhum vídeo encontrado."})
        except Exception as e:
            return json.dumps({"error": f"Erro na API do YouTube: {e}"})

    def send_gif_tool(self, query: str):
        """Busca um GIF no Tenor com base em uma consulta (query). Retorna a URL do GIF."""
        if not self.tenor_api_key:
            return json.dumps({"error": "A chave da API do Tenor não está configurada."})
            
        url = f"https://tenor.googleapis.com/v2/search?q={query}&key={self.tenor_api_key}&limit=1&media_filter=gif"
        try:
            # A chamada requests.get é síncrona, o que é aceitável para chamadas de ferramenta síncronas.
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get('results'):
                # Tenor API v2 usa 'media_formats' e 'gif'
                gif_url = data['results'][0]['media_formats']['gif']['url']
                return json.dumps({"url": gif_url})
            else:
                return json.dumps({"result": f"Nenhum GIF encontrado para '{query}'."})
        except Exception as e:
            return json.dumps({"error": f"Erro na API do Tenor: {e}"})

# Exemplo de uso (opcional, apenas para testes)
# if __name__ == "__main__":
#     tool_service = ToolService()
#     print(tool_service.search_youtube_tool("trailer jujutsu kaisen"))
#     print(tool_service.send_gif_tool("goku super saiyan"))
