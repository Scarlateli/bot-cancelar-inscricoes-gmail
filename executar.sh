#!/bin/bash

# Navegar para o diretório do script (funciona de qualquer lugar)
cd "$(dirname "$0")"

echo "🤖 Iniciando Bot de Cancelamento de Inscrições..."
echo ""

# Ativar ambiente virtual
source venv/bin/activate

# Executar o bot
python3 bot_email.py
