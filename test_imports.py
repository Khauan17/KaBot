# test_imports.py
import sys
import os

# Adiciona o diretório do projeto ao PATH para que as importações funcionem
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from kabot_refactor.core.config import Config
    from kabot_refactor.core.db_manager import DBManager
    from kabot_refactor.services.tool_service import ToolService
    from kabot_refactor.services.ai_service import AIService
    from kabot_refactor.services.external_service import ExternalService
    from kabot_refactor.core.bot import KaBot
    from kabot_refactor.cogs import admin, ai_commands, external_apis, fun, utility
    from kabot_refactor.events import chat_handler, lifecycle
    
    print("✅ Todas as importações de módulos e Cogs foram bem-sucedidas.")

    # Teste de Configuração (apenas para verificar se a classe existe)
    if Config.DISCORD_TOKEN:
        print("✅ Configuração carregada.")
    else:
        print("⚠️ Aviso: DISCORD_TOKEN não carregado. Isso é esperado se o .env não estiver no ambiente de teste.")

    # Teste de inicialização de serviços (sem conexão real)
    db_manager = DBManager()
    tool_service = ToolService()
    ai_service = AIService(db_manager, tool_service)
    external_service = ExternalService()
    print("✅ Serviços inicializados (sem conexão real com Discord/DB/APIs).")

except Exception as e:
    print(f"❌ Erro de importação ou inicialização: {e}")
    sys.exit(1)

sys.exit(0)
