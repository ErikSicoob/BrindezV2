# -*- coding: utf-8 -*-
"""
Script para adicionar comentário de versão em todos os arquivos Python
"""
import os
from datetime import datetime

def update_file(filepath):
    """Adiciona comentário no final do arquivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adicionar comentário de versão no final
        version_comment = f"\n# Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # Verificar se já tem o comentário
        if "# Updated:" not in content:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(version_comment)
            print(f"✓ {filepath}")
            return True
        else:
            print(f"⊘ {filepath} (já atualizado)")
            return False
    except Exception as e:
        print(f"✗ {filepath}: {e}")
        return False

def main():
    """Atualiza todos os arquivos Python"""
    print("🔄 Atualizando arquivos Python...\n")
    
    updated = 0
    skipped = 0
    errors = 0
    
    # Percorrer todos os arquivos .py
    for root, dirs, files in os.walk('.'):
        # Ignorar diretórios
        if '.venv' in root or '__pycache__' in root or '.git' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                result = update_file(filepath)
                if result:
                    updated += 1
                elif result is False:
                    skipped += 1
                else:
                    errors += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Atualizado: {updated}")
    print(f"⊘ Ignorado: {skipped}")
    print(f"✗ Erros: {errors}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
