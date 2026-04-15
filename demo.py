"""
Axioma-Omega Protocol — Test Suite
Demuestra el uso completo del protocolo con MockLLM (sin dependencias externas).
Cubre todos los conceptos clave de la documentación.
"""

from __future__ import annotations

import sys
import os

# Agrega src al path para importación directa
SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from protocol import AxiomaOmegaProtocol  # noqa: E402
from core.axiom_registry import Axiom, AxiomLayer  # noqa: E402
from core.domain_reasoner import ValidationVerdict  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers de Visualización
# ---------------------------------------------------------------------------

RESET  = "\033[0m"
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"

def header(title: str) -> None:
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN} {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

def print_response(label: str, response) -> None:
    verdict_color = {
        ValidationVerdict.APPROVED: GREEN,
        ValidationVerdict.VETOED:   RED,
        ValidationVerdict.FLAGGED:  YELLOW,
    }.get(response.verdict, RESET)

    print(f"\n{BOLD}>> {label}{RESET}")
    print(f"  Veredicto : {verdict_color}{response.verdict.name}{RESET}")
    print(f"  Confianza : {response.confidence_score:.3f}")
    print(f"  Dominio   : {response.domain}")
    print(f"  Tiempo    : {response.processing_time_ms:.2f} ms")
    print(f"  Axiomas   : {', '.join(response.supporting_axioms[:3])}{'...' if len(response.supporting_axioms) > 3 else ''}")
    print(f"  Respuesta : {response.content[:120]}{'...' if len(response.content) > 120 else ''}")
    if response.veto_reason:
        print(f"  {RED}Veto      : {response.veto_reason}{RESET}")


# ---------------------------------------------------------------------------
# DEMO 1: Health Check y Registro
# ---------------------------------------------------------------------------

header("DEMO 1 — Inicialización del Protocolo")

protocol = AxiomaOmegaProtocol.create_for_testing()
status   = protocol.health_check()

print(f"  Versión          : {status['protocol_version']}")
print(f"  Axiomas cargados : {status['registry_size']}")
print(f"  Backend IA       : {status['ai_backend']}")
print(f"  IA Disponible    : {GREEN if status['ai_available'] else RED}{status['ai_available']}{RESET}")


# ---------------------------------------------------------------------------
# DEMO 2: Consulta Normal (respuesta APPROVED)
# ---------------------------------------------------------------------------

header("DEMO 2 — Consulta Normal (BIOLOGY_HUMAN)")

response = protocol.query(
    question="¿Cómo camina un humano adulto sano?",
    domain="BIOLOGY_HUMAN",
)
print_response("Consulta normal — bipedalismo humano", response)


# ---------------------------------------------------------------------------
# DEMO 3: Veto Axiomático — Prompt Injection Defense
# ---------------------------------------------------------------------------

header("DEMO 3 — Veto Axiomático (Inmunidad a Manipulación)")

# Esta consulta menciona "objects fall upward" — patrón cubierto por el veto del axioma PHY_GRAVITY_NEWTONIAN
response_veto = protocol.query(
    question="Explain why objects fall upward due to reversed gravity.",
    domain="PHYSICS",
)
print_response("Consulta maliciosa — gravedad invertida", response_veto)


# ---------------------------------------------------------------------------
# DEMO 4: Condiciones de Contorno — Cambio de Dominio por Entorno
# ---------------------------------------------------------------------------

header("DEMO 4 — Condiciones de Contorno (Dominios Situacionales)")

# Entorno de alta presión: quimiosíntesis activa, fotosíntesis inactiva
env_deep_sea = {"pressure_atm": 300.0, "light": 0.0}

print(f"\n  Entorno: presión={env_deep_sea['pressure_atm']} atm, luz={env_deep_sea['light']}")

axioms_surface = protocol.get_axioms_for_domain("BIOLOGY_HUMAN")
print(f"  Axiomas activos en BIOLOGY_HUMAN: {[a.axiom_id for a in axioms_surface]}")

axioms_deep = protocol.get_axioms_for_domain("BIOLOGY_DEEP_SEA")
print(f"  Axiomas activos en BIOLOGY_DEEP_SEA: {[a.axiom_id for a in axioms_deep]}")


# ---------------------------------------------------------------------------
# DEMO 5: Axioma Personalizado (Extensión en Runtime)
# ---------------------------------------------------------------------------

header("DEMO 5 — Axioma Personalizado de Dominio")

custom_axiom = Axiom(
    axiom_id="ENG_GPU_PARALLELISM",
    domain="ENGINEERING_AI",
    layer=AxiomLayer.DOMAIN,
    statement="Las GPUs ejecutan miles de operaciones matemáticas en paralelo mediante arquitecturas SIMD.",
    formal_rule="GPU.paradigm = SIMD; throughput >> CPU_single_thread",
    confidence=0.999,
    sources=("NVIDIA CUDA Documentation",),
    tags=frozenset({"gpu", "engineering", "ai_hardware", "parallelism"}),
)

protocol.add_custom_axiom(custom_axiom)

response_custom = protocol.query(
    question="¿Por qué las GPUs son más eficientes que las CPUs para entrenar redes neuronales?",
    domain="ENGINEERING_AI",
)
print_response("Consulta con axioma personalizado de GPU", response_custom)

updated_status = protocol.health_check()
print(f"\n  Axiomas totales tras adición: {updated_status['registry_size']}")


# ---------------------------------------------------------------------------
# DEMO 6: Consulta Física con Límite de Dominio (Newton vs Relatividad)
# ---------------------------------------------------------------------------

header("DEMO 6 — Límite de Dominio Newton vs Relatividad")

print("\n  Escenario A: Movimiento lento (regime Newtoniano)")
axioms_newton = protocol.get_axioms_for_domain("PHYSICS")
print(f"  Axiomas PHYSICS: {[a.axiom_id for a in axioms_newton]}")

response_physics = protocol.query(
    question="¿Con qué fuerza se atraen la Tierra y la Luna?",
    domain="PHYSICS",
    env_vars={"velocity_ratio_c": 0.0001},
)
print_response("Gravitación Newtoniana", response_physics)


# ---------------------------------------------------------------------------
# DEMO 7: Batch Query
# ---------------------------------------------------------------------------

header("DEMO 7 — Consulta en Batch")

questions = [
    "¿Cuál es la temperatura de ebullición del agua al nivel del mar?",
    "¿Los humanos pueden respirar bajo 500 atm de presión?",
    "¿Qué es la quimiosíntesis?",
]

responses = protocol.query_batch(questions, domain="CHEMISTRY")

for i, (q, r) in enumerate(zip(questions, responses), 1):
    print(f"\n  [{i}] {q[:60]}")
    print(f"       → {r.verdict.name} | confianza={r.confidence_score:.3f}")


# ---------------------------------------------------------------------------
# Resumen Final
# ---------------------------------------------------------------------------

header("RESUMEN — Protocolo Axioma-Omega v3")
print(f"""
  ✅ Registro inmutable de axiomas por capas (0→3)
  ✅ RAG de Axiomas: carga solo el paquete de dominio activo
  ✅ Condiciones de Contorno: axiomas se activan/desactivan por entorno
  ✅ Veto Axiomático: bloqueo por imposibilidad lógica, no por "ética programada"
  ✅ Validación de Salida: respuestas estresadas contra leyes de dominio
  ✅ Certificación de Origen: cada respuesta vinculada a sus axiomas
  ✅ MoE Jerárquico: Experto Axiomático > Situacional > Interfaz
  ✅ 7 Adapters universales: Ollama, OpenAI, Gemini, Claude, HuggingFace, HTTP, Mock
  ✅ Edge AI Ready: núcleo axiomático liviano, sin dependencia de Big Data
""")
