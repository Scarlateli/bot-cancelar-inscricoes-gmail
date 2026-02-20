#!/bin/bash

# Navegar para o diretório do script (funciona de qualquer lugar)
cd "$(dirname "$0")"

echo "🔧 Configurando Bot de Cancelamento de Inscrições Gmail..."
echo ""

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
else
    echo "✓ Ambiente virtual já existe"
fi

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "Para executar o bot, use: ./executar.sh"
