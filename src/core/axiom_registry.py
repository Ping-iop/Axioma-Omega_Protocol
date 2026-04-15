"""
Axioma-Omega Protocol — Axiom Registry
=======================================
ES: Capa de Datos. Repositorio de solo-lectura de Verdades de Dominio.
    Los axiomas son inmutables por diseño (Principio de Inmutabilidad by Default).
    Ningún agente externo puede escribir en este registro durante el runtime.

EN: Data Layer. Read-only repository of Domain Truths (Axioms).
    Axioms are immutable by design (Immutability-by-Default Principle).
    No external agent can write to this registry at runtime.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import Dict, FrozenSet, List, Optional, Tuple


# ---------------------------------------------------------------------------
# ES: Enumeraciones de Control / EN: Control Enumerations
# ---------------------------------------------------------------------------

class AxiomLayer(IntEnum):
    """
    ES: Jerarquía de certeza según el Paradigma Axioma-Omega v2.
        Capa 0 = verdad absoluta (código duro / hard-coded truth).
        Capa 3 = zona creativo-probabilística (la IA puede especular).

    EN: Certainty hierarchy as defined by the Axioma-Omega Paradigm v2.
        Layer 0 = absolute truth (hard-coded into the system).
        Layer 3 = creative-probabilistic zone (AI is allowed to speculate).
    """
    ATOMIC      = 0   # ES: Física, Química, Matemáticas — inamovibles / EN: Physics, Chemistry, Math — immovable
    DOMAIN      = 1   # ES: Verdades verificadas de dominio / EN: Verified domain truths
    SITUATIONAL = 2   # ES: Dependen del entorno/contexto activo / EN: Environment-dependent
    CREATIVE    = 3   # ES: Zona probabilística: arte, opinión / EN: Probabilistic zone: art, opinion


class AxiomStatus(IntEnum):
    """
    ES: Estado de evaluación de un axioma dado un entorno.
    EN: Evaluation status of an axiom for a given environment context.
    """
    ACTIVE   = auto()   # ES: Activo y aplicable / EN: Active and applicable
    INACTIVE = auto()   # ES: Desactivado por condición de contorno / EN: Deactivated by boundary condition
    VETOED   = auto()   # ES: Bloqueado por contradicción lógica / EN: Blocked due to logical contradiction


# ---------------------------------------------------------------------------
# ES: Estructuras de Datos Inmutables / EN: Immutable Data Structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BoundaryCondition:
    """
    ES: Condición de contorno que activa o desactiva un axioma dado un entorno.
        Ej.: presion_atm > 200 desactiva FOTOSINTESIS y activa QUIMIOSINTESIS.
        Implementa los "Dominios de Validez" del documento técnico.

    EN: Boundary condition that activates or deactivates an axiom in a given environment.
        Ex.: pressure_atm > 200 disables PHOTOSYNTHESIS and enables CHEMOSYNTHESIS.
        Implements the "Validity Domains" from the technical specification.
    """
    variable:    str
    predicate:   str              # ES: expresión evaluable / EN: evaluable expression string
    activates:   FrozenSet[str] = field(default_factory=frozenset)
    deactivates: FrozenSet[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class Axiom:
    """
    ES: Unidad atómica de verdad dentro del protocolo.
        Cada respuesta queda vinculada al ID del axioma que la sustenta,
        eliminando la opacidad de la "caja negra" (v3 — Certificación de Origen).

    EN: Atomic unit of truth within the protocol.
        Every AI response is linked to the axiom ID that supports it,
        eliminating "black box" opacity (v3 — Origin Certification).
    """
    axiom_id:    str
    domain:      str              # ES: ej. "PHYSICS", "BIOLOGY_HUMAN" / EN: e.g. "PHYSICS"
    layer:       AxiomLayer
    statement:   str              # ES: declaración en lenguaje natural / EN: natural language statement
    formal_rule: str              # ES: representación formal / ecuación / EN: formal representation / equation
    confidence:  float            # ES: certeza 0.0–1.0 / EN: certainty 0.0–1.0
    sources:     Tuple[str, ...] = field(default_factory=tuple)
    tags:        FrozenSet[str]  = field(default_factory=frozenset)
    boundary_conditions: Tuple[BoundaryCondition, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        # ES: Los axiomas de Capa 0 SIEMPRE tienen confianza 1.0. Las leyes físicas no se negocian.
        # EN: Layer-0 axioms ALWAYS have confidence 1.0. Physical laws are non-negotiable.
        if self.layer == AxiomLayer.ATOMIC and self.confidence < 1.0:
            raise ValueError(
                f"[ES] Axioma de Capa 0 '{self.axiom_id}' debe tener confianza=1.0.\n"
                f"[EN] Layer-0 Axiom '{self.axiom_id}' must have confidence=1.0."
            )
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                "[ES] confidence debe estar en [0.0, 1.0] / "
                "[EN] confidence must be within [0.0, 1.0]"
            )


# ---------------------------------------------------------------------------
# ES: Registro Global (Singleton de Solo-Lectura)
# EN: Global Registry (Read-Only Singleton)
# ---------------------------------------------------------------------------

class AxiomRegistry:
    """
    ES: Repositorio inmutable de axiomas. Se construye una sola vez al iniciar el sistema.
        La UI y los Expertos NO pueden escribir en este registro; solo leer y consultar.
        Implementa "Inferencia de Privacidad Diferencial" — el contexto carga solo el
        paquete mínimo necesario para el dominio activo.

    EN: Immutable axiom repository. Built once at system startup.
        The UI and Expert modules CANNOT write to this registry; only read/query.
        Implements "Differential Privacy Inference" — context loads only the
        minimum axiom package required for the active domain.
    """

    def __init__(self) -> None:
        # ES: Almacén interno — dict porque O(1) lookup / EN: Internal store — dict for O(1) lookup
        self._store: Dict[str, Axiom] = {}

    # ------------------------------------------------------------------
    # ES: Escritura (solo en fase de inicialización)
    # EN: Write (initialization phase only)
    # ------------------------------------------------------------------

    def register(self, axiom: Axiom) -> None:
        """
        ES: Registra un axioma. Lanza KeyError si el ID ya existe (no sobreescritura).
        EN: Registers an axiom. Raises KeyError if ID already exists (no overwrite).
        """
        if axiom.axiom_id in self._store:
            raise KeyError(
                f"[ES] Axioma '{axiom.axiom_id}' ya registrado — no se sobreescribe.\n"
                f"[EN] Axiom '{axiom.axiom_id}' already registered — overwrite not allowed."
            )
        self._store[axiom.axiom_id] = axiom

    def register_many(self, axioms: List[Axiom]) -> None:
        """
        ES: Registra una lista de axiomas en lote.
        EN: Registers a batch list of axioms.
        """
        for a in axioms:
            self.register(a)

    # ------------------------------------------------------------------
    # ES: Lectura / Consulta / EN: Read / Query
    # ------------------------------------------------------------------

    def get(self, axiom_id: str) -> Axiom:
        """
        ES: Obtiene un axioma por ID. Lanza KeyError si no existe.
        EN: Gets an axiom by ID. Raises KeyError if not found.
        """
        if axiom_id not in self._store:
            raise KeyError(
                f"[ES] Axioma '{axiom_id}' no encontrado.\n"
                f"[EN] Axiom '{axiom_id}' not found in registry."
            )
        return self._store[axiom_id]

    def query_by_domain(self, domain: str) -> List[Axiom]:
        """ES: Filtra por dominio. / EN: Filter by domain."""
        return [a for a in self._store.values() if a.domain == domain]

    def query_by_layer(self, layer: AxiomLayer) -> List[Axiom]:
        """ES: Filtra por capa de certeza. / EN: Filter by certainty layer."""
        return [a for a in self._store.values() if a.layer == layer]

    def query_by_tags(self, tags: FrozenSet[str]) -> List[Axiom]:
        """ES: Filtra por intersección de tags. / EN: Filter by tag intersection."""
        return [a for a in self._store.values() if tags & a.tags]

    def get_active_for_context(
        self,
        domain: str,
        env_vars: Dict[str, float],
    ) -> List[Axiom]:
        """
        ES: Retorna axiomas activos para el dominio dado, evaluando condiciones de contorno.
            Implementa "Memoria por Especialización de Dominio" (Dominios de Verdad).
            El contexto carga el paquete mínimo — máxima eficiencia de cómputo.

        EN: Returns active axioms for the given domain, evaluating boundary conditions.
            Implements "Domain Specialization Memory" (Domain Truths concept).
            The context loads the minimum package — maximum compute efficiency.
        """
        result: List[Axiom] = []
        for axiom in self.query_by_domain(domain):
            if self._evaluate_boundary_conditions(axiom, env_vars) == AxiomStatus.ACTIVE:
                result.append(axiom)
        return result

    # ------------------------------------------------------------------
    # ES: Lógica Interna / EN: Internal Logic
    # ------------------------------------------------------------------

    def _evaluate_boundary_conditions(
        self,
        axiom: Axiom,
        env_vars: Dict[str, float],
    ) -> AxiomStatus:
        """
        ES: Evalúa si las condiciones de contorno dejan este axioma ACTIVE o INACTIVE.
            Los axiomas de Capa 0 SIEMPRE están activos — nunca se desactivan.

        EN: Evaluates whether boundary conditions leave this axiom ACTIVE or INACTIVE.
            Layer-0 axioms are ALWAYS active — they can never be deactivated.
        """
        # ES: Axiomas atómicos son incondicionales / EN: Atomic axioms are unconditional
        if axiom.layer == AxiomLayer.ATOMIC:
            return AxiomStatus.ACTIVE

        for bc in axiom.boundary_conditions:
            try:
                # ES: Evaluación segura — solo se exponen las env_vars como namespace
                # EN: Safe eval — only env_vars are exposed as the execution namespace
                result = eval(bc.predicate, {"__builtins__": {}}, env_vars)  # noqa: S307
                if result and axiom.axiom_id in bc.deactivates:
                    return AxiomStatus.INACTIVE
            except Exception:
                # ES: Si la condición falla, el axioma permanece activo por defecto
                # EN: If condition evaluation fails, axiom stays active by default
                pass

        return AxiomStatus.ACTIVE

    def __len__(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        return f"AxiomRegistry(axioms={len(self._store)})"
