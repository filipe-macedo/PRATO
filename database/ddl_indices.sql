-- PRATO — Índices estratégicos para performance de consulta

-- Vendas: consultas por data (mais frequente)
CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data);
CREATE INDEX IF NOT EXISTS idx_vendas_produto ON vendas(produto_id);
CREATE INDEX IF NOT EXISTS idx_vendas_turno ON vendas(turno_id);
CREATE INDEX IF NOT EXISTS idx_vendas_data_produto ON vendas(data, produto_id);
CREATE INDEX IF NOT EXISTS idx_vendas_data_produto_turno ON vendas(data, produto_id, turno_id);

-- Estoque
CREATE INDEX IF NOT EXISTS idx_estoque_produto_data ON estoque_snapshot(produto_id, data);

-- Movimentação
CREATE INDEX IF NOT EXISTS idx_movimentacao_data ON movimentacao_estoque(data);
CREATE INDEX IF NOT EXISTS idx_movimentacao_produto ON movimentacao_estoque(produto_id);

-- Calendário
CREATE INDEX IF NOT EXISTS idx_calendario_feriado ON calendario(data) WHERE is_feriado = 1;
CREATE INDEX IF NOT EXISTS idx_calendario_dia_semana ON calendario(dia_semana);

-- Histórico de previsões
CREATE INDEX IF NOT EXISTS idx_previsoes_data ON historico_previsoes(data_previsao);
CREATE INDEX IF NOT EXISTS idx_previsoes_produto ON historico_previsoes(produto_id);
