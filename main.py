# main.py - Ponto de entrada refatorado e corrigido
import asyncio
import discord
from core.config import Config
from core.db_manager import DBManager
from services.ai_service import AIService
from services.tool_service import ToolService
from core.bot import KaBot
import os

async def main():
    """Função principal para inicializar e rodar o bot."""
    
    # 1. Validar configurações críticas
    try:
        Config.validate_critical_configs()
    except ValueError as e:
        print(f"ERRO CRÍTICO DE CONFIGURAÇÃO: {e}")
        return

    # 2. Inicializar Gerenciadores e Serviços
    db_manager = DBManager()
    if not await db_manager.test_connection():
        print("ERRO: O bot não pode iniciar sem a conexão com o banco de dados.")
        # Opcional: permitir iniciar sem DB, mas com funcionalidades limitadas
        # return 
    
    tool_service = ToolService()
    
    # 3. Inicializar o Bot (temporariamente para injetar no AIService)
    # O KaBot precisa do AIService, mas o AIService precisa do KaBot (para o loop.run_in_executor).
    # Vamos inicializar o KaBot com None para o AIService e injetar depois.
    bot = KaBot(db_manager, ai_service=None, tool_service=tool_service) 
    ai_service = AIService(bot, db_manager, tool_service)
    bot.ai_service = ai_service # Injeta o AIService no bot
    
    # 4. Rodar o Bot
    try:
        await bot.start(Config.DISCORD_TOKEN)
    except discord.LoginFailure:
        print("ERRO CRÍTICO: O token do Discord está incorreto. Verifique o seu .env!")
    except Exception as e:
        print(f"Erro geral ao iniciar o bot: {e}")

if __name__ == "__main__":
    try:
        # Garante que o diretório de trabalho seja o diretório do script
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Adiciona o diretório atual ao sys.path para que as importações de módulos funcionem
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot desligado pelo usuário.")
    except Exception as e:
        print(f"Erro no loop principal: {e}")
