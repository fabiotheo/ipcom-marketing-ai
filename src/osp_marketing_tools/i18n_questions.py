"""
Internationalization (i18n) support for Interactive Buyer Persona Generator.

Provides bilingual support for English and Portuguese Brazilian.
Based on Adele Revella's 5 Rings of Buying Insight methodology.
"""

from typing import Any, Dict, List

from .persona_data_structures import RingType


class QuestionTranslations:
    """Manages bilingual questions for the interview system."""

    # Supported languages
    SUPPORTED_LANGUAGES = ["en", "pt-br"]
    DEFAULT_LANGUAGE = "en"

    # Language metadata
    LANGUAGE_INFO = {
        "en": {"name": "English", "flag": "🇺🇸", "locale": "en-US"},
        "pt-br": {"name": "Português Brasileiro", "flag": "🇧🇷", "locale": "pt-BR"},
    }

    # Interview context by language
    INTERVIEW_CONTEXT = {
        "en": "We'll explore your buying situation using Adele Revella's proven methodology. This should take about 10-15 minutes.",
        "pt-br": "Vamos explorar sua situação de compra usando a metodologia comprovada de Adele Revella. Isso deve levar cerca de 10-15 minutos.",
    }

    # Progress messages
    PROGRESS_MESSAGES = {
        "en": {
            "ring_progress": "{current}/{total} rings",
            "question_progress": "{current}/{total} questions",
            "completion": "Interview completed",
            "starting": "Starting interview",
        },
        "pt-br": {
            "ring_progress": "{current}/{total} anéis",
            "question_progress": "{current}/{total} perguntas",
            "completion": "Entrevista concluída",
            "starting": "Iniciando entrevista",
        },
    }

    # Ring names translation
    RING_NAMES = {
        "en": {
            RingType.PRIORITY_INITIATIVE: "Priority Initiative",
            RingType.SUCCESS_FACTORS: "Success Factors",
            RingType.PERCEIVED_BARRIERS: "Perceived Barriers",
            RingType.DECISION_CRITERIA: "Decision Criteria",
            RingType.BUYER_JOURNEY: "Buyer's Journey",
        },
        "pt-br": {
            RingType.PRIORITY_INITIATIVE: "Iniciativa Prioritária",
            RingType.SUCCESS_FACTORS: "Fatores de Sucesso",
            RingType.PERCEIVED_BARRIERS: "Barreiras Percebidas",
            RingType.DECISION_CRITERIA: "Critérios de Decisão",
            RingType.BUYER_JOURNEY: "Jornada do Comprador",
        },
    }

    # Questions database - bilingual
    QUESTIONS = {
        "en": {
            # Ring 1: Priority Initiative
            RingType.PRIORITY_INITIATIVE: [
                {
                    "id": "priority_trigger",
                    "question": "What specific event or situation made you realize you needed to solve this problem NOW?",
                    "context": "Understanding the trigger event is crucial - was it a crisis, opportunity, or deadline?",
                    "required": True,
                    "follow_up": "Can you describe the timeline of events that led to this decision?",
                },
                {
                    "id": "priority_pressure",
                    "question": "What pressure (internal or external) is driving the urgency to make this decision?",
                    "context": "This could be competitive pressure, regulatory requirements, customer demands, etc.",
                    "required": True,
                    "follow_up": "Who or what is the source of this pressure?",
                },
                {
                    "id": "priority_status_quo",
                    "question": "What's not working with your current solution or approach?",
                    "context": "Understanding current pain points helps identify what triggered the search.",
                    "required": False,
                    "follow_up": "How long have you been dealing with this problem?",
                },
            ],
            # Ring 2: Success Factors
            RingType.SUCCESS_FACTORS: [
                {
                    "id": "success_business",
                    "question": "What specific business results do you expect to achieve with this solution?",
                    "context": "Look for measurable outcomes like revenue, cost savings, efficiency gains.",
                    "required": True,
                    "follow_up": "How will you measure success?",
                },
                {
                    "id": "success_personal",
                    "question": "How will solving this problem impact you personally or professionally?",
                    "context": "Personal stakes often drive decision-making as much as business factors.",
                    "required": True,
                    "follow_up": "What would failure mean for your career?",
                },
                {
                    "id": "success_timeline",
                    "question": "When do you need to see results, and what would those early wins look like?",
                    "context": "Timeline expectations affect vendor selection and implementation approach.",
                    "required": False,
                    "follow_up": "What milestones will you track along the way?",
                },
            ],
            # Ring 3: Perceived Barriers
            RingType.PERCEIVED_BARRIERS: [
                {
                    "id": "barriers_risks",
                    "question": "What risks or concerns do you have about implementing a new solution?",
                    "context": "Understanding fears helps address objections proactively.",
                    "required": True,
                    "follow_up": "Which of these concerns keeps you up at night?",
                },
                {
                    "id": "barriers_internal",
                    "question": "What internal resistance or challenges do you anticipate?",
                    "context": "Internal politics and change management are often overlooked barriers.",
                    "required": False,
                    "follow_up": "Who might oppose this initiative and why?",
                },
            ],
            # Ring 4: Decision Criteria
            RingType.DECISION_CRITERIA: [
                {
                    "id": "criteria_must_have",
                    "question": "What are your absolute must-have features or capabilities?",
                    "context": "These are non-negotiable requirements that eliminate vendors.",
                    "required": True,
                    "follow_up": "Which of these is most critical to your success?",
                },
                {
                    "id": "criteria_evaluation",
                    "question": "How will you evaluate and compare different vendors or solutions?",
                    "context": "Understanding the evaluation process helps position appropriately.",
                    "required": True,
                    "follow_up": "Who else will be involved in this evaluation?",
                },
                {
                    "id": "criteria_vendor",
                    "question": "What vendor characteristics are important to you beyond the product itself?",
                    "context": "Company size, support quality, financial stability, etc. can be deciding factors.",
                    "required": False,
                    "follow_up": "Have you had bad experiences with vendors in the past?",
                },
            ],
            # Ring 5: Buyer's Journey
            RingType.BUYER_JOURNEY: [
                {
                    "id": "journey_research",
                    "question": "Where do you typically go to research solutions like this?",
                    "context": "Information sources reveal content preferences and trusted channels.",
                    "required": True,
                    "follow_up": "Which sources do you trust most and why?",
                },
                {
                    "id": "journey_team",
                    "question": "Who else will be involved in making this decision?",
                    "context": "Understanding the decision-making unit is crucial for B2B sales.",
                    "required": True,
                    "follow_up": "What role does each person play in the decision?",
                },
                {
                    "id": "journey_process",
                    "question": "Can you walk me through your typical process for making purchases like this?",
                    "context": "Process understanding helps with timing and approach strategies.",
                    "required": False,
                    "follow_up": "How long do decisions like this typically take?",
                },
            ],
        },
        "pt-br": {
            # Anel 1: Iniciativa Prioritária
            RingType.PRIORITY_INITIATIVE: [
                {
                    "id": "priority_trigger",
                    "question": "Que evento específico ou situação fez você perceber que precisava resolver este problema AGORA?",
                    "context": "Entender o evento gatilho é crucial - foi uma crise, oportunidade ou prazo?",
                    "required": True,
                    "follow_up": "Você pode descrever a cronologia de eventos que levaram a esta decisão?",
                },
                {
                    "id": "priority_pressure",
                    "question": "Que pressão (interna ou externa) está impulsionando a urgência para tomar esta decisão?",
                    "context": "Isso pode ser pressão competitiva, requisitos regulamentares, demandas de clientes, etc.",
                    "required": True,
                    "follow_up": "Quem ou o que é a fonte desta pressão?",
                },
                {
                    "id": "priority_status_quo",
                    "question": "O que não está funcionando com sua solução ou abordagem atual?",
                    "context": "Entender as dores atuais ajuda a identificar o que desencadeou a busca.",
                    "required": False,
                    "follow_up": "Há quanto tempo você vem lidando com este problema?",
                },
            ],
            # Anel 2: Fatores de Sucesso
            RingType.SUCCESS_FACTORS: [
                {
                    "id": "success_business",
                    "question": "Que resultados específicos de negócio você espera alcançar com esta solução?",
                    "context": "Procure por resultados mensuráveis como receita, economia de custos, ganhos de eficiência.",
                    "required": True,
                    "follow_up": "Como você vai medir o sucesso?",
                },
                {
                    "id": "success_personal",
                    "question": "Como resolver este problema vai impactar você pessoal ou profissionalmente?",
                    "context": "Interesses pessoais frequentemente dirigem tomada de decisão tanto quanto fatores de negócio.",
                    "required": True,
                    "follow_up": "O que o fracasso significaria para sua carreira?",
                },
                {
                    "id": "success_timeline",
                    "question": "Quando você precisa ver resultados, e como seriam essas primeiras vitórias?",
                    "context": "Expectativas de cronograma afetam seleção de fornecedor e abordagem de implementação.",
                    "required": False,
                    "follow_up": "Que marcos você vai acompanhar pelo caminho?",
                },
            ],
            # Anel 3: Barreiras Percebidas
            RingType.PERCEIVED_BARRIERS: [
                {
                    "id": "barriers_risks",
                    "question": "Que riscos ou preocupações você tem sobre implementar uma nova solução?",
                    "context": "Entender medos ajuda a abordar objeções proativamente.",
                    "required": True,
                    "follow_up": "Qual dessas preocupações mais te tira o sono?",
                },
                {
                    "id": "barriers_internal",
                    "question": "Que resistência interna ou desafios você antecipa?",
                    "context": "Política interna e gestão de mudança são barreiras frequentemente negligenciadas.",
                    "required": False,
                    "follow_up": "Quem pode se opor a esta iniciativa e por quê?",
                },
            ],
            # Anel 4: Critérios de Decisão
            RingType.DECISION_CRITERIA: [
                {
                    "id": "criteria_must_have",
                    "question": "Quais são suas funcionalidades ou capacidades absolutamente obrigatórias?",
                    "context": "Estes são requisitos não-negociáveis que eliminam fornecedores.",
                    "required": True,
                    "follow_up": "Qual destes é mais crítico para seu sucesso?",
                },
                {
                    "id": "criteria_evaluation",
                    "question": "Como você vai avaliar e comparar diferentes fornecedores ou soluções?",
                    "context": "Entender o processo de avaliação ajuda no posicionamento apropriado.",
                    "required": True,
                    "follow_up": "Quem mais estará envolvido nesta avaliação?",
                },
                {
                    "id": "criteria_vendor",
                    "question": "Que características do fornecedor são importantes para você além do produto em si?",
                    "context": "Tamanho da empresa, qualidade do suporte, estabilidade financeira, etc. podem ser fatores decisivos.",
                    "required": False,
                    "follow_up": "Você teve experiências ruins com fornecedores no passado?",
                },
            ],
            # Anel 5: Jornada do Comprador
            RingType.BUYER_JOURNEY: [
                {
                    "id": "journey_research",
                    "question": "Onde você tipicamente vai para pesquisar soluções como esta?",
                    "context": "Fontes de informação revelam preferências de conteúdo e canais confiáveis.",
                    "required": True,
                    "follow_up": "Quais fontes você mais confia e por quê?",
                },
                {
                    "id": "journey_team",
                    "question": "Quem mais estará envolvido em tomar esta decisão?",
                    "context": "Entender a unidade de tomada de decisão é crucial para vendas B2B.",
                    "required": True,
                    "follow_up": "Que papel cada pessoa desempenha na decisão?",
                },
                {
                    "id": "journey_process",
                    "question": "Você pode me explicar seu processo típico para fazer compras como esta?",
                    "context": "Entender o processo ajuda com estratégias de timing e abordagem.",
                    "required": False,
                    "follow_up": "Quanto tempo decisões como esta tipicamente levam?",
                },
            ],
        },
    }

    @classmethod
    def get_questions_for_ring(
        cls, ring_type: RingType, language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Get all questions for a specific ring in the specified language."""
        language = language.lower()
        if language not in cls.SUPPORTED_LANGUAGES:
            language = cls.DEFAULT_LANGUAGE

        return cls.QUESTIONS.get(language, {}).get(ring_type, [])

    @classmethod
    def get_question_by_id(
        cls, question_id: str, language: str = "en"
    ) -> Dict[str, Any]:
        """Get a specific question by ID in the specified language."""
        language = language.lower()
        if language not in cls.SUPPORTED_LANGUAGES:
            language = cls.DEFAULT_LANGUAGE

        for ring_questions in cls.QUESTIONS.get(language, {}).values():
            for question in ring_questions:
                if question["id"] == question_id:
                    return question
        return {}

    @classmethod
    def get_ring_name(cls, ring_type: RingType, language: str = "en") -> str:
        """Get localized ring name."""
        language = language.lower()
        if language not in cls.SUPPORTED_LANGUAGES:
            language = cls.DEFAULT_LANGUAGE

        return cls.RING_NAMES.get(language, {}).get(ring_type, str(ring_type.value))

    @classmethod
    def get_interview_context(cls, language: str = "en") -> str:
        """Get localized interview context message."""
        language = language.lower()
        if language not in cls.SUPPORTED_LANGUAGES:
            language = cls.DEFAULT_LANGUAGE

        return cls.INTERVIEW_CONTEXT.get(
            language, cls.INTERVIEW_CONTEXT[cls.DEFAULT_LANGUAGE]
        )

    @classmethod
    def get_progress_message(cls, key: str, language: str = "en", **kwargs) -> str:
        """Get localized progress message."""
        language = language.lower()
        if language not in cls.SUPPORTED_LANGUAGES:
            language = cls.DEFAULT_LANGUAGE

        template = cls.PROGRESS_MESSAGES.get(language, {}).get(key, "")
        return template.format(**kwargs) if kwargs else template

    @classmethod
    def is_supported_language(cls, language: str) -> bool:
        """Check if language is supported."""
        return language.lower() in cls.SUPPORTED_LANGUAGES

    @classmethod
    def get_language_info(cls, language: str = None) -> Dict[str, Any]:
        """Get language information."""
        if language:
            return cls.LANGUAGE_INFO.get(language.lower(), {})
        return cls.LANGUAGE_INFO
