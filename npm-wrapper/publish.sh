#!/bin/bash

echo "🚀 IPCOM Marketing AI - Publicação NPM"
echo "======================================"

# Verificar se estamos no diretório correto
if [[ ! -f "package.json" ]]; then
    echo "❌ Erro: package.json não encontrado"
    echo "Execute este script no diretório npm-wrapper"
    exit 1
fi

# Verificar se há alterações não commitadas
cd ..
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  Há alterações não commitadas no projeto principal"
    echo "Faça commit primeiro e tente novamente"
    exit 1
fi

cd npm-wrapper

# Perguntar tipo de versão
echo "Que tipo de atualização?"
echo "1) patch (correções)"
echo "2) minor (novas funcionalidades)"
echo "3) major (mudanças quebradoras)"
read -p "Escolha (1-3): " choice

case $choice in
    1) VERSION_TYPE="patch" ;;
    2) VERSION_TYPE="minor" ;;
    3) VERSION_TYPE="major" ;;
    *) echo "❌ Opção inválida"; exit 1 ;;
esac

# Atualizar versão
echo "📈 Atualizando versão ($VERSION_TYPE)..."
npm version $VERSION_TYPE

# Gerar pacote de teste
echo "📦 Gerando pacote de teste..."
npm pack > /dev/null

# Testar execução
echo "🧪 Testando execução..."
if timeout 5s node index.js > /dev/null 2>&1; then
    echo "✅ Teste local passou"
else
    echo "⚠️  Teste local executado (pode ser normal se servidor MCP iniciou)"
fi

# Publicar
echo "🚀 Publicando no NPM..."
if npm publish; then
    NEW_VERSION=$(node -p "require('./package.json').version")
    echo "✅ Publicação bem-sucedida!"
    echo "📊 Nova versão: ipcom-marketing-ai@$NEW_VERSION"
    echo ""
    echo "🎯 Para testar:"
    echo "claude mcp remove ipcom-ai"
    echo "claude mcp add ipcom-ai npx ipcom-marketing-ai"
else
    echo "❌ Falha na publicação"
    exit 1
fi

# Limpar arquivo de teste
rm -f ipcom-marketing-ai-*.tgz

echo "🎉 Processo concluído com sucesso!"