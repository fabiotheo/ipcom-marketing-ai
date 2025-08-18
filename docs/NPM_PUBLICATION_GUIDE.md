# Manual de Publicação NPM - IPCOM Marketing AI

## 📋 **Visão Geral**

Este manual descreve o processo completo para publicar e atualizar o pacote `ipcom-marketing-ai` no NPM sempre que houver alterações no projeto.

## 🔄 **Fluxo de Publicação**

### **Quando Publicar:**
- ✅ Novas funcionalidades implementadas
- ✅ Correções de bugs importantes
- ✅ Atualizações de documentação significativas
- ✅ Mudanças na estrutura do projeto
- ✅ Atualizações de dependências

---

## 📚 **Pré-requisitos**

### **1. Conta NPM**
- Ter conta ativa no [npmjs.com](https://npmjs.com)
- Ter acesso de publicação ao pacote `ipcom-marketing-ai`

### **2. Autenticação**
```bash
# Fazer login no NPM (uma vez por máquina)
npm login
```

### **3. Ferramentas**
- Node.js 18+
- npm ou yarn
- Git configurado

---

## 🚀 **Processo de Publicação**

### **Passo 1: Preparar Alterações no Projeto Principal**

```bash
# Navegar para o diretório do projeto
cd /Users/fabiotheodoro/IPCOM/DEV/osp_marketing_tools

# Verificar status
git status

# Adicionar alterações
git add .

# Commit das alterações
git commit -m "feat: descrição das alterações

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push para GitHub
git push github main
```

### **Passo 2: Atualizar Versão do NPM**

```bash
# Navegar para o wrapper NPM
cd npm-wrapper

# Verificar versão atual
npm version

# Atualizar versão (escolha uma opção):
npm version patch    # Para correções (0.3.0 → 0.3.1)
npm version minor    # Para novas funcionalidades (0.3.0 → 0.4.0)
npm version major    # Para mudanças quebradoras (0.3.0 → 1.0.0)
```

### **Passo 3: Atualizar Documentação NPM (Se Necessário)**

**Editar `README.md` se houver:**
- Novos recursos
- Mudanças nos comandos
- Novos exemplos de uso

**Verificar `package.json`:**
- Keywords atualizadas
- Descrição atualizada
- Links corretos

### **Passo 4: Testar Localmente**

```bash
# Gerar pacote local
npm pack

# Testar execução
node index.js --version
```

### **Passo 5: Publicar no NPM**

```bash
# Publicar nova versão
npm publish

# Verificar publicação
npm view ipcom-marketing-ai
```

### **Passo 6: Testar Instalação**

```bash
# Testar instalação global
npm install -g ipcom-marketing-ai@latest

# Testar com Claude Code
claude mcp remove ipcom-ai
claude mcp add ipcom-ai npx ipcom-marketing-ai

# Verificar funcionamento
npx ipcom-marketing-ai
```

---

## 📝 **Checklist de Publicação**

### **Antes de Publicar:**
- [ ] Código principal commitado e pushed
- [ ] Versão atualizada no package.json
- [ ] README.md do NPM atualizado se necessário
- [ ] Teste local executado com sucesso
- [ ] Login no NPM realizado

### **Durante a Publicação:**
- [ ] `npm publish` executado sem erros
- [ ] Confirmação da nova versão no npmjs.com
- [ ] Teste de instalação via npx realizado

### **Após a Publicação:**
- [ ] Teste de instalação com Claude Code
- [ ] Verificação das funcionalidades básicas
- [ ] Documentação atualizada se necessário
- [ ] Usuários notificados sobre a atualização (se relevante)

---

## ⚠️ **Versioning Guidelines**

### **Semantic Versioning (SemVer)**

**Formato:** `MAJOR.MINOR.PATCH`

#### **PATCH (0.3.0 → 0.3.1)**
```bash
npm version patch
```
**Quando usar:**
- Correções de bugs
- Pequenos ajustes de documentação
- Correções de segurança
- Otimizações menores

#### **MINOR (0.3.0 → 0.4.0)**
```bash
npm version minor
```
**Quando usar:**
- Novas funcionalidades (backward compatible)
- Novos frameworks de análise
- Melhorias significativas no cache/batch
- Novas ferramentas MCP

#### **MAJOR (0.3.0 → 1.0.0)**
```bash
npm version major
```
**Quando usar:**
- Mudanças que quebram compatibilidade
- Reestruturação completa da API
- Remoção de funcionalidades antigas
- Mudanças nos comandos de instalação

---

## 🔧 **Troubleshooting**

### **Erro: Version Already Exists**
```bash
# Verificar versão atual no NPM
npm view ipcom-marketing-ai version

# Incrementar versão manualmente
npm version patch --force

# Ou editar package.json manualmente
```

### **Erro: Authentication Required**
```bash
# Fazer login novamente
npm logout
npm login

# Verificar autenticação
npm whoami
```

### **Erro: Package Not Found**
```bash
# Verificar se está no diretório correto
pwd
# Deve ser: /Users/fabiotheodoro/IPCOM/DEV/osp_marketing_tools/npm-wrapper

# Verificar se package.json existe
ls -la package.json
```

### **Erro: Publish Failed**
```bash
# Verificar conectividade
npm ping

# Verificar permissões do pacote
npm owner ls ipcom-marketing-ai

# Publicar com debug
npm publish --verbose
```

---

## 🎯 **Scripts Automatizados**

### **Script de Publicação Completa**

Criar arquivo `publish.sh` no diretório `npm-wrapper`:

```bash
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
if node index.js --version > /dev/null 2>&1; then
    echo "✅ Teste local passou"
else
    echo "❌ Teste local falhou"
    exit 1
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
```

**Para usar o script:**
```bash
cd npm-wrapper
chmod +x publish.sh
./publish.sh
```

---

## 📚 **Referências**

- **NPM Documentation**: https://docs.npmjs.com/
- **Semantic Versioning**: https://semver.org/
- **Package.json Guide**: https://docs.npmjs.com/cli/v8/configuring-npm/package-json
- **NPM Publishing**: https://docs.npmjs.com/packages-and-modules/contributing-packages-to-the-registry

---

## 📞 **Suporte**

**Para dúvidas ou problemas:**
1. Verificar este manual primeiro
2. Consultar logs do NPM: `~/.npm/_logs/`
3. Verificar status do NPM: https://status.npmjs.org/
4. Contatar suporte IPCOM se necessário

---

**Última atualização:** 2025-08-18  
**Versão do manual:** 1.0  
**Mantido por:** IPCOM Development Team