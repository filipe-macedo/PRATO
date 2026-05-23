-- PRATO — Dados iniciais de referência

-- Categorias
INSERT OR IGNORE INTO categorias (nome, descricao) VALUES
    ('prato_principal', 'Pratos principais do cardápio'),
    ('entrada', 'Entradas e aperitivos'),
    ('bebida', 'Bebidas alcoólicas e não alcoólicas'),
    ('sobremesa', 'Doces e sobremesas'),
    ('acompanhamento', 'Guarnições e acompanhamentos');

-- Turnos
INSERT OR IGNORE INTO turnos (nome, hora_inicio, hora_fim) VALUES
    ('cafe_manha', '06:00', '10:59'),
    ('almoco',     '11:00', '14:59'),
    ('lanche',     '15:00', '17:59'),
    ('jantar',     '18:00', '22:59');
