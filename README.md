# KaBot - Mega Update (v6.0)

Este é o KaBot, agora refatorado para uma arquitetura mais robusta, orientada a serviços e com funcionalidades de Inteligência Artificial aprimoradas, incluindo a capacidade de **visão (multimodalidade)**.

## 🚀 Novidades da Mega Update (v6.0)

*   **Arquitetura Limpa:** Código refatorado para o padrão de Serviços e Cogs, facilitando a manutenção e a adição de novas funcionalidades.
*   **IA Multimodal (Visão):** A IA agora pode "ver" e analisar imagens anexadas em mensagens onde o bot é mencionado.
*   **IA Inteligente com Ferramentas:** A IA pode decidir autonomamente quando usar ferramentas para buscar vídeos no YouTube ou GIFs no Tenor para enriquecer a interação.
*   **Comandos de Barra (`/`):** Todos os comandos principais agora suportam comandos de barra, além do prefixo `!ka`.
*   **Funcionalidades Preservadas:** Todos os comandos originais (`!meme`, `!jokenpo`, `!nasa`, `!gravar`, etc.) foram mantidos e aprimorados.
*   **Novo Comando:** Adicionado o comando `!traduzir` (`/traduzir`) para tradução explícita via IA.

## ⚙️ Setup

1.  **Variáveis de Ambiente:** Certifique-se de que seu arquivo `.env` (copiado para a pasta `kabot_refactor`) esteja preenchido com as chaves de API necessárias (Discord, Gemini, Supabase, YouTube, Tenor, NASA). **Revogue e regenere** as chaves antigas, conforme o aviso de segurança.
2.  **Instalar Dependências:**
    ```bash
    cd kabot_refactor
    pip install -r requirements.txt
    ```
3.  **Rodar o Bot:**
    ```bash
    python main.py
    ```

## 🤖 Comandos Principais

Todos os comandos abaixo funcionam com o prefixo `!ka <comando>` ou como `/comando`.

| Categoria | Comando | Descrição |
| :--- | :--- | :--- |
| **Inteligência Artificial** | `chat [pergunta]` | Converse com a IA. Suporta imagens anexadas. |
| | `gravar [memória]` | Instrua a IA a gravar uma informação importante na sua memória de longo prazo (apenas para o criador). |
| | `traduzir <origem-destino> <texto>` | Traduz um texto usando a IA (ex: `pt-en Olá`). |
| **Utilidade** | `ping` | Verifica a latência do bot. |
| | `info` / `sobre` | Mostra informações e tempo online do bot. |
| | `ajuda` | Mostra este catálogo de comandos. |
| | `somar <expressão>` | Faz cálculos matemáticos básicos. |
| | `pergunta <pergunta>` | Responde a perguntas de sim ou não. |
| | `curiosidade` | Conta uma curiosidade aleatória. |
| **Diversão** | `meme` | Conta uma piada. |
| | `gif [tema]` | Busca um GIF sobre um tema. |
| | `jokenpo` / `ppt` | Joga pedra, papel ou tesoura. |
| | `roleta` | Gira uma roleta de 1 a 100. |
| | `abracar <membro>` | Dá um abraço em alguém. |
| | `monkey <frequência>` | Ativa o Modo Macaco (repete mensagens a cada `frequência` mensagens). |
| **APIs Externas** | `nasa` | Mostra a Imagem Astronômica do Dia (APOD) da NASA, traduzida pela IA. |
| | `news [categoria]` | Busca a manchete de notícias, traduzida pela IA. |

## ⚠️ Aviso de Segurança

Você publicou publicamente seu Token do Discord e chaves de API. **É CRÍTICO que você REVOGUE e REGENERE** essas chaves nos respectivos painéis de controle (Discord Developer Portal, Google AI Studio, Supabase, etc.) e atualize o arquivo `.env` com as novas chaves. **NUNCA** compartilhe essas chaves publicamente.
