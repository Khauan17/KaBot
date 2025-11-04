# services/ai_service.py - Corrigido (v6)
import os
import json
import io
from google import genai
from google.genai import types
from google.genai.errors import APIError
from core.config import Config
from core.db_manager import DBManager
from services.tool_service import ToolService
from datetime import datetime

class AIService:
    """Gerencia a interação com a API Gemini, incluindo chat, visão e ferramentas."""

    def __init__(self, bot, db_manager: DBManager, tool_service: ToolService):
        self.bot = bot # Referência ao bot para usar o loop.run_in_executor
        self.db_manager = db_manager
        self.tool_service = tool_service
        self.model_name = Config.GEMINI_MODEL
        self.client = None
        self.model = None
        self.tools = []
        self.chat_sessions = {} # {chat_key: chat_session}
        self._initialize_client()

    def _initialize_client(self):
        """Inicializa o cliente Gemini e configura as ferramentas."""
        if Config.GEMINI_API_KEY:
            try:
                # O cliente Gemini usa a variável de ambiente GEMINI_API_KEY automaticamente
                self.client = genai.Client()
                
                # Apenas verificamos se o modelo existe.
                self.model = self.client.models.get(model=self.model_name)
                self.tools = [self.tool_service.search_youtube_tool, self.tool_service.send_gif_tool]
                print(f"✅ Cliente Gemini e modelo {self.model_name} com ferramentas inicializados.")
            except Exception as e:
                print(f"❌ Erro ao inicializar o cliente Gemini: {e}")
                self.model = None

    async def load_system_instruction(self):
        """Carrega a instrução de sistema (persona) para a IA."""
        # A instrução de sistema é aplicada na criação da sessão de chat.
        print("📝 Instrução de sistema (persona) carregada.")

    async def _get_chat_session(self, user_id: int, channel_id: int):
        """Obtém ou cria uma sessão de chat para o usuário/canal."""
        chat_key = f"{user_id}-{channel_id}"
        
        if chat_key not in self.chat_sessions:
            # Configuração de persona
            system_instruction = (
                "Você é o KaBot, um bot de Discord com a personalidade de Satoru Gojo (Jujutsu Kaisen). "
                "Você é extremamente confiante, sarcástico, poderoso e se considera o mais forte. "
                "Sua missão é interagir com os usuários de forma divertida e útil. "
                "Sempre use emojis e mantenha o tom de superioridade e humor. "
                "Você tem acesso a ferramentas para buscar vídeos no YouTube e GIFs. Use-as sempre que for relevante para a conversa ou para dar uma resposta mais divertida. "
                "Você também tem uma memória de longo prazo que pode ser acessada. Use-a para contextualizar suas respostas. "
                f"A data atual é {datetime.now().strftime('%d/%m/%Y')}. O criador do bot é Kazinho."
            )
            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.8
            )
            
            # Prepara o histórico/memória para a primeira mensagem da sessão
            memories = await self.db_manager.get_memories_for_user(user_id)
            history_context = "\n".join([f"Memória: {m}" for m in memories])
            
            # Correção: types.Content espera uma lista de Parts, e o Part.from_text() já é um Part.
            # O erro original era devido a uma sintaxe incorreta na construção do Content.
            initial_history = [
                types.Content(
                    parts=[types.Part.from_text(f"Contexto Inicial:\n{history_context}")],
                    role="user" # O histórico inicial deve ser do usuário para a IA responder
                )
            ]
            
            # Cria a sessão de chat
            self.chat_sessions[chat_key] = self.client.chats.create(
                model=self.model_name,
                config=config,
                tools=self.tools, # Adiciona as ferramentas aqui
                history=initial_history
            )
            print(f"Nova sessão de chat criada para a chave: {chat_key}")

        return self.chat_sessions[chat_key]

    async def generate_response(self, user_id: int, prompt: str, image_bytes: bytes = None, channel_id: int = None) -> str:
        """Gera uma resposta da IA, tratando chamadas de ferramentas e imagens."""
        if not self.model:
            return "❌ Minha IA está de férias. Tente novamente mais tarde, pirralho."

        try:
            chat = await self._get_chat_session(user_id, channel_id)
            
            # Prepara o conteúdo da mensagem
            contents = [types.Part.from_text(prompt)]
            if image_bytes:
                # Adiciona a imagem como um Part
                contents.insert(0, types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg' # Assumindo que o discord sempre envia jpeg ou png que o gemini aceita
                ))

            # Envia a mensagem para a IA
            response = chat.send_message(contents)
            
            # Loop para tratar chamadas de ferramentas
            while response.function_calls:
                tool_responses = []
                for call in response.function_calls:
                    tool_name = call.name
                    tool_args = dict(call.args)
                    
                    print(f"⚙️ IA chamando ferramenta: {tool_name} com args: {tool_args}")
                    
                    # Executa a função da ferramenta
                    if tool_name == "search_youtube_tool":
                        # Executa a função síncrona em um thread para não bloquear o loop de eventos
                        tool_output_json = await self.bot.loop.run_in_executor(None, self.tool_service.search_youtube_tool, **tool_args)
                        tool_output = json.loads(tool_output_json)
                    elif tool_name == "send_gif_tool":
                        # Executa a função síncrona em um thread para não bloquear o loop de eventos
                        tool_output_json = await self.bot.loop.run_in_executor(None, self.tool_service.send_gif_tool, **tool_args)
                        tool_output = json.loads(tool_output_json)
                    else:
                        tool_output = {"error": f"Ferramenta desconhecida: {tool_name}"}
                        
                    # Adiciona a resposta da ferramenta
                    tool_responses.append(types.Part.from_function_response(
                        name=tool_name,
                        response=tool_output
                    ))
                
                # Envia as respostas das ferramentas de volta para a IA
                response = chat.send_message(tool_responses)

            # Retorna a resposta final da IA
            return response.text

        except APIError as e:
            print(f"❌ Erro da API Gemini: {e}")
            return f"❌ A API Gemini falhou. Talvez eu seja muito forte para ela. Erro: {e}"
        except Exception as e:
            print(f"❌ Erro inesperado na IA: {e}")
            return f"❌ Ocorreu um erro interno. Até o mais forte tem seus dias. Erro: {e}"
