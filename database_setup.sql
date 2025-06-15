
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
