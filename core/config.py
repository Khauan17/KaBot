# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    CREATOR_ID = int(os.getenv("CREATOR_ID", 857228143478571029)) # Usando o ID do main.py como padrão
    ANIVERSARY_DATE = (5, 17) # Mês e Dia
    ANIVERSARY_CHANNEL_ID = int(os.getenv("ANIVERSARY_CHANNEL_ID", 1165064927430574100))

    # Gemini AI
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash" # Modelo padrão para chat e multimodal

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

    # APIs de Terceiros
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    NASA_API_KEY = os.getenv("NASA_API_KEY")
    TENOR_API_KEY = os.getenv("TENOR_API_KEY")

    @classmethod
    def validate_critical_configs(cls):
        """Verifica se as configurações críticas estão presentes."""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN não encontrado no arquivo .env.")
        if not cls.GEMINI_API_KEY:
            print("AVISO: GEMINI_API_KEY não encontrado. Funções de IA não funcionarão.")
        if not cls.SUPABASE_URL or not cls.SUPABASE_API_KEY:
            print("AVISO: Configurações do Supabase incompletas. Funções de banco de dados não funcionarão.")
        
        return True

# Garante que as configurações críticas sejam validadas ao importar
try:
    Config.validate_critical_configs()
except ValueError as e:
    print(f"ERRO DE CONFIGURAÇÃO: {e}")
    # Não levantamos o erro aqui para permitir que o main.py lide com a falha de inicialização
