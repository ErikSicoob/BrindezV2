-- Dados Iniciais do Sistema
-- Executado apenas se as tabelas estiverem vazias

-- Inserir filial matriz (se não existir)
INSERT OR IGNORE INTO filiais (id, numero, nome, cidade, estado, ativo) 
VALUES (1, '001', 'Matriz - Administrativo', 'São Paulo', 'SP', 1);

-- Inserir usuário administrador padrão (se não existir)
INSERT OR IGNORE INTO usuarios (id, nome, username, email, perfil, filial_id, ativo)
VALUES (1, 'Administrador', 'admin', 'admin@empresa.com', 'ADMIN', 1, 1);

-- Inserir categorias básicas (se não existirem)
INSERT OR IGNORE INTO categorias (nome, descricao, ativo) VALUES
('Eletrônicos', 'Produtos eletrônicos e tecnológicos', 1),
('Vestuário', 'Roupas e acessórios', 1),
('Casa e Decoração', 'Itens para casa e decoração', 1),
('Esportes', 'Artigos esportivos e fitness', 1),
('Alimentação', 'Produtos alimentícios e bebidas', 1);

-- Inserir unidades de medida básicas (se não existirem)
INSERT OR IGNORE INTO unidades_medida (codigo, nome, descricao, ativo) VALUES
('UN', 'Unidade', 'Unidade individual', 1),
('CX', 'Caixa', 'Caixa com múltiplas unidades', 1),
('KG', 'Quilograma', 'Peso em quilogramas', 1),
('LT', 'Litro', 'Volume em litros', 1),
('MT', 'Metro', 'Comprimento em metros', 1),
('PC', 'Peça', 'Peça individual', 1),
('PAR', 'Par', 'Par de itens', 1),
('JG', 'Jogo', 'Conjunto de peças', 1);

-- Inserir fornecedor padrão (se não existir)
INSERT OR IGNORE INTO fornecedores (nome, contato, telefone, email, ativo) VALUES
('Fornecedor Padrão', 'Contato Geral', '(11) 9999-9999', 'contato@fornecedor.com', 1);

-- Updated: 2025-10-14
