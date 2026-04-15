"""
Axioma-Omega Protocol — Domain Reasoner
Capa de Lógica: Motor de razonamiento deductivo con Veto Axiomático.
Implementa:
  - RAG de Axiomas (Retrieval-Axiom Generation)
  - Veto Axiomático (v3 — Inmunidad a Manipulación)
  - Validación de Salida (v3 — Blindaje Anti-Alucinación)
  - MoE Jerárquico: Expertos Axiomáticos > Situacionales > Interfaz
UI es CIEGA a este módulo; solo recibe AxiomicResponse.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.axiom_registry import Axiom, AxiomLayer, AxiomRegistry, AxiomStatus


# ---------------------------------------------------------------------------
# Respuesta Certificada (Certificación de Origen — v3)
# ---------------------------------------------------------------------------

class ValidationVerdict(Enum):
    APPROVED = auto()    # Respuesta válida, compatible con axiomas
    VETOED   = auto()    # Respuesta bloqueada por contradicción axiomática
    FLAGGED  = auto()    # Respuesta permitida pero con advertencia de baja confianza


@dataclass(frozen=True)
class AxiomicResponse:
    """
    Cada respuesta del sistema queda ligada a los axiomas que la sustentan.
    El usuario puede auditar la base lógica de cualquier output.
    """
    content:           str
    verdict:           ValidationVerdict
    supporting_axioms: Tuple[str, ...]   # IDs de axiomas que fundamentan la respuesta
    confidence_score:  float             # Score compuesto de confianza
    domain:            str
    processing_time_ms: float
    veto_reason:       Optional[str] = None   # Solo si verdict == VETOED


# ---------------------------------------------------------------------------
# Tipos de Expertos (MoE Jerárquico)
# ---------------------------------------------------------------------------

class ExpertType(Enum):
    AXIOMATIC    = "axiomatic"     # Guardián de leyes físicas — poder de VETO
    SITUATIONAL  = "situational"   # Maneja dominios específicos
    INTERFACE    = "interface"     # Genera lenguaje natural (probabilístico)


@dataclass
class ExpertVote:
    expert_type:  ExpertType
    proposed_text: str
    axiom_ids_used: List[str]
    confidence:   float
    flags:        List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Motor Principal de Razonamiento
# ---------------------------------------------------------------------------

class DomainReasoner:
    """
    Implementa el Paradigma Axioma-Omega completo:
    1. Carga el Paquete de Axiomas del Dominio Actual (RAG de Axiomas).
    2. Poda lógica: elimina ramas físicamente imposibles antes de inferir.
    3. Aplica el Veto Axiomático sobre cualquier propuesta de experto.
    4. Certifica la respuesta final con Certificación de Origen.
    """

    def __init__(
        self,
        registry: AxiomRegistry,
        llm_inference_fn: Callable[[str, List[Axiom]], str],
    ) -> None:
        """
        Args:
            registry: Registro de axiomas inmutable.
            llm_inference_fn: Wrapper al LLM/backend de inferencia.
                              Recibe (prompt, axioms_context) → str.
                              Nunca se llama directamente: pasa por los Expertos.
        """
        self._registry = registry
        self._llm = llm_inference_fn

    # ------------------------------------------------------------------
    # API Pública
    # ------------------------------------------------------------------

    def reason(
        self,
        query: str,
        domain: str,
        env_vars: Optional[Dict[str, float]] = None,
    ) -> AxiomicResponse:
        """
        Pipeline completo de razonamiento axiomático.
        Implementa el Early-Return Pattern: falla rápido si hay veto.
        """
        start_time = time.perf_counter()
        env_vars = env_vars or {}

        # Paso 1: RAG de Axiomas — cargar solo los axiomas del dominio activo
        active_axioms = self._registry.get_active_for_context(domain, env_vars)
        atomic_axioms = self._registry.query_by_layer(AxiomLayer.ATOMIC)
        context_axioms = atomic_axioms + active_axioms

        # Paso 2: Experto Axiomático — primera pasada de validación del query
        query_veto = self._axiomatic_expert_check_query(query, context_axioms)
        if query_veto is not None:
            elapsed = (time.perf_counter() - start_time) * 1000
            return AxiomicResponse(
                content="[BLOQUEADO] La solicitud contradice axiomas verificados.",
                verdict=ValidationVerdict.VETOED,
                supporting_axioms=tuple(a.axiom_id for a in context_axioms),
                confidence_score=0.0,
                domain=domain,
                processing_time_ms=elapsed,
                veto_reason=query_veto,
            )

        # Paso 3: Inferencia LLM guiada por contexto axiomático
        raw_response = self._llm(query, context_axioms)

        # Paso 4: Validación de Salida — "estresar" la respuesta contra las leyes de dominio
        verdict, veto_reason = self._validate_output(raw_response, context_axioms)

        if verdict == ValidationVerdict.VETOED:
            elapsed = (time.perf_counter() - start_time) * 1000
            return AxiomicResponse(
                content="[BLOQUEADO] La respuesta generada contradice axiomas verificados.",
                verdict=ValidationVerdict.VETOED,
                supporting_axioms=tuple(a.axiom_id for a in context_axioms),
                confidence_score=0.0,
                domain=domain,
                processing_time_ms=elapsed,
                veto_reason=veto_reason,
            )

        # Paso 5: Calcular score de confianza compuesto
        confidence = self._compute_confidence(context_axioms)

        elapsed = (time.perf_counter() - start_time) * 1000
        return AxiomicResponse(
            content=raw_response,
            verdict=verdict,
            supporting_axioms=tuple(a.axiom_id for a in context_axioms),
            confidence_score=confidence,
            domain=domain,
            processing_time_ms=elapsed,
            veto_reason=veto_reason,
        )

    def build_axiom_context_prompt(
        self,
        query: str,
        axioms: List[Axiom],
    ) -> str:
        """
        Construye el prompt enriquecido con el contexto axiomático.
        Inyecta el sesgo inductivo dirigido al LLM (Hard Constraints).
        """
        axiom_block = "\n".join(
            f"[AXIOMA-{a.layer.name}|{a.axiom_id}] {a.statement} "
            f"| REGLA: {a.formal_rule} | CONFIANZA: {a.confidence:.3f}"
            for a in sorted(axioms, key=lambda x: x.layer)
        )
        return (
            f"=== NÚCLEO AXIOMÁTICO (RESTRICCIONES INAMOVIBLES) ===\n"
            f"{axiom_block}\n"
            f"=== CONSULTA ===\n"
            f"{query}\n"
            f"IMPORTANTE: Tu respuesta NUNCA puede contradecir los axiomas anteriores. "
            f"Si no puedes responder sin violarlos, indica la razón.\n"
        )

    # ------------------------------------------------------------------
    # Lógica Privada — Expertos MoE
    # ------------------------------------------------------------------

    def _axiomatic_expert_check_query(
        self,
        query: str,
        axioms: List[Axiom],
    ) -> Optional[str]:
        """
        Experto Axiomático: verifica si el QUERY en sí contradice algún axioma.
        Retorna None si todo está OK, o el motivo del veto.
        Implementa el 'Veto Axiomático' de la v3.
        """
        query_lower = query.lower()

        # Lista de patrones de contradicción conocidos (extensible via axiomas con tags)
        contradiction_patterns: List[Tuple[str, str]] = []
        for axiom in axioms:
            for tag in axiom.tags:
                if tag.startswith("veto:"):
                    pattern = tag.replace("veto:", "").replace("_", " ")
                    contradiction_patterns.append((pattern, axiom.axiom_id))

        for pattern, axiom_id in contradiction_patterns:
            if pattern in query_lower:
                return (
                    f"Solicitud contradice el Axioma '{axiom_id}': "
                    f"el patrón '{pattern}' viola una ley de Capa 0."
                )

        return None

    def _validate_output(
        self,
        response: str,
        axioms: List[Axiom],
    ) -> Tuple[ValidationVerdict, Optional[str]]:
        """
        Validación de Salida: 'estresar' la respuesta contra las leyes de dominio.
        Los axiomas de Capa 0 tienen poder de veto absoluto.
        Los de Capa 1 producen FLAGGED si se detecta baja alineación.
        """
        response_lower = response.lower()

        # Verificar contra axiomas de Capa 0 (veto absoluto)
        for axiom in axioms:
            if axiom.layer != AxiomLayer.ATOMIC:
                continue
            for tag in axiom.tags:
                if tag.startswith("veto:"):
                    pattern = tag.replace("veto:", "").replace("_", " ")
                    if pattern in response_lower:
                        return (
                            ValidationVerdict.VETOED,
                            f"Respuesta viola Axioma Atómico '{axiom.axiom_id}': '{pattern}'",
                        )

        # Verificar alineación con axiomas de Capa 1
        layer1_axioms = [a for a in axioms if a.layer == AxiomLayer.DOMAIN]
        alignment_score = self._compute_alignment_score(response, layer1_axioms)
        if alignment_score < 0.3 and layer1_axioms:
            return (
                ValidationVerdict.FLAGGED,
                f"Baja alineación con axiomas de dominio (score={alignment_score:.2f}).",
            )

        return ValidationVerdict.APPROVED, None

    def _compute_alignment_score(
        self,
        response: str,
        axioms: List[Axiom],
    ) -> float:
        """
        Score heurístico de alineación respuesta-axioma.
        En producción, reemplazar con embedding-cosine-similarity.
        """
        if not axioms:
            return 1.0
        matched = sum(
            1 for a in axioms
            if any(kw in response.lower() for kw in a.tags if not kw.startswith("veto:"))
        )
        return matched / len(axioms)

    def _compute_confidence(self, axioms: List[Axiom]) -> float:
        """
        Score de confianza compuesto del contexto axiomático activo.
        Confianza mínima del conjunto determina el piso de certeza.
        """
        if not axioms:
            return 0.0
        return min(a.confidence for a in axioms)
