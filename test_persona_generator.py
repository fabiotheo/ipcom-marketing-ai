#!/usr/bin/env python3
"""
🎯 TESTE DO INTERACTIVE BUYER PERSONA GENERATOR
==================================================

Este script demonstra como usar a nova funcionalidade de 
geração de personas baseada na metodologia de Adele Revella.
"""

import sys
import asyncio
import json
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from osp_marketing_tools.interview_engine import InterviewEngine
from osp_marketing_tools.persona_builder import PersonaBuilder


def test_interview_flow():
    """Testa o fluxo de entrevista interativa."""
    
    print("🎯 INTERACTIVE BUYER PERSONA GENERATOR")
    print("=" * 60)
    print("Baseado na metodologia de Adele Revella - 5 Rings of Buying Insight")
    print()
    
    # Inicializar engine
    engine = InterviewEngine()
    
    # Começar entrevista
    session_id, first_question = engine.start_interview(
        "FlowDesk Pro - Plataforma de Produtividade com IA"
    )
    
    print(f"📋 Session ID: {session_id}")
    print()
    
    # Mostrar primeira pergunta
    q = first_question["question"]
    progress = first_question["progress"]
    
    print(f"🎭 Ring Atual: {progress['current_ring']}")
    print(f"📊 Progresso: {progress['ring_progress']} rings | {progress['percentage']:.0f}% concluído")
    print()
    print(f"❓ PERGUNTA 1:")
    print(f"   {q['text']}")
    print()
    print(f"💡 Contexto: {q['context']}")
    print(f"✅ Obrigatória: {'Sim' if q['required'] else 'Não'}")
    print()
    
    # Simular algumas respostas
    print("🤖 SIMULANDO RESPOSTAS DE EXEMPLO:")
    print("-" * 40)
    
    responses = [
        "Nossa equipe estava perdendo 3+ horas por dia organizando emails e tarefas manualmente. O CEO exigiu uma solução até o final do trimestre.",
        "A pressão veio do board que viu nossos concorrentes lançando produtos 50% mais rápido que nós.",
        "O sistema atual falha constantemente e nossa produtividade caiu 30% nos últimos 6 meses.",
        "Esperamos recuperar pelo menos 2 horas por pessoa por dia e aumentar nossa velocidade de entrega em 40%.",
        "Sucesso pessoal seria ter tempo para focar em estratégia ao invés de tarefas operacionais."
    ]
    
    current_response = 0
    
    for i in range(min(5, len(responses))):
        # Dar resposta
        response = responses[current_response]
        print(f"💬 Resposta {i+1}: {response}")
        
        # Processar resposta
        result = engine.answer_question(session_id, response)
        
        if "question" in result:
            q = result["question"]
            progress = result["progress"]
            print(f"📊 Progresso: {progress['percentage']:.0f}%")
            print(f"❓ Próxima pergunta: {q['text'][:100]}...")
        else:
            print("✅ Entrevista concluída!")
            break
            
        print()
        current_response += 1
    
    # Obter summary
    summary = engine.get_interview_summary(session_id)
    print("📋 RESUMO DA ENTREVISTA:")
    print(f"   - Respostas coletadas: {summary['total_responses']}")
    print(f"   - Rings explorados: {', '.join(summary['rings_covered'])}")
    print(f"   - Status: {summary['status']}")
    
    return session_id


async def test_persona_generation():
    """Testa a geração completa de persona."""
    
    print("\n🚀 TESTANDO GERAÇÃO DE PERSONA COMPLETA")
    print("=" * 60)
    
    # Para este teste, vamos simular uma sessão completa
    session_id = test_interview_flow()
    
    print("\n🔄 Gerando persona completa...")
    
    try:
        builder = PersonaBuilder()
        
        # NOTA: Este teste pode falhar porque requer sessão completa
        # Em um uso real, você completaria todas as 14 perguntas
        print("⚠️  Para geração completa, complete todas as 14 perguntas da entrevista")
        print("🎯 Este é apenas um teste da estrutura básica")
        
        # Mostrar como seria usado:
        print("\n📝 CÓDIGO DE EXEMPLO PARA USO REAL:")
        print("```python")
        print("# Após completar todas as perguntas:")
        print("persona_result = await builder.build_persona_from_interview(")
        print("    session_id, 'Tech Director - SaaS Company'")
        print(")")
        print("print(json.dumps(persona_result, indent=2))")
        print("```")
        
    except Exception as e:
        print(f"ℹ️  Esperado: {e}")
        print("💡 Complete a entrevista inteira para gerar a persona final")


def main():
    """Função principal de teste."""
    
    print("🧪 TESTANDO NOVA FUNCIONALIDADE - BUYER PERSONA GENERATOR")
    print("=" * 70)
    print("Metodologia: Adele Revella's 5 Rings of Buying Insight")
    print("Componentes: 7 novos módulos Python + 3 ferramentas MCP")
    print()
    
    # Teste 1: Fluxo de entrevista
    test_interview_flow()
    
    # Teste 2: Geração de persona (simulado)
    asyncio.run(test_persona_generation())
    
    print("\n✅ TESTE CONCLUÍDO!")
    print("🎯 Para usar em produção:")
    print("   1. Complete todas as 14 perguntas da entrevista")
    print("   2. Use PersonaBuilder.build_persona_from_interview()")
    print("   3. Analise o relatório de qualidade gerado")
    print("   4. Use as ferramentas MCP para integração com Claude")


if __name__ == "__main__":
    main()