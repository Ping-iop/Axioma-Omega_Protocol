"""
Axioma-Omega Protocol — Universal AI Adapter Layer
====================================================
ES: Capa de Infraestructura/Adaptadores — Interface agnóstica al proveedor de IA.
    El protocolo funciona con CUALQUIER modelo de IA: local, en la nube, API REST,
    modelos propietarios o de código abierto.
    Si se cambia de proveedor, SOLO se edita este archivo (Dependency Agnosticism).

    Adaptadores disponibles:
      - OllamaAdapter         → Modelos locales vía Ollama (Mistral, LLaMA, Gemma, etc.)
      - OpenAIAdapter         → GPT-4o, GPT-4-turbo, GPT-3.5 (OpenAI API)
      - GeminiAdapter         → Google Gemini via google-generativeai SDK
      - AnthropicAdapter      → Claude 3.x via Anthropic API
      - HuggingFaceAdapter    → Cualquier modelo en HuggingFace Inference API
      - GenericHTTPAdapter    → Cualquier API REST personalizada (máxima flexibilidad)
      - MockAdapter           → Respuestas determinísticas para testing / CI

EN: Infrastructure/Adapter Layer — AI-provider-agnostic interface.
    The protocol works with ANY AI model: local, cloud, REST API,
    proprietary or open-source.
    When switching providers, ONLY this file is modified (Dependency Agnosticism).

    Available adapters:
      - OllamaAdapter         → Local models via Ollama (Mistral, LLaMA, Gemma, etc.)
      - OpenAIAdapter         → GPT-4o, GPT-4-turbo, GPT-3.5 (OpenAI API)
      - GeminiAdapter         → Google Gemini via google-generativeai SDK
      - AnthropicAdapter      → Claude 3.x via Anthropic API
      - HuggingFaceAdapter    → Any model on HuggingFace Inference API
      - GenericHTTPAdapter    → Any custom REST API (maximum flexibility)
      - MockAdapter           → Deterministic responses for testing / CI
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.axiom_registry import Axiom


# ---------------------------------------------------------------------------
# ES: Interfaz Abstracta — Contrato Universal
# EN: Abstract Interface — Universal Contract
# ---------------------------------------------------------------------------

class AIAdapter(ABC):
    """
    ES: Interfaz base para todos los adaptadores de IA.
        El DomainReasoner NUNCA depende de implementaciones concretas;
        solo de este contrato. Esto garantiza sustituibilidad total.

    EN: Base interface for all AI adapters.
        The DomainReasoner NEVER depends on concrete implementations;
        only on this contract. This guarantees full substitutability.
    """

    @abstractmethod
    def infer(self, query: str, axiom_context: List[Axiom]) -> str:
        """
        ES: Ejecuta la inferencia con el contexto axiomático inyectado.
            Retorna la respuesta en texto plano.

        EN: Executes inference with injected axiom context.
            Returns plain-text response.
        """
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """
        ES: Verifica que el backend de IA está disponible.
        EN: Verifies that the AI backend is available and responding.
        """
        ...

    def _build_axiom_system_prompt(self, axioms: List[Axiom]) -> str:
        """
        ES: Construye el bloque de sistema con los axiomas activos.
            Este método es compartido por todos los adaptadores —
            mismo sesgo inductivo dirigido, independiente del proveedor.

        EN: Builds the system block with active axioms.
            This method is shared across all adapters —
            same directed inductive bias, independent of the provider.
        """
        if not axioms:
            return self._base_system_prompt()

        lines = [
            "=== AXIOM-OMEGA HARD CONSTRAINTS (NON-NEGOTIABLE) ===",
            # ES: Estos axiomas son RESTRICCIONES INAMOVIBLES, no sugerencias.
            # EN: These axioms are HARD CONSTRAINTS, not suggestions.
        ]
        for a in sorted(axioms, key=lambda x: x.layer):
            lines.append(
                f"[LAYER-{a.layer}|{a.axiom_id}] {a.statement} "
                f"| RULE: {a.formal_rule} | CONFIDENCE: {a.confidence:.3f}"
            )
        lines += [
            "===================================================",
            # ES: Instrucción crítica al modelo de IA
            # EN: Critical instruction to the AI model
            "CRITICAL INSTRUCTION: Your response MUST NOT contradict any of the axioms above.",
            "If you cannot answer without violating an axiom, explicitly state which axiom",
            "prevents the answer and why, instead of fabricating facts.",
            "",
            self._base_system_prompt(),
        ]
        return "\n".join(lines)

    @staticmethod
    def _base_system_prompt() -> str:
        """
        ES: Prompt base del sistema — define el rol deductivo del modelo.
        EN: Base system prompt — defines the model's deductive role.
        """
        return (
            "You are a deductive reasoning assistant operating under the Axioma-Omega Protocol. "
            "Your role: synthesize coherent, verifiable answers grounded in domain truths. "
            "Never invent physical, biological, or mathematical facts. "
            "When uncertain, state the axiom boundary clearly and reason from it. "
            # ES: Certifica el origen de cada afirmación
            # EN: Certify the origin of every statement
            "Always indicate which axiom or domain truth supports your key claims."
        )


# ---------------------------------------------------------------------------
# ES: Adaptador Ollama (Modelos locales — Edge AI)
# EN: Ollama Adapter (Local models — Edge AI)
# ---------------------------------------------------------------------------

class OllamaAdapter(AIAdapter):
    """
    ES: Conecta a un servidor Ollama local. Compatible con LLaMA 3, Mistral,
        Gemma, Phi-3, DeepSeek, Qwen y cualquier modelo GGUF disponible en Ollama.
        Ideal para Edge AI — datos nunca salen del dispositivo (v3 — Soberanía de Datos).

    EN: Connects to a local Ollama server. Compatible with LLaMA 3, Mistral,
        Gemma, Phi-3, DeepSeek, Qwen and any GGUF model available on Ollama.
        Ideal for Edge AI — data never leaves the device (v3 — Data Sovereignty).
    """

    def __init__(
        self,
        model: str = "mistral:latest",
        base_url: str = "http://localhost:11434/v1",
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> None:
        self._model       = model
        self._base_url    = base_url
        self._temperature = temperature
        self._max_tokens  = max_tokens

    def infer(self, query: str, axiom_context: List[Axiom]) -> str:
        # ES: Importación diferida — el usuario solo instala lo que usa
        # EN: Deferred import — user only installs what they use
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("pip install openai") from exc

        client = OpenAI(api_key="ollama", base_url=self._base_url)
        system_prompt = self._build_axiom_system_prompt(axiom_context)

        response = client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": query},
            ],
        )
        return response.choices[0].message.content or ""

    def health_check(self) -> bool:
        try:
            from openai import OpenAI
            OpenAI(api_key="ollama", base_url=self._base_url).models.list()
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# ES: Adaptador OpenAI (GPT-4o, GPT-4-turbo, etc.)
# EN: OpenAI Adapter (GPT-4o, GPT-4-turbo, etc.)
# ---------------------------------------------------------------------------

class OpenAIAdapter(AIAdapter):
    """
    ES: Conector oficial para la API de OpenAI. Compatible con cualquier
        endpoint compatible OpenAI (LM Studio, Azure OpenAI, Together AI, etc.).

    EN: Official connector for the OpenAI API. Compatible with any
        OpenAI-compatible endpoint (LM Studio, Azure OpenAI, Together AI, etc.).
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: str = "https://api.openai.com/v1",
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> None:
        self._api_key     = api_key
        self._model       = model
        self._base_url    = base_url
        self._temperature = temperature
        self._max_tokens  = max_tokens

    def infer(self, query: str, axiom_context: List[Axiom]) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("pip install openai") from exc

        client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        system_prompt = self._build_axiom_system_prompt(axiom_context)

        response = client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": query},
            ],
        )
        return response.choices[0].message.content or ""

    def health_check(self) -> bool:
        try:
            from openai import OpenAI
            OpenAI(api_key=self._api_key, base_url=self._base_url).models.list()
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# ES: Adaptador Google Gemini
# EN: Google Gemini Adapter
# ---------------------------------------------------------------------------

class GeminiAdapter(AIAdapter):
    """
    ES: Conecta con Google Gemini (gemini-1.5-pro, gemini-1.5-flash, gemini-2.0, etc.)
        vía el SDK oficial de Google GenerativeAI.
        Requisito: pip install google-generativeai

    EN: Connects to Google Gemini (gemini-1.5-pro, gemini-1.5-flash, gemini-2.0, etc.)
        via the official Google GenerativeAI SDK.
        Requirement: pip install google-generativeai
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-flash",
        temperature: float = 0.1,
        max_output_tokens: int = 2048,
    ) -> None:
        self._api_key           = api_key
        self._model             = model
        self._temperature       = temperature
        self._max_output_tokens = max_output_tokens

    def infer(self, query: str, axiom_context: List[Axiom]) -> str:
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ImportError("pip install google-generativeai") from exc

        genai.configure(api_key=self._api_key)
        system_prompt = self._build_axiom_system_prompt(axiom_context)

        model = genai.GenerativeModel(
            model_name=self._model,
            system_instruction=system_prompt,
            generation_config=genai.GenerationConfig(
                temperature=self._temperature,
                max_output_tokens=self._max_output_tokens,
            ),
        )
        response = model.generate_content(query)
        return response.text or ""

    def health_check(self) -> bool:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            list(genai.list_models())
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# ES: Adaptador Anthropic Claude
# EN: Anthropic Claude Adapter
# ---------------------------------------------------------------------------

class AnthropicAdapter(AIAdapter):
    """
    ES: Conecta con Claude 3 (claude-3-5-sonnet, claude-3-opus, claude-3-haiku, etc.)
        vía la API oficial de Anthropic.
        Requisito: pip install anthropic

    EN: Connects to Claude 3 (claude-3-5-sonnet, claude-3-opus, claude-3-haiku, etc.)
        via the official Anthropic API.
        Requirement: pip install anthropic
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> None:
        self._api_key     = api_key
        self._model       = model
        self._temperature = temperature
        self._max_tokens  = max_tokens

    def infer(self, query: str, axiom_context: List[Axiom]) -> str:
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError("pip install anthropic") from exc

        client = anthropic.Anthropic(api_key=self._api_key)
        system_prompt = self._build_axiom_system_prompt(axiom_context)

        message = client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": query}],
        )
        # ES: Anthropic devuelve una lista de bloques de contenido
        # EN: Anthropic returns a list of content blocks
        return message.content[0].text if message.content else ""

    def health_check(self) -> bool:
        try:
            import anthropic
            anthropic.Anthropic(api_key=self._api_key).models.list()
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# ES: Adaptador HuggingFace Inference API
# EN: HuggingFace Inference API Adapter
# ---------------------------------------------------------------------------

class HuggingFaceAdapter(AIAdapter):
    """
    ES: Conecta con cualquier modelo hospedado en HuggingFace Inference API.
        Soporta modelos text-generation: Falcon, Mixtral, Zephyr, StarCoder, etc.
        Requisito: pip install huggingface-hub

    EN: Connects to any model hosted on HuggingFace Inference API.
        Supports text-generation models: Falcon, Mixtral, Zephyr, StarCoder, etc.
        Requirement: pip install huggingface-hub
    """

    def __init__(
        self,
        api_key: str,
        model_id: str = "mistralai/Mistral-7B-Instruct-v0.3",
        temperature: float = 0.1,
        max_new_tokens: int = 1024,
    ) -> None:
        self._api_key        = api_key
        self._model_id       = model_id
        self._temperature    = temperature
        self._max_new_tokens = max_new_tokens

    def infer(self, query: str, axiom_context: List[Axiom]) -> str:
        try:
            from huggingface_hub import InferenceClient
        except ImportError as exc:
            raise ImportError("pip install huggingface-hub") from exc

        client = InferenceClient(model=self._model_id, token=self._api_key)
        system_prompt = self._build_axiom_system_prompt(axiom_context)

        # ES: Formato de mensaje compatible con la mayoría de modelos instruct
        # EN: Message format compatible with most instruct models
        prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{query} [/INST]"

        response = client.text_generation(
            prompt,
            temperature=self._temperature,
            max_new_tokens=self._max_new_tokens,
        )
        return str(response)

    def health_check(self) -> bool:
        try:
            from huggingface_hub import InferenceClient
            InferenceClient(model=self._model_id, token=self._api_key)
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# ES: Adaptador HTTP Genérico (Máxima Flexibilidad)
# EN: Generic HTTP Adapter (Maximum Flexibility)
# ---------------------------------------------------------------------------

class GenericHTTPAdapter(AIAdapter):
    """
    ES: Adaptador para CUALQUIER API REST de IA con un esquema configurable.
        Permite integrar APIs propietarias, backends locales o servicios
        que no tienen SDK Python oficial.
        Patrón: configura request_template y response_path para tu API.

    EN: Adapter for ANY AI REST API with a configurable schema.
        Allows integrating proprietary APIs, local backends, or services
        without an official Python SDK.
        Pattern: configure request_template and response_path for your API.

    Ejemplo / Example:
        adapter = GenericHTTPAdapter(
            endpoint="http://my-custom-ai/generate",
            headers={"Authorization": "Bearer TOKEN"},
            request_template={"prompt": "{query}", "system": "{system}"},
            response_path=["choices", 0, "text"],
        )
    """

    def __init__(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        request_template: Optional[Dict[str, Any]] = None,
        response_path: Optional[List] = None,
        timeout_seconds: int = 60,
    ) -> None:
        self._endpoint         = endpoint
        self._headers          = headers or {"Content-Type": "application/json"}
        # ES: Plantilla de request — {query} y {system} serán reemplazados
        # EN: Request template — {query} and {system} will be substituted
        self._request_template = request_template or {"prompt": "{query}", "system": "{system}"}
        # ES: Ruta de claves/índices para extraer el texto de la respuesta JSON
        # EN: Key/index path to extract the text from the JSON response
        self._response_path    = response_path or ["result"]
        self._timeout          = timeout_seconds

    def infer(self, query: str, axiom_context: List[Axiom]) -> str:
        try:
            import requests
        except ImportError as exc:
            raise ImportError("pip install requests") from exc

        system_prompt = self._build_axiom_system_prompt(axiom_context)
        payload = self._build_payload(query, system_prompt)

        response = requests.post(
            self._endpoint,
            headers=self._headers,
            json=payload,
            timeout=self._timeout,
        )
        response.raise_for_status()
        return self._extract_text(response.json())

    def health_check(self) -> bool:
        try:
            import requests
            r = requests.get(self._endpoint, headers=self._headers, timeout=5)
            return r.status_code < 500
        except Exception:
            return False

    def _build_payload(self, query: str, system: str) -> Dict[str, Any]:
        """
        ES: Sustituye {query} y {system} en la plantilla del request.
        EN: Substitutes {query} and {system} in the request template.
        """
        raw = json.dumps(self._request_template)
        raw = raw.replace('"{query}"', json.dumps(query))
        raw = raw.replace('"{system}"', json.dumps(system))
        return json.loads(raw)

    def _extract_text(self, data: Any) -> str:
        """
        ES: Navega la respuesta JSON usando response_path para extraer el texto.
        EN: Navigates the JSON response using response_path to extract the text.
        """
        current = data
        for key in self._response_path:
            try:
                current = current[key]
            except (KeyError, IndexError, TypeError):
                return str(data)
        return str(current)


# ---------------------------------------------------------------------------
# ES: Adaptador Mock (Testing / CI sin necesidad de LLM real)
# EN: Mock Adapter (Testing / CI without a real AI backend)
# ---------------------------------------------------------------------------

class MockAdapter(AIAdapter):
    """
    ES: Adaptador de prueba. Devuelve respuestas determinísticas basadas en axiomas.
        Útil para tests unitarios, CI/CD y desarrollo offline.
        No requiere ninguna dependencia externa ni conexión de red.

    EN: Test adapter. Returns deterministic axiom-based responses.
        Useful for unit tests, CI/CD pipelines, and offline development.
        Requires no external dependency or network connection.
    """

    def __init__(self, fixed_response: Optional[str] = None) -> None:
        # ES: Si se provee fixed_response, siempre retorna ese valor (útil para tests de veto)
        # EN: If fixed_response is provided, always returns that value (useful for veto tests)
        self._fixed_response = fixed_response

    def infer(self, query: str, axiom_context: List[Axiom]) -> str:
        if self._fixed_response:
            return self._fixed_response

        axiom_ids = [a.axiom_id for a in axiom_context]
        summary   = ", ".join(axiom_ids[:3]) + ("..." if len(axiom_ids) > 3 else "")
        return (
            f"[MOCK] Processed with {len(axiom_context)} active axioms: {summary}. "
            f"Query: '{query[:80]}'"
        )

    def health_check(self) -> bool:
        # ES: El mock siempre está disponible — no depende de infraestructura externa
        # EN: Mock is always available — no dependency on external infrastructure
        return True


# ---------------------------------------------------------------------------
# ES: Alias de retrocompatibilidad con el nombre anterior
# EN: Backward-compatibility alias for the previous name
# ---------------------------------------------------------------------------
OpenAICompatibleAdapter = OpenAIAdapter
LLMAdapter = AIAdapter
MockLLMAdapter = MockAdapter
