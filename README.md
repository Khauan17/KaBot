# 🤖 KaBot

KaBot é um bot modular para Discord desenvolvido em Python com recursos de interação por texto, memória, radar de informações e manutenção automática. Ele é projetado para ser simples, expansível e funcional, podendo inclusive rodar em ambientes leves como o Termux (Android).

---

## 📦 Requisitos

- Python 3.10 ou superior
- Conta e servidor no Discord
- Token de bot (criado via [Discord Developer Portal](https://discord.com/developers/applications))
- Variáveis `.env` (confidenciais)
- Linux, Termux ou ambiente compatível (Replit opcional)

---

## ⚙️ Instalação

### 🔧 1. Clone o repositório:

```bash
git clone https://github.com/seunome/KaBot.git
cd KaBot

📦 2. Instale as dependências:

pip install -r Requests.txt

🔐 3. Configure o .env:

Crie um arquivo chamado .env na raiz com o seguinte conteúdo:

TOKEN=SEU_TOKEN_DO_DISCORD

(Substitua SEU_TOKEN_DO_DISCORD pelo token real do seu bot.)

⸻

🚀 Execução

🖥️ Em PC/Linux:

python3 main.py

ou

./start_bot.sh

📱 Em Android com Termux:
	1.	Instale Python:

pkg update
pkg install python git

	2.	Clone o projeto:

git clone https://github.com/seunome/KaBot.git
cd KaBot

	3.	Instale as dependências e rode:

pip install -r Requests.txt
python main.py

(Ou use ./start_bot.sh se desejar reiniciar automaticamente após erro.)

⸻

🧠 Funcionalidades
	•	kabot/memoria.py: Armazena e recupera memórias/respostas do bot
	•	kabot/chatbase.py: Comunicação com APIs externas (ex: IA)
	•	kabot/radar.py: Radar de informações (provavelmente para pesquisas ou interações rápidas)
	•	kabot/mensagem_sistema.py: Exibe mensagens padronizadas do sistema
	•	kabot/conversar.py: Núcleo do sistema de conversação
	•	keep_alive.py: Mantém o bot ativo em plataformas como Replit
	•	Scripts .sh: Automatizam o início/reinício do bot (úteis em VPS/Termux)

⸻

🛠️ Estrutura do Projeto

KaBot/
├── kabot/                  # Módulos internos do bot
│   ├── __init__.py
│   ├── memoria.py
│   ├── radar.py
│   ├── mensagem_sistema.py
│   ├── conversar.py
│   └── chatbase.py
├── keep_alive.py           # Manutenção online
├── main.py                 # Ponto de entrada do bot
├── start_bot.sh            # Início automático com loop
├── reiniciar_bot.sh        # Reinício manual do bot
├── Requests.txt            # Bibliotecas necessárias
├── README.md               # Este arquivo
└── .env                    # (Ignorado no Git) Token do bot


⸻

📌 Observações
	•	Se rodar no Termux, mantenha o app aberto ou use nohup para manter rodando em segundo plano.
	•	O chatbase.py parece usar alguma API de IA — se necessário, inclua instruções para adicionar essa chave também ao .env.

⸻

📃 Licença

Este projeto é de código aberto. Use, edite e distribua à vontade (adicione sua licença se desejar).

⸻
