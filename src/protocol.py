"""
Axioma-Omega Protocol — Public API Facade
==========================================
ES: Punto de entrada único para el protocolo.
    La UI y los agentes externos llaman SOLO a esta fachada; nunca acceden
    directamente a DomainReasoner o AxiomRegistry.
    Cumple el principio S (Single Responsibility): su única función es orquestar.

EN: Single entry point for the protocol.
    UI and external agents call ONLY this facade; they NEVER access
    DomainReasoner or AxiomRegistry directly.
    Fulfills the S (Single Responsibility) principle: its only job is to orchestrate.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from core.axiom_registry import Axiom, AxiomLayer, AxiomRegistry
from core.domain_reasoner import AxiomicResponse, DomainReasoner, ValidationVerdict
from adapters.llm_adapter import (
    AIAdapter,
    AnthropicAdapter,
    GeminiAdapter,
    GenericHTTPAdapter,
    HuggingFaceAdapter,
    MockAdapter,
    OllamaAdapter,
    OpenAIAdapter,
)
from axioms.standard_library import build_standard_registry


# ---------------------------------------------------------------------------
# ES: Fachada Principal / EN: Main Facade
# ---------------------------------------------------------------------------

class AxiomaOmegaProtocol:
    """
    ES: Facade del Protocolo Axioma-Omega.
        Compatible con CUALQUIER modelo de IA — local o en la nube.

        Modelos soportados:
          Locales   → Ollama (Mistral, LLaMA, Gemma, Phi-3, Qwen, DeepSeek...)
          En la nube → OpenAI (GPT-4o), Google Gemini, Anthropic Claude
          Abiertos  → HuggingFace Inference API (miles de modelos)
          Custom    → GenericHTTPAdapter (cualquier API REST)

    EN: Facade for the Axioma-Omega Protocol.
        Compatible with ANY AI model — local or cloud-based.

        Supported models:
          Local   → Ollama (Mistral, LLaMA, Gemma, Phi-3, Qwen, DeepSeek...)
          Cloud   → OpenAI (GPT-4o), Google Gemini, Anthropic Claude
          Open    → HuggingFace Inference API (thousands of models)
          Custom  → GenericHTTPAdapter (any REST API)

    Uso mínimo / Minimal usage:
        # ES: Con Ollama local (gratis, sin enviar datos a la nube)
        # EN: With local Ollama (free, no data sent to the cloud)
        protocol = AxiomaOmegaProtocol.create_with_ollama()
        response = protocol.query("How does gravity work?", domain="PHYSICS")
        print(response.content)
        print(response.supporting_axioms)  # ES: Certificación de origen / EN: Origin certification

        # ES: Con Google Gemini
        # EN: With Google Gemini
        protocol = AxiomaOmegaProtocol.create_with_gemini(api_key="YOUR_KEY")

        # ES: Con Claude
        # EN: With Claude
        protocol = AxiomaOmegaProtocol.create_with_anthropic(api_key="YOUR_KEY")
    """

    def __init__(
        self,
        registry: AxiomRegistry,
        ai_adapter: AIAdapter,
    ) -> None:
        self._registry = registry
        self._adapter  = ai_adapter
        # ES: El Reasoner es la capa de lógica pura — no sabe qué proveedor usa
        # EN: The Reasoner is the pure logic layer — it has no knowledge of the provider
        self._reasoner = DomainReasoner(
            registry=registry,
            llm_inference_fn=ai_adapter.infer,
        )

    # ------------------------------------------------------------------
    # ES: Factories Semánticos / EN: Semantic Factory Methods
    # ------------------------------------------------------------------

    @classmethod
    def create_with_ollama(
        cls,
        model: str = "mistral:latest",
        base_url: str = "http://localhost:11434/v1",
        temperature: float = 0.1,
        extra_axioms: Optional[List[Axiom]] = None,
    ) -> "AxiomaOmegaProtocol":
        """
        ES: Crea el protocolo con un modelo local vía Ollama.
            Edge AI — tus datos nunca salen del dispositivo.
            Modelos recomendados: mistral:latest, llama3:8b, gemma2:9b, phi3:medium

        EN: Creates the protocol with a local model via Ollama.
            Edge AI — your data never leaves the device.
            Recommended models: mistral:latest, llama3:8b, gemma2:9b, phi3:medium
        """
        registry = build_standard_registry()
        if extra_axioms:
            registry.register_many(extra_axioms)
        return cls(registry=registry, ai_adapter=OllamaAdapter(base_url=base_url, model=model, temperature=temperature))

    @classmethod
    def create_with_openai(
        cls,
        api_key: str,
        model: str = "gpt-4o",
        temperature: float = 0.1,
        extra_axioms: Optional[List[Axiom]] = None,
    ) -> "AxiomaOmegaProtocol":
        """
        ES: Crea el protocolo conectado a OpenAI (GPT-4o, GPT-4-turbo, GPT-3.5).
        EN: Creates the protocol connected to OpenAI (GPT-4o, GPT-4-turbo, GPT-3.5).
        """
        registry = build_standard_registry()
        if extra_axioms:
            registry.register_many(extra_axioms)
        return cls(registry=registry, ai_adapter=OpenAIAdapter(api_key=api_key, model=model, temperature=temperature))

    @classmethod
    def create_with_gemini(
        cls,
        api_key: str,
        model: str = "gemini-1.5-flash",
        temperature: float = 0.1,
        extra_axioms: Optional[List[Axiom]] = None,
    ) -> "AxiomaOmegaProtocol":
        """
        ES: Crea el protocolo conectado a Google Gemini.
            Requiere: pip install google-generativeai
            Modelos: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash

        EN: Creates the protocol connected to Google Gemini.
            Requires: pip install google-generativeai
            Models: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash
        """
        registry = build_standard_registry()
        if extra_axioms:
            registry.register_many(extra_axioms)
        return cls(registry=registry, ai_adapter=GeminiAdapter(api_key=api_key, model=model, temperature=temperature))

    @classmethod
    def create_with_anthropic(
        cls,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.1,
        extra_axioms: Optional[List[Axiom]] = None,
    ) -> "AxiomaOmegaProtocol":
        """
        ES: Crea el protocolo conectado a Anthropic Claude.
            Requiere: pip install anthropic
            Modelos: claude-3-5-sonnet, claude-3-opus, claude-3-haiku

        EN: Creates the protocol connected to Anthropic Claude.
            Requires: pip install anthropic
            Models: claude-3-5-sonnet, claude-3-opus, claude-3-haiku
        """
        registry = build_standard_registry()
        if extra_axioms:
            registry.register_many(extra_axioms)
        return cls(registry=registry, ai_adapter=AnthropicAdapter(api_key=api_key, model=model, temperature=temperature))

    @classmethod
    def create_with_huggingface(
        cls,
        api_key: str,
        model_id: str = "mistralai/Mistral-7B-Instruct-v0.3",
        extra_axioms: Optional[List[Axiom]] = None,
    ) -> "AxiomaOmegaProtocol":
        """
        ES: Crea el protocolo con cualquier modelo de HuggingFace Inference API.
            Requiere: pip install huggingface-hub
            Miles de modelos open-source disponibles.

        EN: Creates the protocol with any HuggingFace Inference API model.
            Requires: pip install huggingface-hub
            Thousands of open-source models available.
        """
        registry = build_standard_registry()
        if extra_axioms:
            registry.register_many(extra_axioms)
        return cls(registry=registry, ai_adapter=HuggingFaceAdapter(api_key=api_key, model_id=model_id))

    @classmethod
    def create_with_custom_api(
        cls,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        request_template: Optional[Dict] = None,
        response_path: Optional[List] = None,
        extra_axioms: Optional[List[Axiom]] = None,
    ) -> "AxiomaOmegaProtocol":
        """
        ES: Crea el protocolo con CUALQUIER API REST personalizada.
            Máxima flexibilidad — úsalo con cualquier backend propietario.

        EN: Creates the protocol with ANY custom REST API.
            Maximum flexibility — use it with any proprietary backend.
        """
        registry = build_standard_registry()
        if extra_axioms:
            registry.register_many(extra_axioms)
        return cls(
            registry=registry,
            ai_adapter=GenericHTTPAdapter(
                endpoint=endpoint,
                headers=headers,
                request_template=request_template,
                response_path=response_path,
            ),
        )

    @classmethod
    def create_for_testing(
        cls,
        fixed_response: Optional[str] = None,
    ) -> "AxiomaOmegaProtocol":
        """
        ES: Crea el protocolo con MockAdapter — no requiere servidor externo.
            Ideal para tests unitarios, CI/CD y demos offline.

        EN: Creates the protocol with MockAdapter — no external server required.
            Ideal for unit tests, CI/CD pipelines, and offline demos.
        """
        registry = build_standard_registry()
        return cls(registry=registry, ai_adapter=MockAdapter(fixed_response))

    # ------------------------------------------------------------------
    # ES: API de Consulta / EN: Query API
    # ------------------------------------------------------------------

    def query(
        self,
        question: str,
        domain: str,
        env_vars: Optional[Dict[str, float]] = None,
    ) -> AxiomicResponse:
        """
        ES: Consulta axiomática completa con validación y Certificación de Origen.
            Retorna AxiomicResponse con veredicto, confianza y axiomas vinculados.

        EN: Full axiom-grounded query with validation and Origin Certification.
            Returns AxiomicResponse with verdict, confidence, and linked axioms.
        """
        return self._reasoner.reason(
            query=question,
            domain=domain,
            env_vars=env_vars or {},
        )

    def query_batch(
        self,
        questions: List[str],
        domain: str,
        env_vars: Optional[Dict[str, float]] = None,
    ) -> List[AxiomicResponse]:
        """
        ES: Procesa múltiples consultas bajo el mismo contexto de dominio.
        EN: Processes multiple queries under the same domain context.
        """
        return [self.query(q, domain, env_vars) for q in questions]

    # ------------------------------------------------------------------
    # ES: Gestión de Axiomas / EN: Axiom Management
    # ------------------------------------------------------------------

    def add_custom_axiom(self, axiom: Axiom) -> None:
        """
        ES: Registra un axioma personalizado en tiempo de ejecución.
            Permite extender el protocolo para dominios propietarios o científicos.

        EN: Registers a custom axiom at runtime.
            Allows extending the protocol for proprietary or scientific domains.
        """
        self._registry.register(axiom)

    def get_axioms_for_domain(self, domain: str) -> List[Axiom]:
        """ES: Retorna todos los axiomas del dominio. / EN: Returns all axioms for the domain."""
        return self._registry.query_by_domain(domain)

    def health_check(self) -> Dict[str, object]:
        """
        ES: Estado del protocolo: versión, axiomas cargados, proveedor de IA y disponibilidad.
        EN: Protocol status: version, loaded axioms, AI provider, and availability.
        """
        return {
            "protocol_version": "Axioma-Omega v3",
            "registry_size":    len(self._registry),
            "ai_backend":       type(self._adapter).__name__,
            "ai_available":     self._adapter.health_check(),
        }
