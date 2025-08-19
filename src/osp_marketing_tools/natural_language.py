"""Natural Language Interface for Interactive Buyer Persona Generator.

This module provides a natural language wrapper that allows users to interact
with the persona generator using simple commands in Portuguese or English.
"""

import re
from typing import Dict, Optional, Tuple

from .i18n_questions import QuestionTranslations
from .persona_builder import PersonaBuilder


class NaturalLanguageInterface:
    """Interface for natural language interaction with persona generator."""

    # Pattern matching for language detection
    PORTUGUESE_INDICATORS = [
        "para",
        "meu",
        "minha",
        "produto",
        "serviço",
        "empresa",
        "resolver",
        "problema",
        "solução",
        "cliente",
        "persona",
        "criar",
        "gerar",
        "fazer",
        "produzir",
    ]

    ENGLISH_INDICATORS = [
        "for",
        "my",
        "product",
        "service",
        "company",
        "solve",
        "problem",
        "solution",
        "customer",
        "client",
        "persona",
        "create",
        "generate",
        "make",
        "produce",
        "build",
    ]

    def __init__(self):
        """Initialize the natural language interface."""
        self.current_session = None
        self.detected_language = None
        self.product_context = None

    def detect_language(self, text: str) -> str:
        """Detect language from user input.

        Args:
            text: User input text

        Returns:
            Language code ('pt-br' or 'en')
        """
        text_lower = text.lower()

        # Count indicators for each language
        pt_count = sum(1 for word in self.PORTUGUESE_INDICATORS if word in text_lower)
        en_count = sum(1 for word in self.ENGLISH_INDICATORS if word in text_lower)

        # Default to Portuguese if more Portuguese indicators
        if pt_count > en_count:
            return "pt-br"
        elif en_count > pt_count:
            return "en"
        else:
            # Default to English if unclear
            return "en"

    def extract_product_context(self, text: str) -> str:
        """Extract product/service context from natural language input.

        Args:
            text: User input text

        Returns:
            Extracted product context
        """
        # Portuguese patterns
        pt_patterns = [
            r"(?:meu produto é|minha empresa faz|nós oferecemos|eu ofereço|trabalhamos com)\s+([^.]+)",
            r"(?:produto|serviço|empresa|negócio)(?:\s+é)?\s*:?\s*([^.,]+)",
            r"(?:resolvemos?|soluciona(?:mos)?|ajuda(?:mos)?)\s+(?:o problema de\s+)?([^.]+)",
            r"(?:para|voltado para|focado em)\s+([^.]+)",
        ]

        # English patterns
        en_patterns = [
            r"(?:my product is|my company does|we offer|I offer|we work with)\s+([^.]+)",
            r"(?:product|service|company|business)(?:\s+is)?\s*:?\s*([^.,]+)",
            r"(?:we solve|solves?|helps?|addresses?)\s+(?:the problem of\s+)?([^.]+)",
            r"(?:for|focused on|targeting)\s+([^.]+)",
        ]

        # Try to extract context using patterns
        all_patterns = pt_patterns + en_patterns

        for pattern in all_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                context = match.group(1).strip()
                # Clean up the context
                context = re.sub(r"\s+", " ", context)  # Remove extra spaces
                context = context.rstrip(".,;:")  # Remove trailing punctuation

                # Expand context if it's too short
                if len(context) < 20:
                    # Try to find more context around the match
                    sentences = text.split(".")
                    for sentence in sentences:
                        if context.lower() in sentence.lower():
                            return sentence.strip()

                return context

        # Fallback: use the entire input as context
        return text.strip()

    def parse_command(self, command: str) -> Dict:
        """Parse natural language command to extract intent and parameters.

        Args:
            command: Natural language command from user

        Returns:
            Dict with parsed intent and parameters
        """
        # Detect language
        language = self.detect_language(command)

        # Extract product context
        product_context = self.extract_product_context(command)

        # Check for specific intents
        command_lower = command.lower()

        # Check if user wants to create a persona
        create_keywords = [
            "criar",
            "gerar",
            "produzir",
            "fazer",
            "desenvolver",  # PT
            "create",
            "generate",
            "produce",
            "make",
            "build",
            "develop",  # EN
        ]

        wants_persona = any(keyword in command_lower for keyword in create_keywords)

        # Check if user mentions persona explicitly
        mentions_persona = any(
            word in command_lower
            for word in ["persona", "buyer persona", "cliente ideal", "perfil"]
        )

        return {
            "intent": (
                "create_persona" if wants_persona or mentions_persona else "unknown"
            ),
            "language": language,
            "product_context": product_context,
            "original_command": command,
        }


async def use_ipcom_marketing_ai(command: str) -> Dict:
    """Natural language interface for IPCOM Marketing AI.

    This function allows users to interact with the persona generator using
    natural language commands in Portuguese or English.

    Examples:
        - "use ipcom-marketing-ai para criar uma persona para meu produto X"
        - "create a buyer persona for my SaaS product that helps with Y"
        - "gerar persona para minha empresa de consultoria"

    Args:
        command: Natural language command from the user

    Returns:
        Dict with the result of the command execution
    """
    try:
        # Validate input
        if not command or not command.strip():
            return {
                "success": False,
                "error": "Command cannot be empty",
                "suggestion": "Please provide a description of what you want",
            }

        interface = NaturalLanguageInterface()

        # Parse the command
        parsed = interface.parse_command(command)

        if parsed["intent"] == "create_persona":
            # Initialize persona builder with detected language
            builder = PersonaBuilder(language=parsed["language"])

            # Start the interview with extracted context
            session_id, session_info = builder.interview_engine.start_interview(
                product_context=parsed["product_context"]
            )

            # Prepare response based on language
            if parsed["language"] == "pt-br":
                instructions = {
                    "next_step": "Responda a pergunta e use 'continue_persona_interview' para continuar",
                    "completion": "A entrevista gerará automaticamente uma persona completa ao final",
                    "tip": "Seja específico nas respostas para melhores resultados",
                }
                intro_message = (
                    f"🎯 Iniciando criação de persona para: {parsed['product_context']}"
                )
            else:
                instructions = {
                    "next_step": "Answer the question and use 'continue_persona_interview' to proceed",
                    "completion": "The interview will automatically generate a complete persona when finished",
                    "tip": "Be specific in your answers for better results",
                }
                intro_message = (
                    f"🎯 Starting persona creation for: {parsed['product_context']}"
                )

            return {
                "success": True,
                "message": intro_message,
                "action": "interview_started",
                "data": {
                    "session_id": session_id,
                    "first_question": session_info["question"],
                    "progress": session_info["progress"],
                    "context": session_info["context"],
                    "language": parsed["language"],
                    "product_context": parsed["product_context"],
                    "instructions": instructions,
                },
                "metadata": {
                    "detected_language": parsed["language"],
                    "extracted_context": parsed["product_context"],
                    "original_command": parsed["original_command"],
                },
            }
        else:
            # Handle unknown intent
            return {
                "success": False,
                "error": "Could not understand the command",
                "suggestion": "Try: 'create a persona for my product X' or 'criar uma persona para meu produto Y'",
                "parsed_info": parsed,
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing command: {str(e)}",
            "suggestion": "Please try rephrasing your request",
            "command": command,
        }


async def quick_persona(description: str) -> Dict:
    """Quick persona creation with automatic language detection.

    Simplified interface that automatically detects language and starts
    the persona creation process.

    Args:
        description: Product/service description in any language

    Returns:
        Dict with interview session information
    """
    try:
        # Validate input
        if not description or not description.strip():
            return {
                "success": False,
                "error": "Description cannot be empty",
                "suggestion": "Please provide a product or service description",
            }

        # Ensure description has minimum length for language detection
        if len(description.strip()) < 10:
            return {
                "success": False,
                "error": "Description too short",
                "suggestion": "Please provide a more detailed description (at least 10 characters)",
            }

        interface = NaturalLanguageInterface()

        # Detect language from description
        language = interface.detect_language(description)

        # Initialize persona builder
        builder = PersonaBuilder(language=language)

        # Start interview
        session_id, session_info = builder.interview_engine.start_interview(
            product_context=description
        )

        return {
            "success": True,
            "session_id": session_id,
            "language": language,
            "first_question": session_info["question"],
            "progress": session_info["progress"],
            "product_context": description,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error starting persona creation: {str(e)}",
            "suggestion": "Please check your description and try again",
            "description": description,
        }
