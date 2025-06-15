
# 🤖 KaBot - Assistente Inteligente para Discord

Um bot Discord proativo e inteligente que participa, lembra e informa, tornando o servidor um lugar mais conectado e dinâmico.

## 🧠 Sistemas Principais

### 1. Cérebro Conversacional
- Lê passivamente as mensagens para entender contexto
- Consulta memória de longo prazo para respostas inteligentes
- Conecta presente com passado nas conversas

### 2. Sistema de Memória
- **Memória de Curto Prazo**: Captura todas as conversas
- **Processamento Diário**: Cria resumos dos eventos importantes
- **Memória de Longo Prazo**: Armazena lembranças permanentes
- **Esquecimento Saudável**: Remove dados antigos automaticamente

### 3. Radar de Informações
- Busca notícias da NASA e de ciência
- Apresenta conteúdo curado com título, resumo e link
- Compartilha informações em intervalos regulares

## 🚀 Configuração

### 1. Configurar o Banco de Dados (Supabase)
1. Acesse seu projeto Supabase
2. Vá para SQL Editor
3. Execute o conteúdo de `database_setup.sql`

### 2. Instalar Dependências
```bash
pip install discord.py supabase requests python-dotenv
```

### 3. Configurar Variáveis de Ambiente
O arquivo `.env` já está configurado com suas credenciais.

### 4. Executar o Bot
```bash
python main.py
```

## 📖 Comandos Disponíveis

- `!ka memoria [quantidade]` - Ver lembranças recentes do KaBot
- `!ka status` - Verificar status dos sistemas
- Mencione `@KaBot` ou escreva "kabot" para interagir

## 🔧 Funcionalidades Futuras

- [ ] Integração com IA para processamento de memórias
- [ ] Análise de sentimentos das conversas
- [ ] Recomendações personalizadas
- [ ] Sistema de aprendizado avançado

## 📱 Status dos Sistemas

✅ **Cérebro Conversacional**: Implementado e funcional
✅ **Sistema de Memória**: Implementado (sem IA por enquanto)
✅ **Radar de Informações**: Implementado com NASA e NewsAPI

---

**Desenvolvido com ❤️ para criar comunidades mais inteligentes e conectadas!**
