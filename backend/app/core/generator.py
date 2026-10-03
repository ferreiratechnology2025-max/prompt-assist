import json
import logging
from typing import Dict, Optional

from app.core.memory import AdaptiveMemory
from app.core.validator import ValidatorEngine, ValidationResult
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class PromptGenerationRequest:
    def __init__(
        self,
        template_name: str,
        template: Dict,
        field_values: Dict,
        user_goal: str,
    ):
        self.template_name = template_name
        self.template = template
        self.field_values = field_values
        self.user_goal = user_goal


class PromptEngine:
    def __init__(
        self,
        llm_service: LLMService,
        validator: ValidatorEngine,
        memory: Optional[AdaptiveMemory] = None,
    ):
        self.llm = llm_service
        self.validator = validator
        self.memory = memory
        self.max_iterations = 3

    def _build_structured_prompt(self, request: PromptGenerationRequest) -> str:
        prompt_parts = []

        prompt_parts.append("## CONTEXTO")
        prompt_parts.append(
            f"Voce e um {request.template['assistant_role']}"
        )
        prompt_parts.append(
            "Informacoes do usuario: "
            f"{json.dumps(request.field_values, indent=2, ensure_ascii=False)}"
        )
        prompt_parts.append("")

        prompt_parts.append("## TAREFA")
        prompt_parts.append(request.template["task_description"])
        if request.user_goal:
            prompt_parts.append(f"Objetivo especifico: {request.user_goal}")
        prompt_parts.append("")

        prompt_parts.append("## RESTRICOES")
        for constraint in request.template.get("constraints_default", []):
            prompt_parts.append(f"- {constraint}")
        prompt_parts.append("")

        prompt_parts.append("## FORMATO DE SAIDA")
        prompt_parts.append(request.template["output_format"])
        prompt_parts.append("")

        prompt_parts.append("## AUTO-VALIDACAO")
        prompt_parts.append("Antes de responder, verifique:")
        prompt_parts.append("1. A resposta atende ao objetivo?")
        prompt_parts.append("2. O formato esta correto?")
        prompt_parts.append("3. Nenhuma restricao foi violada?")

        return "\n".join(prompt_parts)

    async def _refine_prompt(
        self,
        previous_prompt: str,
        validation: ValidationResult,
        iteration: int,
    ) -> str:
        fixes_text = "\n".join(f"- {fix}" for fix in validation.suggested_fixes)

        refine_prompt = (
            "## CONTEXTO\n"
            "Voce esta refinando um prompt que nao passou na validacao.\n\n"
            f"## PROMPT ANTERIOR (Iteracao {iteration})\n"
            f"```\n{previous_prompt[:2000]}\n```\n\n"
            "## FEEDBACK DO VALIDADOR\n"
            f"Score: {validation.score}/100\n"
            f"{validation.feedback}\n\n"
            "## SUGESTOES DE CORRECAO\n"
            f"{fixes_text}\n\n"
            "## TAREFA\n"
            "Reescreva o prompt corrigindo TODOS os problemas.\n"
            "Mantenha a estrutura (## CONTEXTO, ## TAREFA, ## FORMATO, ## RESTRICOES).\n\n"
            "## RESTRICOES\n"
            "- NAO repita os mesmos erros\n"
            "- NAO invente informacoes nao fornecidas\n"
            "- Seja mais especifico e rigoroso"
        )

        refined = await self.llm.generate(
            refine_prompt, temperature=0.3, max_tokens=3000
        )
        return refined

    async def generate_and_validate(
        self, request: PromptGenerationRequest
    ) -> Dict:
        best_prompt = None
        best_score = 0
        best_validation = None
        iteration = 1

        best_known_prompt = None
        is_exploration = False

        if self.memory:
            best_known_prompt, is_exploration = self.memory.get_best_prompt(
                template_name=request.template_name,
                user_goal=request.user_goal,
                field_values=request.field_values,
            )

        if best_known_prompt and not is_exploration:
            current_prompt = best_known_prompt
            logger.info("Usando prompt da memoria (exploracao)")
        else:
            if is_exploration:
                logger.info("Modo exploracao: ignorando memoria existente")
            current_prompt = self._build_structured_prompt(request)

        for iteration in range(1, self.max_iterations + 1):
            validation = await self.validator.validate(
                prompt=current_prompt,
                original_goal=(
                    request.user_goal or request.template["task_description"]
                ),
            )

            if validation.score > best_score:
                best_score = validation.score
                best_prompt = current_prompt
                best_validation = validation

            if validation.passed:
                logger.info(
                    f"Prompt aprovado na iteracao {iteration} "
                    f"com score {validation.score}"
                )
                break

            if iteration < self.max_iterations:
                logger.info(
                    f"Refinando prompt (iteracao {iteration}, "
                    f"score {validation.score})..."
                )
                current_prompt = await self._refine_prompt(
                    current_prompt, validation, iteration
                )

        if self.memory and best_prompt and best_score:
            self.memory.update(
                template_name=request.template_name,
                user_goal=request.user_goal,
                field_values=request.field_values,
                generated_prompt=best_prompt,
                score=best_score,
            )

        return {
            "generated_prompt": best_prompt,
            "validation_score": best_score,
            "validation_result": best_validation.model_dump()
            if best_validation
            else None,
            "iterations_used": iteration,
            "passed": best_score >= 80,
            "template_used": request.template_name,
        }
