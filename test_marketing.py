#!/usr/bin/env python3
"""Teste da análise de marketing"""

import sys

sys.path.append("src")

from osp_marketing_tools.analysis import analyze_content_with_frameworks

# Texto do FlowDesk Pro para análise
content = """
🚀 **Transforme sua produtividade com o FlowDesk Pro!**

Cansado de perder tempo com tarefas repetitivas? Nossa plataforma de automação inteligente usa IA para organizar automaticamente seus emails, agendar reuniões e priorizar suas tarefas mais importantes.

✅ **Resultados comprovados:** Nossos 50.000+ usuários relatam 70% menos tempo perdido em administração
✅ **Tecnologia premiada:** Reconhecida pela TechCrunch como 'Startup do Ano 2024'
✅ **Integração perfeita:** Funciona com Gmail, Outlook, Slack, Notion e mais de 200 ferramentas

**💡 Depoimento real:** 'O FlowDesk me devolveu 3 horas por dia. Agora posso focar no que realmente importa para meu negócio!' - Maria Silva, CEO da TechStart

**🎯 Oferta especial:** Primeiros 1000 usuários ganham 6 meses GRÁTIS + consultoria personalizada de produtividade.

👉 **[Comece grátis agora - sem cartão de crédito]**

*Junte-se à revolução da produtividade. Seus concorrentes já estão na frente.*
"""

print("🎯 ANÁLISE DE MARKETING - FlowDesk Pro")
print("=" * 50)

# Testar diferentes frameworks
frameworks = ["IDEAL", "STEPPS", "E-E-A-T"]

for framework in frameworks:
    print(f"\n📊 Framework: {framework}")
    print("-" * 30)
    result = analyze_content_with_frameworks(content, [framework])

    # Debug: mostrar estrutura completa
    print(f"Resultado completo: {result}")

    if framework in result:
        data = result[framework]
        print(f"Dados do framework: {data}")
        print(f"Score: {data.get('score', 'N/A')}")
        print(f"Análise: {data.get('analysis', 'N/A')}")
        print(f"Recomendações: {data.get('recommendations', 'N/A')}")
    else:
        print(f"Framework não encontrado nos resultados")

print("\n🚀 Teste concluído!")
