import re
import logging
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class CheckResult(BaseModel):
    name: str
    passed: bool
    weight: float
    score: float
    details: str
    severity: Severity


class ValidationResult(BaseModel):
    score: float
    passed: bool
    checks: Dict[str, CheckResult]
    feedback: str
    suggested_fixes: List[str]
    iteration_needed: bool


AMBIGUOUS_TERMS = [
    (r"\bcurto\b", "especificar palavras", 15),
    (r"\blongo\b", "especificar palavras", 15),
    (r"\bt[eé]cnico\b", "especificar nivel", 15),
    (r"\brecente\b", "especificar periodo", 15),
    (r"\bmelhor\b", "especificar criterio", 15),
    (r"\bbom\b", "especificar metrica", 15),
    (r"\badequado\b", "especificar parametros", 15),
    (r"\bprofissional\b", "especificar tom", 15),
]

REQUIRED_SECTIONS = [
    "## CONTEXTO",
    "## TAREFA",
    "## FORMATO DE SAIDA",
    "## RESTRICOES",
]

BONUS_SECTIONS = [
    ("## EXEMPLOS", "## FEW-SHOT"),
    ("## AUTO-VALIDACAO", "## SELF-CHECK"),
]


class ValidatorEngine:
    def __init__(self, llm_service):
        self.llm = llm_service

    def _check_structure(self, prompt: str) -> CheckResult:
        found_required = 0
        missing = []
        for section in REQUIRED_SECTIONS:
            alt = section.replace("## FORMATO DE SAIDA", "## FORMATO DE SAÍDA")
            alt2 = alt.replace("## RESTRICOES", "## RESTRIÇÕES")
            alt3 = alt2.replace("## AUTO-VALIDACAO", "## AUTO-VALIDAÇÃO")
            if section in prompt or alt in prompt or alt2 in prompt or alt3 in prompt:
                found_required += 1
            else:
                missing.append(section)

        missing_count = len(missing)

        if missing_count >= 2:
            score = 0.0
            severity = Severity.CRITICAL
        elif missing_count == 1:
            score = 50.0
            severity = Severity.CRITICAL
        else:
            score = 100.0
            severity = Severity.INFO

        for a, b in BONUS_SECTIONS:
            if a in prompt or b in prompt:
                score = min(100.0, score + 5)
                if severity == Severity.CRITICAL and missing_count == 0:
                    severity = Severity.WARNING

        if missing_count == 0:
            passed = True
        else:
            passed = False

        details = f"Seções obrigatórias encontradas: {found_required}/4"
        if missing:
            details += f". Faltando: {', '.join(missing)}"

        return CheckResult(
            name="estrutura",
            passed=passed,
            weight=20.0,
            score=score,
            details=details,
            severity=severity,
        )

    def _check_ambiguity(self, prompt: str) -> CheckResult:
        score = 100.0
        corrections = []

        for pattern, suggestion, penalty in AMBIGUOUS_TERMS:
            if re.search(pattern, prompt, re.IGNORECASE):
                matches = len(re.findall(pattern, prompt, re.IGNORECASE))
                total_penalty = min(penalty * matches, score)
                score -= total_penalty
                corrections.append(f"'{pattern}': {suggestion}")

        score = max(0.0, min(100.0, score))
        passed = score >= 70

        details = f"Score de ambiguidade: {score:.1f}"
        if corrections:
            details += f". Termos problematicos: {'; '.join(corrections)}"

        return CheckResult(
            name="ambiguidade",
            passed=passed,
            weight=20.0,
            score=score,
            details=details,
            severity=Severity.WARNING if not passed else Severity.INFO,
        )

    async def _check_semantic(self, prompt: str, original_goal: str) -> CheckResult:
        validation_prompt = (
            "## CONTEXTO\n"
            "Voce e um validador de prompts especialista. "
            "Avalie o prompt abaixo em 5 criterios, retornando APENAS JSON.\n"
            "## TAREFA\n"
            f"Avalie o prompt em relacao ao objetivo: {original_goal}\n"
            "## PROMPT PARA AVALIAR\n"
            f"{prompt}\n"
            "## FORMATO DE SAIDA\n"
            "```json\n"
            '{"coerencia": 0-100, "completude": 0-100, '
            '"acionabilidade": 0-100, "precisao": 0-100, '
            '"eficiencia": 0-100, '
            '"justificativa": "texto", '
            '"sugestoes": ["sugestao1", "sugestao2"]}\n'
            "```\n"
            "## RESTRICOES\n"
            "Responda APENAS com JSON valido. Nao inclua outros textos."
        )

        try:
            result = await self.llm.generate_json(validation_prompt)
        except Exception as e:
            logger.warning(f"Falha na validacao semantica: {e}")
            return CheckResult(
                name="semantica",
                passed=False,
                weight=25.0,
                score=50.0,
                details=f"Validacao semantica indisponivel: {e}",
                severity=Severity.WARNING,
            )

        coerencia = float(result.get("coerencia", 0))
        completude = float(result.get("completude", 0))
        acionabilidade = float(result.get("acionabilidade", 0))
        precisao = float(result.get("precisao", 0))
        eficiencia = float(result.get("eficiencia", 0))

        score = (
            coerencia * 0.25
            + completude * 0.25
            + acionabilidade * 0.20
            + precisao * 0.20
            + eficiencia * 0.10
        )
        score = max(0.0, min(100.0, score))
        passed = score >= 70

        justificativa = result.get("justificativa", "")

        return CheckResult(
            name="semantica",
            passed=passed,
            weight=25.0,
            score=score,
            details=(
                f"Coerencia:{coerencia:.0f} Completude:{completude:.0f} "
                f"Acionabilidade:{acionabilidade:.0f} Precisao:{precisao:.0f} "
                f"Eficiencia:{eficiencia:.0f} | {justificativa}"
            ),
            severity=Severity.WARNING if not passed else Severity.INFO,
        )

    def _check_constraints(self, prompt: str) -> CheckResult:
        constraints = set()

        neg_patterns = [
            r"NÃO\s+\w+", r"NAO\s+\w+",
            r"NUNCA\s+\w+",
            r"EVITE\s+\w+", r"E VIT E\s+\w+",
        ]
        for pat in neg_patterns:
            for m in re.finditer(pat, prompt, re.IGNORECASE):
                constraints.add(m.group().upper())

        boundary_patterns = [
            r"m[áa]ximo\s+\d+",
            r"m[ií]nimo\s+\d+",
            r"entre\s+\d+\s+e\s+\d+",
            r"exatamente\s+\d+",
            r"at[eé]\s+\d+",
        ]
        for pat in boundary_patterns:
            for m in re.finditer(pat, prompt, re.IGNORECASE):
                constraints.add(m.group().upper())

        neg_words = ["ignore", "desconsidere", "exclua", "evite", "nao", "nunca"]
        for word in neg_words:
            if re.search(rf"\b{word}\w*\b", prompt, re.IGNORECASE):
                constraints.add(word.upper())

        score = min(100.0, len(constraints) * 12)
        passed = score >= 60

        return CheckResult(
            name="restricoes",
            passed=passed,
            weight=15.0,
            score=score,
            details=f"Instrucoes negativas/limites encontrados: {len(constraints)}. Score: {score:.0f}/100",
            severity=Severity.WARNING if not passed else Severity.INFO,
        )

    async def _check_smart(self, prompt: str, original_goal: str) -> CheckResult:
        validation_prompt = (
            "## CONTEXTO\n"
            "Voce e um validador de prompts especialista. "
            "Avalie o quao SMART o prompt abaixo atende ao objetivo.\n"
            "## TAREFA\n"
            f"Avalie o prompt em relacao ao objetivo: {original_goal}\n"
            "## PROMPT PARA AVALIAR\n"
            f"{prompt}\n"
            "## FORMATO DE SAIDA\n"
            "```json\n"
            '{"specific": 0-100, "measurable": 0-100, '
            '"achievable": 0-100, "relevant": 0-100, '
            '"time_bound": 0-100, '
            '"justificativa": "texto"}\n'
            "```\n"
            "## RESTRICOES\n"
            "Responda APENAS com JSON valido. Nao inclua outros textos."
        )

        try:
            result = await self.llm.generate_json(validation_prompt)
        except Exception as e:
            logger.warning(f"Falha na validacao SMART: {e}")
            return CheckResult(
                name="smart",
                passed=False,
                weight=20.0,
                score=50.0,
                details=f"Validacao SMART indisponivel: {e}",
                severity=Severity.WARNING,
            )

        specific = float(result.get("specific", 0))
        measurable = float(result.get("measurable", 0))
        achievable = float(result.get("achievable", 0))
        relevant = float(result.get("relevant", 0))
        time_bound = float(result.get("time_bound", 0))

        score = (specific + measurable + achievable + relevant + time_bound) / 5
        score = max(0.0, min(100.0, score))
        passed = score >= 70

        return CheckResult(
            name="smart",
            passed=passed,
            weight=20.0,
            score=score,
            details=(
                f"Specific:{specific:.0f} Measurable:{measurable:.0f} "
                f"Achievable:{achievable:.0f} Relevant:{relevant:.0f} "
                f"Time-bound:{time_bound:.0f} | {result.get('justificativa', '')}"
            ),
            severity=Severity.WARNING if not passed else Severity.INFO,
        )

    async def validate(self, prompt: str, original_goal: str) -> ValidationResult:
        checks = {}

        check1 = self._check_structure(prompt)
        checks[check1.name] = check1

        check2 = self._check_ambiguity(prompt)
        checks[check2.name] = check2

        check4 = self._check_constraints(prompt)
        checks[check4.name] = check4

        import asyncio
        sem_check, smart_check = await asyncio.gather(
            self._check_semantic(prompt, original_goal),
            self._check_smart(prompt, original_goal),
        )
        checks[sem_check.name] = sem_check
        checks[smart_check.name] = smart_check

        total_weight = sum(c.weight for c in checks.values())
        score = sum(c.score * (c.weight / total_weight) for c in checks.values())
        score = round(max(0.0, min(100.0, score)), 2)

        has_critical_failure = any(
            c.severity == Severity.CRITICAL and not c.passed
            for c in checks.values()
        )
        passed = score >= 80 and not has_critical_failure

        feedback_lines = [
            f"{c.name}: {c.score:.0f}/100 ({'passou' if c.passed else 'falhou'})"
            for c in checks.values()
        ]
        feedback = " | ".join(feedback_lines)

        suggested_fixes = []
        if not checks["estrutura"].passed:
            suggested_fixes.append(
                "Adicione as secoes obrigatorias: ## CONTEXTO, ## TAREFA, "
                "## FORMATO DE SAIDA, ## RESTRICOES"
            )
        if not checks["ambiguidade"].passed:
            suggested_fixes.append(
                "Substitua termos vagos por metricas concretas"
            )
        if not checks["semantica"].passed:
            sugg = checks["semantica"].details.split("|")[-1].strip()
            if sugg and "indisponivel" not in sugg:
                suggested_fixes.append(f"Melhorias semanticas sugeridas: {sugg}")
            else:
                suggested_fixes.append("Melhore a coerencia e completude do prompt")
        if not checks["restricoes"].passed:
            suggested_fixes.append(
                "Adicione instrucoes negativas e limites numericos explicitos"
            )
        if not checks["smart"].passed:
            suggested_fixes.append(
                "Torne o objetivo mais especifico e mensuravel"
            )

        return ValidationResult(
            score=score,
            passed=passed,
            checks=checks,
            feedback=feedback,
            suggested_fixes=suggested_fixes,
            iteration_needed=not passed,
        )
