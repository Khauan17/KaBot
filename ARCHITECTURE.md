# Proposta de Nova Arquitetura para o KaBot

## 1. Visão Geral e Justificativa da Refatoração

O KaBot atual utiliza uma estrutura funcional e procedural, com a lógica principal concentrada em `main.py` e a lógica de banco de dados em `database.py`. Para suportar a "mega update" solicitada, que inclui novas funcionalidades complexas como a visão da IA e a necessidade de um código mais limpo e manutenível, propomos a adoção de uma arquitetura baseada em **Programação Orientada a Objetos (POO)** e o padrão **Cogs** do `discord.py` de forma mais rigorosa.

A refatoração visa os seguintes objetivos:
1. **Separação de Responsabilidades (SRP):** Garantir que cada módulo ou classe tenha uma única responsabilidade.
2. **Manutenibilidade:** Facilitar a adição de novas funcionalidades e a correção de bugs.
3. **Testabilidade:** Tornar o código mais fácil de testar.
4. **Escalabilidade:** Preparar o bot para um crescimento futuro em comandos e complexidade.

## 2. Estrutura de Diretórios Proposta

A nova estrutura de diretórios será mais organizada, separando as diferentes camadas do bot:

```
kabot_refactor/
├── cogs/                  # Módulos de comandos e funcionalidades (Cogs)
│   ├── ai_commands.py     # Comandos de interação com a IA (chat, visão, etc.)
│   ├── utility.py         # Comandos utilitários (ping, help, etc.)
│   └── external_apis.py   # Comandos que usam APIs externas (NASA, YouTube, etc.)
├── core/                  # Componentes centrais e de infraestrutura
│   ├── bot.py             # Classe principal do Bot (herda de commands.Bot)
│   ├── config.py          # Gerenciamento de configurações e variáveis de ambiente
│   └── db_manager.py      # Gerenciamento da conexão e operações de banco de dados (Supabase)
├── events/                # Módulos de eventos do Discord (on_ready, on_message, etc.)
│   ├── lifecycle.py       # Eventos de ciclo de vida (on_ready, on_connect)
│   └── chat_handler.py    # Eventos de mensagens e lógica de chat
├── services/              # Classes de serviço para lógica de negócio complexa
│   ├── ai_service.py      # Lógica de interação com a API Gemini (chat, visão, memória)
│   └── external_service.py# Lógica para APIs externas (NASA, YouTube, etc.)
├── .env                   # Variáveis de ambiente (mantido)
├── main.py                # Ponto de entrada do bot (apenas inicializa e roda)
├── requirements.txt       # Dependências (atualizado)
└── README.md              # Documentação do projeto (atualizado)
```

## 3. Principais Mudanças de Arquitetura

### 3.1. Ponto de Entrada (`main.py`)
O `main.py` será simplificado para apenas carregar as configurações, inicializar o banco de dados e iniciar a classe `KaBot` (agora em `core/bot.py`).

### 3.2. Gerenciamento de Configuração (`core/config.py`)
Todas as variáveis de ambiente serão carregadas e validadas em uma única classe ou função, garantindo que o bot não inicie sem as chaves críticas.

### 3.3. Gerenciamento de Banco de Dados (`core/db_manager.py`)
O código de `database.py` será movido para `core/db_manager.py` e encapsulado em uma classe `DBManager`. Isso permitirá que a conexão seja inicializada uma única vez e passada para os serviços que a utilizam.

### 3.4. Serviço de IA (`services/ai_service.py`)
Esta será a camada mais importante para a nova funcionalidade.
- **Responsabilidade:** Gerenciar a comunicação com a API Gemini, incluindo a configuração do modelo, o histórico de conversas e a nova funcionalidade de **visão**.
- **Visão (Multimodalidade):** O serviço será projetado para receber o texto da mensagem e, opcionalmente, um ou mais anexos de imagem. Ele fará a chamada apropriada para o modelo Gemini que suporta entrada multimodal (texto + imagem).

### 3.5. Classe Principal do Bot (`core/bot.py`)
A classe `KaBot` será o coração do bot, responsável por:
- Configurar intents e prefixo.
- Gerenciar o estado global (tempo de início, versão, etc.).
- Carregar os Cogs e Eventos.
- Inicializar os serviços (como `AIService` e `DBManager`) e passá-los para os Cogs.

### 3.6. Cogs e Eventos
- **Cogs:** Serão responsáveis por comandos específicos (`!ka <cmd>` ou `/slash`). Eles receberão instâncias dos serviços (`AIService`, `ExternalService`) no construtor para executar a lógica de negócio.
- **Eventos:** Serão responsáveis por lidar com eventos do Discord, como `on_message`. O `events/chat_handler.py` será crucial para interceptar mensagens, verificar se há anexos de imagem e chamar o `AIService` para a resposta multimodal.

## 4. Próximos Passos

Com esta arquitetura definida, o próximo passo será configurar o ambiente de desenvolvimento e criar a estrutura de diretórios, para então iniciar a refatoração do código existente para essa nova estrutura.
