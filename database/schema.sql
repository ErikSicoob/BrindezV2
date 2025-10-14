-- Schema do Banco de Dados - Sistema de Gestão de Brindes
-- SQLite Database

-- Tabela de Fornecedores
CREATE TABLE IF NOT EXISTS fornecedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(200) NOT NULL,
    cnpj VARCHAR(18) UNIQUE,
    contato VARCHAR(100),
    telefone VARCHAR(20),
    email VARCHAR(100),
    endereco TEXT,
    cidade VARCHAR(100),
    estado VARCHAR(2),
    cep VARCHAR(10),
    observacoes TEXT,
    ativo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Categorias
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    ativo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Unidades de Medida
CREATE TABLE IF NOT EXISTS unidades_medida (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nome VARCHAR(50) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Filiais
CREATE TABLE IF NOT EXISTS filiais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero VARCHAR(10) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado VARCHAR(2),
    endereco TEXT,
    telefone VARCHAR(20),
    email VARCHAR(100),
    responsavel VARCHAR(100),
    ativo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100),
    perfil VARCHAR(20) NOT NULL CHECK(perfil IN ('ADMIN', 'GESTOR', 'USUARIO')),
    filial_id INTEGER NOT NULL,
    ativo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filial_id) REFERENCES filiais(id)
);

-- Tabela de Brindes
CREATE TABLE IF NOT EXISTS brindes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao VARCHAR(200) NOT NULL,
    quantidade INTEGER NOT NULL DEFAULT 0,
    valor_unitario DECIMAL(10, 2) NOT NULL,
    categoria_id INTEGER NOT NULL,
    unidade_id INTEGER NOT NULL,
    filial_id INTEGER NOT NULL,
    fornecedor_id INTEGER,
    codigo_interno VARCHAR(50),
    observacoes TEXT,
    estoque_minimo INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    FOREIGN KEY (unidade_id) REFERENCES unidades_medida(id),
    FOREIGN KEY (filial_id) REFERENCES filiais(id),
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
);

-- Tabela de Movimentações (Entradas e Saídas)
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brinde_id INTEGER NOT NULL,
    tipo VARCHAR(10) NOT NULL CHECK(tipo IN ('ENTRADA', 'SAIDA')),
    quantidade INTEGER NOT NULL,
    valor_unitario DECIMAL(10, 2),
    usuario_id INTEGER NOT NULL,
    justificativa TEXT,
    data_movimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brinde_id) REFERENCES brindes(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabela de Transferências entre Filiais
CREATE TABLE IF NOT EXISTS transferencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brinde_id INTEGER NOT NULL,
    filial_origem_id INTEGER NOT NULL,
    filial_destino_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    justificativa TEXT NOT NULL,
    data_transferencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brinde_id) REFERENCES brindes(id) ON DELETE CASCADE,
    FOREIGN KEY (filial_origem_id) REFERENCES filiais(id),
    FOREIGN KEY (filial_destino_id) REFERENCES filiais(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabela de Histórico de Alterações (Auditoria)
CREATE TABLE IF NOT EXISTS historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tabela VARCHAR(50) NOT NULL,
    registro_id INTEGER NOT NULL,
    acao VARCHAR(20) NOT NULL CHECK(acao IN ('INSERT', 'UPDATE', 'DELETE')),
    usuario_id INTEGER,
    dados_anteriores TEXT,
    dados_novos TEXT,
    data_acao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabela de Brindes Excluídos (para auditoria)
CREATE TABLE IF NOT EXISTS brindes_excluidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brinde_id_original INTEGER NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    categoria_nome VARCHAR(100),
    unidade_codigo VARCHAR(10),
    filial_nome VARCHAR(100),
    fornecedor_nome VARCHAR(100),
    quantidade INTEGER,
    valor_unitario DECIMAL(10, 2),
    codigo_interno VARCHAR(50),
    observacoes TEXT,
    estoque_minimo INTEGER,
    data_criacao TIMESTAMP,
    data_exclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_exclusao_id INTEGER NOT NULL,
    usuario_exclusao_nome VARCHAR(100) NOT NULL,
    motivo_exclusao TEXT,
    FOREIGN KEY (usuario_exclusao_id) REFERENCES usuarios(id)
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_brindes_categoria ON brindes(categoria_id);
CREATE INDEX IF NOT EXISTS idx_brindes_filial ON brindes(filial_id);
CREATE INDEX IF NOT EXISTS idx_brindes_fornecedor ON brindes(fornecedor_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_brinde ON movimentacoes(brinde_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_data ON movimentacoes(data_movimentacao);
CREATE INDEX IF NOT EXISTS idx_transferencias_brinde ON transferencias(brinde_id);
CREATE INDEX IF NOT EXISTS idx_transferencias_data ON transferencias(data_transferencia);
CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_historico_tabela_registro ON historico(tabela, registro_id);

-- Views úteis

-- View de Estoque Atual por Filial
CREATE VIEW IF NOT EXISTS vw_estoque_atual AS
SELECT 
    b.id,
    b.descricao,
    b.quantidade,
    b.valor_unitario,
    b.quantidade * b.valor_unitario as valor_total,
    b.categoria_id,
    c.nome as categoria,
    b.unidade_id,
    u.codigo as unidade,
    b.filial_id,
    f.nome as filial,
    b.fornecedor_id,
    fo.nome as fornecedor,
    b.codigo_interno,
    b.observacoes,
    b.estoque_minimo,
    b.created_at,
    b.updated_at,
    CASE WHEN b.quantidade <= b.estoque_minimo THEN 1 ELSE 0 END as estoque_baixo
FROM brindes b
INNER JOIN categorias c ON b.categoria_id = c.id
INNER JOIN unidades_medida u ON b.unidade_id = u.id
INNER JOIN filiais f ON b.filial_id = f.id
LEFT JOIN fornecedores fo ON b.fornecedor_id = fo.id;

-- View de Movimentações Completas
CREATE VIEW IF NOT EXISTS vw_movimentacoes_completas AS
SELECT 
    m.id,
    m.brinde_id,
    m.tipo,
    m.quantidade,
    m.valor_unitario,
    m.justificativa,
    m.data_movimentacao,
    b.descricao as brinde,
    u.nome as usuario,
    b.filial_id,
    f.nome as filial
FROM movimentacoes m
INNER JOIN brindes b ON m.brinde_id = b.id
INNER JOIN usuarios u ON m.usuario_id = u.id
INNER JOIN filiais f ON b.filial_id = f.id
ORDER BY m.data_movimentacao DESC;

-- View de Transferências Completas
CREATE VIEW IF NOT EXISTS vw_transferencias_completas AS
SELECT 
    t.id,
    t.brinde_id,
    t.quantidade,
    t.justificativa,
    t.data_transferencia,
    b.descricao as brinde,
    t.filial_origem_id,
    fo.nome as filial_origem,
    t.filial_destino_id,
    fd.nome as filial_destino,
    u.nome as usuario
FROM transferencias t
INNER JOIN brindes b ON t.brinde_id = b.id
INNER JOIN filiais fo ON t.filial_origem_id = fo.id
INNER JOIN filiais fd ON t.filial_destino_id = fd.id
INNER JOIN usuarios u ON t.usuario_id = u.id
ORDER BY t.data_transferencia DESC;

-- Updated: 2025-10-14
