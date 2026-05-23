-- PRATO — DDL do Banco de Dados
-- Compatível com SQLite (desenvolvimento) e PostgreSQL (produção)
-- Ordem de criação respeita dependências de chave estrangeira

PRAGMA foreign_keys = ON;

-- 1. Categorias
CREATE TABLE IF NOT EXISTS categorias (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        VARCHAR(100) NOT NULL UNIQUE,
    descricao   TEXT,
    criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Produtos
CREATE TABLE IF NOT EXISTS produtos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            VARCHAR(150) NOT NULL UNIQUE,
    categoria_id    INTEGER REFERENCES categorias(id),
    preco_unitario  NUMERIC(10,2) CHECK (preco_unitario >= 0),
    ativo           INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0,1)),
    criado_em       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Turnos
CREATE TABLE IF NOT EXISTS turnos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        VARCHAR(50) NOT NULL UNIQUE,
    hora_inicio VARCHAR(5),
    hora_fim    VARCHAR(5),
    CHECK (nome IN ('cafe_manha','almoco','lanche','jantar','madrugada'))
);

-- 4. Calendário
CREATE TABLE IF NOT EXISTS calendario (
    data                DATE PRIMARY KEY,
    dia_semana          INTEGER NOT NULL CHECK (dia_semana BETWEEN 0 AND 6),
    nome_dia            VARCHAR(20),
    mes                 INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    ano                 INTEGER NOT NULL,
    semana_do_ano       INTEGER,
    trimestre           INTEGER CHECK (trimestre BETWEEN 1 AND 4),
    is_fim_de_semana    INTEGER NOT NULL DEFAULT 0 CHECK (is_fim_de_semana IN (0,1)),
    is_feriado          INTEGER NOT NULL DEFAULT 0 CHECK (is_feriado IN (0,1)),
    descricao_feriado   VARCHAR(100)
);

-- 5. Vendas (tabela principal)
CREATE TABLE IF NOT EXISTS vendas (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    data                DATE NOT NULL,
    produto_id          INTEGER NOT NULL REFERENCES produtos(id),
    turno_id            INTEGER NOT NULL REFERENCES turnos(id),
    quantidade_vendida  NUMERIC(10,2) NOT NULL CHECK (quantidade_vendida >= 0),
    preco_unitario      NUMERIC(10,2) CHECK (preco_unitario >= 0),
    receita_total       NUMERIC(12,2),
    quantidade_cancelada NUMERIC(10,2) DEFAULT 0,
    criado_em           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (data, produto_id, turno_id)
);

-- 6. Snapshot de Estoque
CREATE TABLE IF NOT EXISTS estoque_snapshot (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    data            DATE NOT NULL,
    produto_id      INTEGER NOT NULL REFERENCES produtos(id),
    quantidade      NUMERIC(10,3) NOT NULL CHECK (quantidade >= 0),
    unidade_medida  VARCHAR(20),
    estoque_minimo  NUMERIC(10,3),
    estoque_maximo  NUMERIC(10,3),
    custo_unitario  NUMERIC(10,2),
    registrado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (data, produto_id)
);

-- 7. Movimentação de Estoque
CREATE TABLE IF NOT EXISTS movimentacao_estoque (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    data            DATE NOT NULL,
    produto_id      INTEGER NOT NULL REFERENCES produtos(id),
    tipo            VARCHAR(20) NOT NULL CHECK (tipo IN ('entrada','saida','ajuste','perda')),
    quantidade      NUMERIC(10,3) NOT NULL,
    motivo          VARCHAR(100),
    registrado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Histórico de Previsões
CREATE TABLE IF NOT EXISTS historico_previsoes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    data_previsao       DATE NOT NULL,
    produto_id          INTEGER NOT NULL REFERENCES produtos(id),
    turno_id            INTEGER NOT NULL REFERENCES turnos(id),
    quantidade_prevista REAL NOT NULL CHECK (quantidade_prevista >= 0),
    modelo_utilizado    VARCHAR(100),
    gerado_em           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
