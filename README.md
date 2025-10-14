#  Sistema de Gestão de Brindes

Sistema completo de controle de estoque de brindes com interface gráfica moderna usando CustomTkinter e banco de dados SQLite.

##  Requisitos

- Python 3.8 ou superior
- CustomTkinter
- Pillow Funcionalidades

###  Dashboard
- Indicadores de estoque em tempo real
- Gráfico de distribuição por categoria
- Alertas de estoque baixo
- Filtro por filial (para administradores)

###  Configurações

#### Fornecedores
- Cadastro completo com CNPJ, contato, endereço
- Ativar/Desativar/Excluir
- Controle de brindes associados

#### Usuários (Apenas ADMIN)
- 3 perfis: Administrador, Gestor, Usuário
- Integração com login Windows
- Controle de acesso por filial

#### Filiais (Apenas ADMIN)
- Gestão de filiais/unidades
- Controle de usuários e brindes
- Validação de dependências

###  Controle de Acesso

**Perfis de Usuário**:
- **Administrador**: Acesso total ao sistema
- **Gestor**: Gerencia estoque de sua filial
- **Usuário**: Visualização e saídas de estoque

**Permissões**:
- Apenas ADMIN pode gerenciar usuários e filiais
- Apenas ADMIN pode excluir/desativar registros
- Usuários veem apenas sua filial (exceto ADMIN)
##  Desenvolvimento

**Tecnologias**:
- Python 3.8+
- CustomTkinter (GUI)
- SQLite (Banco de dados)
- Pillow (Imagens)

##  Licença

Este projeto é proprietário e de uso interno.

---

**Versão**: 1.0.0  
**Última Atualização**: 13/10/2025
