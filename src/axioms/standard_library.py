"""
Axioma-Omega Protocol — Standard Axiom Library
Base de verdades precargadas para uso inmediato.
Organizada por dominio y capa según la Jerarquía de Certeza (v2).
"""

from __future__ import annotations

from typing import List

from core.axiom_registry import Axiom, AxiomLayer, AxiomRegistry, BoundaryCondition


# ---------------------------------------------------------------------------
# Capa 0 — Axiomas Atómicos (Leyes Físicas / Matemáticas / Químicas)
# ---------------------------------------------------------------------------

AXIOMS_LAYER_0: List[Axiom] = [

    Axiom(
        axiom_id="PHY_ENERGY_CONSERVATION",
        domain="PHYSICS",
        layer=AxiomLayer.ATOMIC,
        statement="La energía no se crea ni se destruye, solo se transforma.",
        formal_rule="dE/dt = 0  (sistema aislado)",
        confidence=1.0,
        sources=("Termodinámica — Primer Principio",),
        tags=frozenset({"energy", "physics", "veto:energy_created_from_nothing"}),
    ),

    Axiom(
        axiom_id="PHY_GRAVITY_NEWTONIAN",
        domain="PHYSICS",
        layer=AxiomLayer.ATOMIC,
        statement="Dos cuerpos con masa se atraen con fuerza proporcional al producto de sus masas e inversamente proporcional al cuadrado de la distancia.",
        formal_rule="F = G * (m1 * m2) / r^2",
        confidence=1.0,
        sources=("Newton's Law of Universal Gravitation",),
        tags=frozenset({"gravity", "physics", "newtonian", "veto:objects_fall_upward"}),
        boundary_conditions=(
            BoundaryCondition(
                variable="velocity_ratio_c",
                predicate="velocity_ratio_c > 0.1",
                deactivates=frozenset({"PHY_GRAVITY_NEWTONIAN"}),
                activates=frozenset({"PHY_GRAVITY_RELATIVISTIC"}),
            ),
        ),
    ),

    Axiom(
        axiom_id="PHY_GRAVITY_RELATIVISTIC",
        domain="PHYSICS",
        layer=AxiomLayer.ATOMIC,
        statement="La gravedad es la curvatura del espacio-tiempo causada por la masa-energía.",
        formal_rule="G_μν + Λg_μν = (8πG/c^4) * T_μν",
        confidence=1.0,
        sources=("Einstein — General Theory of Relativity",),
        tags=frozenset({"gravity", "relativity", "spacetime"}),
    ),

    Axiom(
        axiom_id="CHE_WATER_PROPERTIES",
        domain="CHEMISTRY",
        layer=AxiomLayer.ATOMIC,
        statement="El agua (H₂O) es una molécula polar con tensión superficial, punto de ebullición 100°C a 1 atm y punto de fusión 0°C a 1 atm.",
        formal_rule="H2O: polar_molecule=True, T_boil_1atm=100°C, T_melt_1atm=0°C",
        confidence=1.0,
        sources=("Química General — Atkins",),
        tags=frozenset({"water", "chemistry", "matter_states", "veto:water_flows_uphill"}),
    ),

    Axiom(
        axiom_id="MATH_EUCLIDEAN_SPACE",
        domain="MATHEMATICS",
        layer=AxiomLayer.ATOMIC,
        statement="En el espacio euclidiano, la distancia entre dos puntos sigue el teorema de Pitágoras.",
        formal_rule="d(A,B) = sqrt((x2-x1)^2 + (y2-y1)^2 + (z2-z1)^2)",
        confidence=1.0,
        sources=("Euclid — Elements",),
        tags=frozenset({"geometry", "math", "euclidean"}),
    ),

    Axiom(
        axiom_id="PHY_LIGHT_SPEED",
        domain="PHYSICS",
        layer=AxiomLayer.ATOMIC,
        statement="La velocidad de la luz en el vacío es constante e igual a 299,792,458 m/s.",
        formal_rule="c = 299792458 m/s  (constante universal)",
        confidence=1.0,
        sources=("Special Theory of Relativity — Einstein",),
        tags=frozenset({"light", "speed", "relativity", "veto:faster_than_light"}),
    ),
]


# ---------------------------------------------------------------------------
# Capa 1 — Verdades de Dominio (99.9% de certeza)
# ---------------------------------------------------------------------------

AXIOMS_LAYER_1: List[Axiom] = [

    Axiom(
        axiom_id="BIO_HUMAN_BIPEDALISM",
        domain="BIOLOGY_HUMAN",
        layer=AxiomLayer.DOMAIN,
        statement="Los humanos sanos se desplazan erguidos sobre dos extremidades inferiores.",
        formal_rule="HUMAN.locomotion = BIPEDAL; limb_count_lower = 2",
        confidence=0.999,
        sources=("Human Anatomy — Gray's Anatomy",),
        tags=frozenset({"human", "biology", "locomotion", "veto:human_has_three_legs"}),
    ),

    Axiom(
        axiom_id="BIO_HUMAN_OXYGEN",
        domain="BIOLOGY_HUMAN",
        layer=AxiomLayer.DOMAIN,
        statement="Los humanos requieren oxígeno (O₂) para la respiración celular en condiciones de superficie.",
        formal_rule="HUMAN.respiration_medium = O2; pressure_range_valid = [0.2, 3.0] atm",
        confidence=0.999,
        sources=("Human Physiology — Guyton",),
        tags=frozenset({"human", "biology", "oxygen", "respiration"}),
        boundary_conditions=(
            BoundaryCondition(
                variable="pressure_atm",
                predicate="pressure_atm > 200",
                deactivates=frozenset({"BIO_HUMAN_OXYGEN"}),
                activates=frozenset({"BIO_CHEMOSYNTHESIS"},),
            ),
        ),
    ),

    Axiom(
        axiom_id="BIO_CHEMOSYNTHESIS",
        domain="BIOLOGY_DEEP_SEA",
        layer=AxiomLayer.DOMAIN,
        statement="En ausencia de luz y alta presión, algunos organismos usan quimiosíntesis (metano/azufre) como fuente de energía.",
        formal_rule="ENERGY_SOURCE = chemosynthesis(methane, sulfur) IF pressure_atm > 200 AND light = 0",
        confidence=0.997,
        sources=("Deep Sea Biology — Jannasch & Jones",),
        tags=frozenset({"biology", "deep_sea", "chemosynthesis", "extremophile"}),
    ),

    Axiom(
        axiom_id="ENG_CMOS_SENSOR",
        domain="ENGINEERING_CAMERA",
        layer=AxiomLayer.DOMAIN,
        statement="Un sensor CMOS convierte fotones en carga eléctrica mediante el efecto fotoeléctrico.",
        formal_rule="CMOS.signal_chain = photon → photoelectric_effect → charge → voltage → ADC",
        confidence=0.998,
        sources=("Image Sensor Technology — Fossum",),
        tags=frozenset({"camera", "engineering", "cmos", "photon"}),
    ),
]


# ---------------------------------------------------------------------------
# Capa 2 — Situacionales (varían según entorno)
# ---------------------------------------------------------------------------

AXIOMS_LAYER_2: List[Axiom] = [

    Axiom(
        axiom_id="ASTRO_MARS_GRAVITY",
        domain="ASTROPHYSICS",
        layer=AxiomLayer.SITUATIONAL,
        statement="La gravedad superficial en Marte es ~3.72 m/s², aproximadamente el 38% de la terrestre.",
        formal_rule="g_mars = 3.72 m/s^2  (0.378 * g_earth)",
        confidence=0.9999,
        sources=("NASA Mars Fact Sheet",),
        tags=frozenset({"mars", "gravity", "astrophysics"}),
    ),

    Axiom(
        axiom_id="SCI_NEWTONIAN_MACRO_DOMAIN",
        domain="PHYSICS",
        layer=AxiomLayer.SITUATIONAL,
        statement="Las leyes de Newton son válidas para velocidades << c y escalas >> cuánticas.",
        formal_rule="VALID IF velocity < 0.1*c AND scale > 1e-9 m",
        confidence=0.9999,
        sources=("Classical Mechanics — Goldstein",),
        tags=frozenset({"physics", "newtonian", "domain_boundary"}),
    ),
]


# ---------------------------------------------------------------------------
# Función de Bootstrap del Registro
# ---------------------------------------------------------------------------

def build_standard_registry() -> AxiomRegistry:
    """
    Construye e inicializa el AxiomRegistry con la biblioteca estándar.
    Punto de entrada único para el sistema Axioma-Omega.
    """
    registry = AxiomRegistry()
    registry.register_many(AXIOMS_LAYER_0)
    registry.register_many(AXIOMS_LAYER_1)
    registry.register_many(AXIOMS_LAYER_2)
    return registry
