
-- Configuração das tabelas para o KaBot no Supabase
-- Execute estes comandos no SQL Editor do Supabase

-- Tabela para memória de curto prazo (mensagens brutas)
CREATE TABLE IF NOT EXISTS mensagens_brutas (
    id BIGSERIAL PRIMARY KEY,
    canal_id TEXT NOT NULL,
    usuario_id TEXT NOT NULL,
    usuario_nome TEXT,
    conteudo TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    servidor_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela para memória de longo prazo (resumos processados)
CREATE TABLE IF NOT EXISTS memoria_longo_prazo (
    id BIGSERIAL PRIMARY KEY,
    data DATE NOT NULL,
    resumo TEXT NOT NULL,
    relevancia DECIMAL DEFAULT 1.0,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_mensagens_timestamp ON mensagens_brutas(timestamp);
CREATE INDEX IF NOT EXISTS idx_mensagens_canal ON mensagens_brutas(canal_id);
CREATE INDEX IF NOT EXISTS idx_memoria_data ON memoria_longo_prazo(data);
CREATE INDEX IF NOT EXISTS idx_memoria_timestamp ON memoria_longo_prazo(timestamp);

-- RLS (Row Level Security) - Opcional
ALTER TABLE mensagens_brutas ENABLE ROW LEVEL SECURITY;
ALTER TABLE memoria_longo_prazo ENABLE ROW LEVEL SECURITY;

-- Políticas básicas (ajuste conforme necessário)
CREATE POLICY "Permitir todas operações para service_role" ON mensagens_brutas
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Permitir todas operações para service_role" ON memoria_longo_prazo
    FOR ALL USING (auth.role() = 'service_role');
-- Tabela para memória de curto prazo (mensagens brutas)
CREATE TABLE IF NOT EXISTS short_term_memory (
    id SERIAL PRIMARY KEY,
    guild_id TEXT,
    channel_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    message_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela para memória de longo prazo (resumos processados)
CREATE TABLE IF NOT EXISTS long_term_memory (
    id SERIAL PRIMARY KEY,
    guild_id TEXT,
    date DATE NOT NULL,
    summary TEXT NOT NULL,
    important_events JSONB,
    user_mentions JSONB,
    topics_discussed TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela para configurações do bot por servidor
CREATE TABLE IF NOT EXISTS bot_settings (
    id SERIAL PRIMARY KEY,
    guild_id TEXT UNIQUE NOT NULL,
    news_channel_id TEXT,
    memory_enabled BOOLEAN DEFAULT true,
    news_radar_enabled BOOLEAN DEFAULT true,
    preferred_language TEXT DEFAULT 'pt',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_short_memory_guild_timestamp ON short_term_memory(guild_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_long_memory_guild_date ON long_term_memory(guild_id, date);
CREATE INDEX IF NOT EXISTS idx_short_memory_timestamp ON short_term_memory(timestamp);

-- Política de limpeza automática para memória de curto prazo (opcional)
-- DELETE FROM short_term_memory WHERE created_at < NOW() - INTERVAL '7 days';
