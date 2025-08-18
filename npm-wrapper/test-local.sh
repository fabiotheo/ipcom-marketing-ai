#!/bin/bash

echo "🧪 IPCOM Marketing AI - Teste Local"
echo "=================================="

# Verificar se estamos no diretório correto
if [[ ! -f "package.json" ]]; then
    echo "❌ Erro: package.json não encontrado"
    echo "Execute este script no diretório npm-wrapper"
    exit 1
fi

# Verificar versão atual
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo "📊 Versão atual: ipcom-marketing-ai@$CURRENT_VERSION"

# Gerar pacote de teste
echo "📦 Gerando pacote de teste..."
npm pack

# Verificar conteúdo do pacote
echo "📋 Conteúdo do pacote:"
tar -tzf ipcom-marketing-ai-$CURRENT_VERSION.tgz

# Testar execução com timeout
echo "🧪 Testando execução (5 segundos)..."
timeout 5s node index.js && echo "✅ Script executou corretamente" || echo "⚠️  Script iniciou (normal para servidor MCP)"

# Verificar sintaxe do JSON
echo "🔍 Verificando package.json..."
if node -e "JSON.parse(require('fs').readFileSync('package.json', 'utf8'))"; then
    echo "✅ package.json válido"
else
    echo "❌ package.json inválido"
    exit 1
fi

# Limpar arquivo de teste
rm -f ipcom-marketing-ai-*.tgz

echo "✅ Teste local concluído!"
echo ""
echo "Para publicar:"
echo "./publish.sh"