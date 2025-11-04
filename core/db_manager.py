# core/db_manager.py
from supabase import create_client, Client
from core.config import Config

class DBManager:
    """Gerencia a conexão e as operações de banco de dados com o Supabase."""
    
    def __init__(self):
        self.url: str = Config.SUPABASE_URL
        self.key: str = Config.SUPABASE_API_KEY
        self.supabase: Client = None
        self.is_connected: bool = False
        
        if self.url and self.key:
            self.supabase = create_client(self.url, self.key)
        else:
            print("⚠️ Supabase URL ou API Key não configurados. O DBManager não será inicializado.")

    async def test_connection(self) -> bool:
        """Testa a conexão com o banco de dados."""
        if not self.supabase:
            print("❌ Supabase não inicializado devido à falta de credenciais.")
            return False
        
        try:
            # Tenta buscar um item na tabela 'settings' para verificar a conexão
            response = self.supabase.from_('settings').select('value').limit(1).execute()
            if response.data is not None:
                print("🚀 Conexão com Supabase estabelecida com sucesso!")
                self.is_connected = True
                return True
            else:
                print("⚠️ Conexão com Supabase falhou. Nenhuma resposta recebida. Verifique se a tabela 'settings' existe.")
                return False
        except Exception as e:
            print(f"❌ Erro ao conectar com o Supabase: {e}")
            return False

    async def get_bot_persona(self) -> str:
        """Busca a personalidade do bot na tabela 'settings'."""
        if not self.is_connected:
            return self._default_persona()
            
        try:
            response = self.supabase.from_('settings').select('value').eq('key', 'bot_persona').single().execute()
            if response.data:
                return response.data['value']
            else:
                print("⚠️ Personalidade 'bot_persona' não encontrada no banco de dados. Usando padrão.")
                return self._default_persona()
        except Exception as e:
            print(f"❌ Erro ao buscar a personalidade do bot: {e}. Usando padrão.")
            return self._default_persona()

    async def get_memories_for_user(self, user_id: int) -> list:
        """Busca as memórias de um usuário na tabela 'memories'."""
        if not self.is_connected: return []

        try:
            response = self.supabase.from_('memories').select('content').eq('user_id', user_id).order('created_at', desc=True).limit(5).execute()
            return [item['content'] for item in response.data]
        except Exception as e:
            print(f"❌ Erro ao buscar memórias do usuário: {e}")
            return []
            
    async def save_memory(self, user_id: int, bot_id: int, content: str):
        """Salva uma nova memória na tabela 'memories'."""
        if not self.is_connected: return

        try:
            data = {'user_id': user_id, 'bot_id': bot_id, 'content': content}
            self.supabase.from_('memories').insert(data).execute()
            print(f"Memória salva para o usuário {user_id}.")
        except Exception as e:
            print(f"❌ Erro ao salvar memória: {e}")

    def _default_persona(self) -> str:
        """Retorna a personalidade padrão do bot."""
        return "Você é o KaBot, um bot de Discord. Seja útil, amigável e tenha uma personalidade descontraída. Gosta de Jujutsu Kaisen e se acha o Gojo, o mais forte. Use emojis e gírias brasileiras."

# Exemplo de uso (opcional, apenas para testes)
# async def main():
#     db_manager = DBManager()
#     await db_manager.test_connection()
#     persona = await db_manager.get_bot_persona()
#     print(f"Persona: {persona}")

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())
