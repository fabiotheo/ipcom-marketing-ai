#!/usr/bin/env python3
"""
🎯 DEMO - INTERACTIVE BUYER PERSONA GENERATOR
==============================================

Demonstração da nova funcionalidade de geração de personas
baseada na metodologia 5 Rings de Adele Revella.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from osp_marketing_tools.interview_engine import InterviewEngine


def demo_interview():
    """Demo do sistema de entrevista."""

    print("🎯 INTERACTIVE BUYER PERSONA GENERATOR")
    print("=" * 60)
    print("✨ Nova funcionalidade baseada na metodologia de Adele Revella")
    print("🎭 5 Rings of Buying Insight")
    print()

    # Inicializar
    engine = InterviewEngine()

    # Começar entrevista
    session_id, question_data = engine.start_interview(
        "FlowDesk Pro - Plataforma de Produtividade com IA"
    )

    print(f"📋 Session: {session_id[:8]}...")
    print()

    # Primeira pergunta
    q = question_data["question"]
    progress = question_data["progress"]

    print(f"🎭 Ring: {progress['current_ring']}")
    print(f"📊 Progresso: {progress['ring_progress']}")
    print()
    print("❓ PERGUNTA 1 (Priority Initiative):")
    print(f"   {q['text']}")
    print()
    print(f"💡 {q['context']}")
    print()

    # Simular resposta
    print("💬 RESPOSTA DE EXEMPLO:")
    resposta = (
        "Nossa equipe perde 3+ horas por dia organizando emails e tarefas. "
        "O CEO exigiu uma solução até o final do trimestre após ver nossos "
        "concorrentes lançando produtos 50% mais rápido."
    )
    print(f"   '{resposta}'")
    print()

    # Processar resposta
    result = engine.answer_question(session_id, resposta)

    if "question" in result:
        next_q = result["question"]
        new_progress = result["progress"]

        print(f"📊 Novo progresso: {new_progress['percentage']:.0f}%")
        print()
        print("❓ PRÓXIMA PERGUNTA:")
        print(f"   {next_q['text']}")
        print()

    # Estatísticas
    print("📊 ESTATÍSTICAS:")
    print(f"   - Total de perguntas: 14")
    print(f"   - Rings a explorar: 5")
    print(f"   - Tempo estimado: 10-15 minutos")
    print()

    print("🎯 FUNCIONALIDADES DISPONÍVEIS:")
    print("   ✅ Interview Engine - Perguntas inteligentes")
    print("   ✅ Quality Assurance - Validação científica")
    print("   ✅ Market Research - Pesquisa automatizada")
    print("   ✅ Persona Builder - Geração completa")
    print("   ✅ MCP Tools - Integração com Claude")
    print()

    print("📝 PRÓXIMOS PASSOS:")
    print("   1. Complete todas as 14 perguntas")
    print("   2. O sistema gera persona completa")
    print("   3. Relatório de qualidade incluído")
    print("   4. Use via MCP tools no Claude")
    print()

    print("🚀 STATUS: ✅ FUNCIONAL E DISPONÍVEL!")

    return session_id


def show_methodology():
    """Mostra a metodologia implementada."""

    print("\n📚 METODOLOGIA IMPLEMENTADA")
    print("=" * 40)
    print("🎓 Adele Revella's 5 Rings of Buying Insight:")
    print()
    print("1️⃣ PRIORITY INITIATIVE")
    print("   ↳ O que motivou a busca por solução AGORA?")
    print()
    print("2️⃣ SUCCESS FACTORS")
    print("   ↳ Que resultados específicos são esperados?")
    print()
    print("3️⃣ PERCEIVED BARRIERS")
    print("   ↳ Que obstáculos o comprador vê?")
    print()
    print("4️⃣ DECISION CRITERIA")
    print("   ↳ Como avaliam e comparam fornecedores?")
    print()
    print("5️⃣ BUYER'S JOURNEY")
    print("   ↳ Como navegam o processo de decisão?")
    print()


def show_mcp_tools():
    """Mostra as ferramentas MCP disponíveis."""

    print("🔧 FERRAMENTAS MCP DISPONÍVEIS")
    print("=" * 40)
    print("Use no Claude Code via MCP:")
    print()
    print("🎯 start_buyer_persona_interview")
    print("   ↳ Inicia nova entrevista de persona")
    print()
    print("💬 answer_persona_question")
    print("   ↳ Responde pergunta da entrevista")
    print()
    print("📊 generate_buyer_persona")
    print("   ↳ Gera persona completa da sessão")
    print()


if __name__ == "__main__":
    demo_interview()
    show_methodology()
    show_mcp_tools()

    print("\n🎉 DEMO CONCLUÍDA!")
    print("💡 Teste completo via npm: npx ipcom-marketing-ai@0.3.6")
