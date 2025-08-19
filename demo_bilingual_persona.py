#!/usr/bin/env python3
"""
🌍 DEMO - INTERACTIVE BUYER PERSONA GENERATOR BILÍNGUE
======================================================

Demonstração do sistema em Português Brasileiro e Inglês.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from osp_marketing_tools.i18n_questions import QuestionTranslations
from osp_marketing_tools.interview_engine import InterviewEngine


def demo_language_selection():
    """Demo da seleção de idioma."""

    print("🌍 INTERACTIVE BUYER PERSONA GENERATOR - BILINGUAL")
    print("=" * 60)
    print("✨ Nova funcionalidade: Suporte bilíngue!")
    print()

    # Mostrar idiomas disponíveis
    print("🗣️  IDIOMAS DISPONÍVEIS:")
    for lang_code, info in QuestionTranslations.get_language_info().items():
        print(f"   {info['flag']} {lang_code}: {info['name']}")
    print()

    return "pt-br"  # Para demo, usar português


def demo_portuguese():
    """Demo em português brasileiro."""

    print("🇧🇷 DEMO EM PORTUGUÊS BRASILEIRO")
    print("=" * 50)

    # Inicializar em português
    engine = InterviewEngine(language="pt-br")

    # Começar entrevista
    session_id, question_data = engine.start_interview(
        "FlowDesk Pro - Plataforma de Produtividade com IA"
    )

    print(f"📋 Sessão: {session_id[:8]}...")
    print()

    # Primeira pergunta
    q = question_data["question"]
    progress = question_data["progress"]

    print(f"🎭 Anel: {progress['current_ring']} ({q['ring_name']})")
    print(f"📊 Progresso: {progress['ring_progress']}")
    print()
    print("❓ PERGUNTA 1:")
    print(f"   {q['text']}")
    print()
    print(f"💡 Contexto: {q['context']}")
    print()
    print("📝 Contexto da entrevista:")
    print(f"   {question_data['context']}")
    print()

    # Simular resposta em português
    print("💬 RESPOSTA DE EXEMPLO:")
    resposta = (
        "Nossa equipe estava perdendo mais de 3 horas por dia organizando "
        "emails e tarefas manualmente. O CEO exigiu uma solução até o final "
        "do trimestre depois que viu nossos concorrentes lançando produtos "
        "50% mais rápido que nós."
    )
    print(f"   '{resposta}'")
    print()

    # Processar resposta
    result = engine.answer_question(session_id, resposta)

    if "question" in result:
        next_q = result["question"]
        new_progress = result["progress"]

        print(f"📊 Progresso atualizado: {new_progress['percentage']:.0f}%")
        print()
        print("❓ PRÓXIMA PERGUNTA:")
        print(f"   {next_q['text']}")
        print()
        print(f"💡 {next_q['context']}")

    return session_id


def demo_english():
    """Demo em inglês."""

    print("\n🇺🇸 DEMO IN ENGLISH")
    print("=" * 50)

    # Inicializar em inglês
    engine = InterviewEngine(language="en")

    # Começar entrevista
    session_id, question_data = engine.start_interview(
        "FlowDesk Pro - AI-Powered Productivity Platform"
    )

    print(f"📋 Session: {session_id[:8]}...")
    print()

    # Primeira pergunta
    q = question_data["question"]
    progress = question_data["progress"]

    print(f"🎭 Ring: {progress['current_ring']} ({q['ring_name']})")
    print(f"📊 Progress: {progress['ring_progress']}")
    print()
    print("❓ QUESTION 1:")
    print(f"   {q['text']}")
    print()
    print(f"💡 Context: {q['context']}")
    print()
    print("📝 Interview context:")
    print(f"   {question_data['context']}")
    print()

    # Simular resposta em inglês
    print("💬 SAMPLE RESPONSE:")
    response = (
        "Our team was losing 3+ hours per day organizing emails and tasks manually. "
        "The CEO demanded a solution by end of quarter after seeing our competitors "
        "shipping products 50% faster than us."
    )
    print(f"   '{response}'")
    print()

    # Processar resposta
    result = engine.answer_question(session_id, response)

    if "question" in result:
        next_q = result["question"]
        new_progress = result["progress"]

        print(f"📊 Updated progress: {new_progress['percentage']:.0f}%")
        print()
        print("❓ NEXT QUESTION:")
        print(f"   {next_q['text']}")
        print()
        print(f"💡 {next_q['context']}")

    return session_id


def demo_comparison():
    """Mostra comparação lado a lado."""

    print("\n📊 COMPARAÇÃO LADO A LADO")
    print("=" * 60)

    # Mostrar primeira pergunta em ambos idiomas
    pt_question = QuestionTranslations.get_question_by_id("priority_trigger", "pt-br")
    en_question = QuestionTranslations.get_question_by_id("priority_trigger", "en")

    print("❓ MESMA PERGUNTA EM AMBOS OS IDIOMAS:")
    print()
    print("🇺🇸 English:")
    print(f"   Q: {en_question['question']}")
    print(f"   Context: {en_question['context']}")
    print()
    print("🇧🇷 Português:")
    print(f"   P: {pt_question['question']}")
    print(f"   Contexto: {pt_question['context']}")
    print()

    # Mostrar nomes dos rings
    print("🎭 NOMES DOS RINGS/ANÉIS:")
    print()
    from osp_marketing_tools.persona_data_structures import RingType

    for ring in RingType:
        en_name = QuestionTranslations.get_ring_name(ring, "en")
        pt_name = QuestionTranslations.get_ring_name(ring, "pt-br")
        print(f"   🇺🇸 {en_name} | 🇧🇷 {pt_name}")


def show_implementation_details():
    """Mostra detalhes da implementação."""

    print("\n🔧 DETALHES DA IMPLEMENTAÇÃO")
    print("=" * 50)
    print("✅ Funcionalidades implementadas:")
    print("   • Sistema i18n completo")
    print("   • 14 perguntas traduzidas em ambos idiomas")
    print("   • Nomes dos rings localizados")
    print("   • Contextos e mensagens traduzidas")
    print("   • Seleção automática de idioma")
    print("   • Fallback para inglês se idioma não suportado")
    print()
    print("📁 Arquivos criados/modificados:")
    print("   • i18n_questions.py - Sistema de traduções")
    print("   • interview_engine.py - Suporte bilíngue")
    print()
    print("🗣️  Idiomas suportados:")
    print("   • en (English) - Estados Unidos")
    print("   • pt-br (Português Brasileiro) - Brasil")
    print()
    print("💡 Como usar:")
    print("   engine = InterviewEngine(language='pt-br')")
    print("   engine = InterviewEngine(language='en')")


if __name__ == "__main__":
    # Seleção de idioma
    selected_lang = demo_language_selection()

    # Demo em português
    demo_portuguese()

    # Demo em inglês
    demo_english()

    # Comparação
    demo_comparison()

    # Detalhes
    show_implementation_details()

    print("\n🎉 DEMO BILÍNGUE CONCLUÍDA!")
    print("🌍 Agora o sistema suporta Português e Inglês!")
    print("💡 Use: InterviewEngine(language='pt-br') ou InterviewEngine(language='en')")
