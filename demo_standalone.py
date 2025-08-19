#!/usr/bin/env python3
"""
Demo Standalone - Interactive Buyer Persona Generator
Funciona independentemente do MCP, permitindo uso direto via CLI.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from osp_marketing_tools.i18n_questions import QuestionTranslations
from osp_marketing_tools.interview_engine import InterviewEngine
from osp_marketing_tools.persona_builder import PersonaBuilder


class StandalonePersonaGenerator:
    """Gerador de personas standalone com interface CLI interativa."""

    def __init__(self):
        self.language = None
        self.engine = None
        self.builder = None
        self.session_id = None
        self.product_context = ""

    def clear_screen(self):
        """Limpa a tela do terminal."""
        import os
        import subprocess

        try:
            # Safer approach using subprocess
            if os.name == "nt":
                subprocess.run(["cls"], shell=True, check=False)
            else:
                subprocess.run(["clear"], check=False)
        except:
            # Fallback: print newlines
            print("\n" * 100)

    def print_header(self):
        """Imprime o cabeçalho do programa."""
        print("=" * 70)
        print(" 🎯 INTERACTIVE BUYER PERSONA GENERATOR - STANDALONE MODE")
        print("=" * 70)
        print(" Based on Adele Revella's 5 Rings of Buying Insight Methodology")
        print("=" * 70)
        print()

    def select_language(self) -> str:
        """Permite ao usuário selecionar o idioma."""
        print("📋 SELECT LANGUAGE / SELECIONE O IDIOMA:")
        print()

        languages = QuestionTranslations.get_language_info()
        options = []

        for idx, (code, info) in enumerate(languages.items(), 1):
            print(f"  {idx}. {info['flag']} {info['name']} ({code})")
            options.append(code)

        print()

        while True:
            try:
                choice = input(
                    "Enter your choice (1-2) / Digite sua escolha (1-2): "
                ).strip()

                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(options):
                        return options[idx]

                # Permitir código direto
                if choice.lower() in options:
                    return choice.lower()

                print("❌ Invalid choice. Please try again.")
                print("❌ Escolha inválida. Tente novamente.\n")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! / Até logo!")
                sys.exit(0)

    def get_product_context(self) -> str:
        """Obtém o contexto do produto do usuário."""
        print("\n📦 PRODUCT/SERVICE CONTEXT:")

        if self.language == "pt-br":
            print("Descreva brevemente seu produto ou serviço (opcional):")
            print("Exemplo: 'Software de gestão para pequenas empresas'")
        else:
            print("Briefly describe your product or service (optional):")
            print("Example: 'Project management software for remote teams'")

        print()
        context = input("> ").strip()

        if not context:
            if self.language == "pt-br":
                context = "Produto ou serviço genérico"
            else:
                context = "Generic product or service"

        return context

    def display_question(self, question_data: Dict, progress: Dict):
        """Exibe uma pergunta formatada."""
        self.clear_screen()
        self.print_header()

        # Progress bar
        percentage = progress.get("percentage", 0)
        filled = int(percentage / 5)  # 20 caracteres total
        bar = "█" * filled + "░" * (20 - filled)

        print(f"📊 PROGRESS: [{bar}] {percentage:.0f}%")
        print(
            f"🎭 Ring: {progress.get('current_ring', '')} ({question_data.get('ring_name', '')})"
        )
        print(
            f"📝 {progress.get('ring_progress', '')} | Question {progress.get('current_question', 0)}/14"
        )
        print()
        print("=" * 70)
        print()

        # Question
        print("❓ QUESTION:")
        print(f"   {question_data.get('text', '')}")
        print()

        # Context
        if question_data.get("context"):
            print("💡 CONTEXT:")
            print(f"   {question_data.get('context', '')}")
            print()

        # Required indicator
        if question_data.get("required"):
            if self.language == "pt-br":
                print("⚠️  Esta pergunta é obrigatória")
            else:
                print("⚠️  This question is required")
        else:
            if self.language == "pt-br":
                print("ℹ️  Opcional - pressione Enter para pular")
            else:
                print("ℹ️  Optional - press Enter to skip")

        print()
        print("-" * 70)
        print()

    def get_user_response(self) -> str:
        """Obtém a resposta do usuário."""
        if self.language == "pt-br":
            print("Sua resposta (ou 'sair' para encerrar):")
        else:
            print("Your answer (or 'quit' to exit):")

        print()

        # Permitir resposta multilinha
        lines = []
        print(
            "📝 (Press Enter twice to submit / Pressione Enter duas vezes para enviar)"
        )
        print()

        empty_count = 0
        while True:
            try:
                line = input()

                if line.lower() in ["quit", "sair", "exit"]:
                    raise KeyboardInterrupt

                if not line:
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                    lines.append(line)

            except KeyboardInterrupt:
                raise

        return " ".join(lines).strip()

    def save_persona(self, persona_data: Dict):
        """Salva a persona gerada em arquivo."""
        import re

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sanitize filename
        safe_timestamp = re.sub(r"[^a-zA-Z0-9_-]", "", timestamp)

        # Salvar JSON
        json_file = f"persona_{safe_timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(persona_data, f, indent=2, ensure_ascii=False)

        # Salvar Markdown
        md_file = f"persona_{safe_timestamp}.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(self.format_persona_markdown(persona_data))

        print()
        print("=" * 70)
        print("✅ FILES SAVED / ARQUIVOS SALVOS:")
        print(f"   📄 {json_file}")
        print(f"   📝 {md_file}")
        print("=" * 70)

    def format_persona_markdown(self, persona: Dict) -> str:
        """Formata a persona como Markdown."""
        md = []
        md.append(f"# Buyer Persona: {persona.get('name', 'Persona')}")
        md.append(f"\n*Generated: {persona.get('created_at', '')}*")
        md.append(f"\n*Language: {self.language}*")
        md.append(
            f"\n*Confidence: {persona.get('quality_metrics', {}).get('overall_confidence', 0):.1f}%*"
        )

        md.append("\n## Executive Summary")
        md.append(persona.get("executive_summary", ""))

        # 5 Rings
        md.append("\n## 5 Rings of Buying Insight")

        for ring_name, ring_data in persona.get("rings", {}).items():
            if isinstance(ring_data, dict) and "insights" in ring_data:
                md.append(f"\n### {ring_name.replace('_', ' ').title()}")
                for insight in ring_data["insights"]:
                    md.append(f"- {insight}")

        # Quality Metrics
        md.append("\n## Quality Metrics")
        metrics = persona.get("quality_metrics", {})
        for metric, value in metrics.items():
            if isinstance(value, (int, float)):
                md.append(f"- **{metric.replace('_', ' ').title()}**: {value:.1f}%")

        # Recommendations
        if "marketing_recommendations" in persona:
            md.append("\n## Marketing Recommendations")
            for rec in persona["marketing_recommendations"]:
                md.append(f"- {rec}")

        return "\n".join(md)

    async def run_interview(self):
        """Executa a entrevista completa."""
        try:
            # Inicializar componentes
            self.engine = InterviewEngine(language=self.language)
            self.builder = PersonaBuilder(language=self.language)

            # Iniciar entrevista
            self.session_id, first_question = self.engine.start_interview(
                product_context=self.product_context
            )

            # Loop de perguntas
            current_question = first_question

            while True:
                # Exibir pergunta
                self.display_question(
                    current_question["question"], current_question["progress"]
                )

                # Obter resposta
                response = self.get_user_response()

                # Processar resposta
                if not response and not current_question["question"].get(
                    "required", False
                ):
                    response = "N/A"  # Pular opcional
                elif not response:
                    if self.language == "pt-br":
                        print("\n⚠️  Esta pergunta é obrigatória!")
                    else:
                        print("\n⚠️  This question is required!")
                    input("\nPress Enter to continue...")
                    continue

                # Enviar resposta
                result = self.engine.answer_question(self.session_id, response)

                # Verificar se completou
                if result.get("completed"):
                    self.clear_screen()
                    self.print_header()

                    if self.language == "pt-br":
                        print("🎉 ENTREVISTA CONCLUÍDA!")
                        print("\n⏳ Gerando sua persona personalizada...")
                    else:
                        print("🎉 INTERVIEW COMPLETED!")
                        print("\n⏳ Generating your custom persona...")

                    # Gerar persona
                    persona = await self.builder.build_persona_from_interview(
                        session_id=self.session_id,
                        persona_name=f"Persona_{self.product_context[:20]}",
                    )

                    # Salvar resultados
                    self.save_persona(persona)

                    print()
                    if self.language == "pt-br":
                        print("✨ Persona gerada com sucesso!")
                        print(
                            f"   Confiança: {persona['quality_metrics']['overall_confidence']:.1f}%"
                        )
                    else:
                        print("✨ Persona generated successfully!")
                        print(
                            f"   Confidence: {persona['quality_metrics']['overall_confidence']:.1f}%"
                        )

                    break

                # Próxima pergunta
                current_question = result

        except KeyboardInterrupt:
            print("\n\n")
            if self.language == "pt-br":
                print("👋 Entrevista cancelada. Até logo!")
            else:
                print("👋 Interview cancelled. Goodbye!")
            sys.exit(0)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print(
                "\nPlease report this issue at: https://github.com/yourusername/osp-marketing-tools/issues"
            )
            sys.exit(1)

    async def run(self):
        """Executa o programa principal."""
        self.clear_screen()
        self.print_header()

        # Selecionar idioma
        self.language = self.select_language()

        # Obter contexto do produto
        self.product_context = self.get_product_context()

        # Executar entrevista
        await self.run_interview()

        # Finalização
        print()
        if self.language == "pt-br":
            print("🙏 Obrigado por usar o Interactive Buyer Persona Generator!")
            print("📧 Feedback: contato@openpartners.com.br")
        else:
            print("🙏 Thank you for using the Interactive Buyer Persona Generator!")
            print("📧 Feedback: contact@openpartners.com")

        print()
        input("Press Enter to exit / Pressione Enter para sair...")


def main():
    """Função principal."""
    generator = StandalonePersonaGenerator()
    asyncio.run(generator.run())


if __name__ == "__main__":
    main()
