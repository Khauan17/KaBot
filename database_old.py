# database.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_API_KEY")

supabase: Client = create_client(url, key)

async def get_bot_persona() -> str:
    """Busca a personalidade do bot na tabela 'settings'."""
    try:
        # Busca a personalidade do bot com um ID fixo ou um 'key' específico
        response = supabase.from_('settings').select('value').eq('key', 'bot_persona').single().execute()
        if response.data:
            return response.data['value']
        else:
            print("⚠️ Personalidade 'bot_persona' não encontrada no banco de dados. Usando padrão.")
            return "Você é o KaBot, um bot de Discord. Seja útil, amigável e tenha uma personalidade descontraída. Gosta de Jujutsu Kaisen e se acha o Gojo, o mais forte. Use emojis e gírias brasileiras."
    except Exception as e:
        print(f"❌ Erro ao buscar a personalidade do bot: {e}. Usando padrão.")
        return "Você é o KaBot, um bot de Discord. Seja útil, amigável e tenha uma personalidade descontraída. Gosta de Jujutsu Kaisen e se acha o Gojo, o mais forte. Use emojis e gírias brasileiras."

async def get_memories_for_user(user_id: int) -> list:
    """Busca as memórias de um usuário na tabela 'memories'."""
    try:
        response = supabase.from_('memories').select('content').eq('user_id', user_id).order('created_at', desc=True).limit(5).execute()
        return [item['content'] for item in response.data]
    except Exception as e:
        print(f"❌ Erro ao buscar memórias do usuário: {e}")
        return []
        
async def save_memory(user_id: int, bot_id: int, content: str):
    """Salva uma nova memória na tabela 'memories'."""
    try:
        data = {'user_id': user_id, 'bot_id': bot_id, 'content': content}
        supabase.from_('memories').insert(data).execute()
        print(f"Memória salva para o usuário {user_id}.")
    except Exception as e:
        print(f"❌ Erro ao salvar memória: {e}")

async def test_supabase_connection():
    """Testa a conexão com o banco de dados."""
    if not url or not key:
        print("❌ Supabase URL ou API Key não configurados no .env. A conexão não será estabelecida.")
        return False
    try:
        response = supabase.from_('settings').select('value').limit(1).execute()
        if response.data:
            print("🚀 Conexão com Supabase estabelecida com sucesso!")
            return True
        else:
            print("⚠️ Conexão com Supabase falhou. Nenhuma resposta recebida. Verifique se a tabela 'settings' existe.")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com o Supabase: {e}")
        return False