# -*- coding: utf-8 -*-
"""
Script para Popular o Banco de Dados com Dados Iniciais
"""
from database.connection import db
from database.dao import *


def seed_database():
    """Popula o banco com dados iniciais"""
    
    print("🌱 Iniciando população do banco de dados...")
    
    # 1. Categorias
    print("📦 Criando categorias...")
    categorias = [
        {"nome": "Escritório", "descricao": "Materiais de escritório"},
        {"nome": "Tecnologia", "descricao": "Produtos tecnológicos"},
        {"nome": "Vestuário", "descricao": "Roupas e uniformes"},
        {"nome": "Acessórios", "descricao": "Acessórios diversos"},
        {"nome": "Material Promocional", "descricao": "Material para divulgação"},
    ]
    
    for cat in categorias:
        try:
            CategoriaDAO.create(cat)
            print(f"  ✓ {cat['nome']}")
        except:
            print(f"  ⚠ {cat['nome']} já existe")
    
    # 2. Unidades de Medida
    print("\n📏 Criando unidades de medida...")
    unidades = [
        {"codigo": "UN", "nome": "Unidade", "descricao": "Unidade simples"},
        {"codigo": "KG", "nome": "Quilograma", "descricao": "Peso em quilogramas"},
        {"codigo": "LT", "nome": "Litro", "descricao": "Volume em litros"},
        {"codigo": "CX", "nome": "Caixa", "descricao": "Caixa fechada"},
        {"codigo": "PC", "nome": "Peça", "descricao": "Peça individual"},
        {"codigo": "MT", "nome": "Metro", "descricao": "Comprimento em metros"},
        {"codigo": "M²", "nome": "Metro Quadrado", "descricao": "Área em metros quadrados"},
    ]
    
    for un in unidades:
        try:
            UnidadeDAO.create(un)
            print(f"  ✓ {un['codigo']} - {un['nome']}")
        except:
            print(f"  ⚠ {un['codigo']} já existe")
    
    # 3. Filiais
    print("\n🏢 Criando filiais...")
    filiais = [
        {
            "numero": "001",
            "nome": "Matriz",
            "cidade": "São Paulo",
            "estado": "SP",
            "endereco": "Av. Paulista, 1000",
            "telefone": "(11) 3000-0000",
            "email": "matriz@empresa.com",
            "responsavel": "João Silva"
        },
        {
            "numero": "002",
            "nome": "Filial RJ",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "endereco": "Av. Atlântica, 500",
            "telefone": "(21) 3000-0000",
            "email": "rj@empresa.com",
            "responsavel": "Maria Santos"
        },
        {
            "numero": "003",
            "nome": "Filial BH",
            "cidade": "Belo Horizonte",
            "estado": "MG",
            "endereco": "Av. Afonso Pena, 200",
            "telefone": "(31) 3000-0000",
            "email": "bh@empresa.com",
            "responsavel": "Carlos Oliveira"
        },
        {
            "numero": "004",
            "nome": "Filial BSB",
            "cidade": "Brasília",
            "estado": "DF",
            "endereco": "SCS Quadra 1",
            "telefone": "(61) 3000-0000",
            "email": "bsb@empresa.com",
            "responsavel": "Ana Costa"
        },
    ]
    
    for fil in filiais:
        try:
            FilialDAO.create(fil)
            print(f"  ✓ {fil['numero']} - {fil['nome']}")
        except:
            print(f"  ⚠ {fil['numero']} já existe")
    
    # 4. Usuários
    print("\n👤 Criando usuários...")
    usuarios = [
        {
            "nome": "Administrador",
            "username": "admin",
            "email": "admin@empresa.com",
            "perfil": "ADMIN",
            "filial_id": 1
        },
        {
            "nome": "Gestor SP",
            "username": "gestor.sp",
            "email": "gestor.sp@empresa.com",
            "perfil": "GESTOR",
            "filial_id": 1
        },
        {
            "nome": "Gestor RJ",
            "username": "gestor.rj",
            "email": "gestor.rj@empresa.com",
            "perfil": "GESTOR",
            "filial_id": 2
        },
        {
            "nome": "Usuário SP",
            "username": "user.sp",
            "email": "user.sp@empresa.com",
            "perfil": "USUARIO",
            "filial_id": 1
        },
    ]
    
    for usr in usuarios:
        try:
            UsuarioDAO.create(usr)
            print(f"  ✓ {usr['nome']} ({usr['perfil']})")
        except:
            print(f"  ⚠ {usr['username']} já existe")
    
    # 5. Fornecedores
    print("\n🏭 Criando fornecedores...")
    fornecedores = [
        {
            "nome": "Brindes & Cia",
            "cnpj": "12.345.678/0001-90",
            "contato": "Pedro Alves",
            "telefone": "(11) 4000-0000",
            "email": "contato@brindese cia.com",
            "endereco": "Rua das Flores, 100",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01000-000",
            "observacoes": "Fornecedor principal"
        },
        {
            "nome": "Promo Gifts",
            "cnpj": "98.765.432/0001-10",
            "contato": "Lucia Ferreira",
            "telefone": "(21) 4000-0000",
            "email": "vendas@promogifts.com",
            "endereco": "Av. Brasil, 2000",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "cep": "20000-000",
            "observacoes": "Especializado em tecnologia"
        },
    ]
    
    for forn in fornecedores:
        try:
            FornecedorDAO.create(forn)
            print(f"  ✓ {forn['nome']}")
        except:
            print(f"  ⚠ {forn['nome']} já existe")
    
    # 6. Brindes de Exemplo
    print("\n🎁 Criando brindes de exemplo...")
    brindes = [
        {
            "descricao": "Caneta Personalizada Azul",
            "quantidade": 500,
            "valor_unitario": 2.50,
            "categoria_id": 1,
            "unidade_id": 1,
            "filial_id": 1,
            "fornecedor_id": 1,
            "codigo_interno": "CAN-001",
            "estoque_minimo": 100
        },
        {
            "descricao": "Mouse Pad Corporativo",
            "quantidade": 150,
            "valor_unitario": 12.00,
            "categoria_id": 2,
            "unidade_id": 1,
            "filial_id": 1,
            "fornecedor_id": 2,
            "codigo_interno": "MOU-001",
            "estoque_minimo": 50
        },
        {
            "descricao": "Camiseta Polo Branca M",
            "quantidade": 80,
            "valor_unitario": 35.00,
            "categoria_id": 3,
            "unidade_id": 5,
            "filial_id": 2,
            "fornecedor_id": 1,
            "codigo_interno": "CAM-M-001",
            "estoque_minimo": 20
        },
        {
            "descricao": "Squeeze de Alumínio 500ml",
            "quantidade": 200,
            "valor_unitario": 18.50,
            "categoria_id": 4,
            "unidade_id": 1,
            "filial_id": 1,
            "fornecedor_id": 1,
            "codigo_interno": "SQU-001",
            "estoque_minimo": 50
        },
        {
            "descricao": "Pen Drive 16GB",
            "quantidade": 5,
            "valor_unitario": 25.00,
            "categoria_id": 2,
            "unidade_id": 1,
            "filial_id": 3,
            "fornecedor_id": 2,
            "codigo_interno": "PEN-16GB",
            "estoque_minimo": 10
        },
        {
            "descricao": "Sacola Ecológica",
            "quantidade": 300,
            "valor_unitario": 8.00,
            "categoria_id": 5,
            "unidade_id": 1,
            "filial_id": 1,
            "fornecedor_id": 1,
            "codigo_interno": "SAC-001",
            "estoque_minimo": 100
        },
    ]
    
    for brinde in brindes:
        try:
            BrindeDAO.create(brinde)
            print(f"  ✓ {brinde['descricao']}")
        except:
            print(f"  ⚠ {brinde['descricao']} já existe")
    
    print("\n✅ População do banco de dados concluída!")


if __name__ == "__main__":
    seed_database()
