import asyncio
import os
import time
from typing import Optional

import httpx

from src.kernel_lobes.models import SemanticState, TimeoutTrauma
from src.modules.llm_http_cancel import raise_if_llm_cancel_requested


class PerceptiveLobe:
    """
    Hemisferio Izquierdo: Async I/O, Parsing, and Timeout Coercion.

    Perception layer for the ethical kernel with strict timeout enforcement
    and async LLM API integration via httpx.AsyncClient.
    """

    def __init__(self):
        self._timeout = self._get_perception_timeout()
        self._llm_endpoint = os.environ.get("KERNEL_PERCEPTION_LLM_ENDPOINT", "http://localhost:11434/api/generate")

    @staticmethod
    def _get_perception_timeout() -> float:
        """Get timeout from KERNEL_CHAT_TURN_TIMEOUT or fallback to 30s."""
        timeout_str = os.environ.get("KERNEL_CHAT_TURN_TIMEOUT", "30")
        try:
            return float(timeout_str)
        except ValueError:
            return 30.0

    async def observe(self, raw_input: str, multimodal_payload: dict | None = None) -> SemanticState:
        """
        Takes raw input, queries LLMs via API with strict timeouts.
        If timeout occurs, returns a SemanticState with a TimeoutTrauma.

        Args:
            raw_input: Raw natural language input from user/sensor
            multimodal_payload: Optional dict with visual/audio/sensor metadata

        Returns:
            SemanticState with perception_confidence, entities, sentiment, and latency
        """
        start_time = time.time()

        # Check for cancellation before starting
        raise_if_llm_cancel_requested()

        try:
            # Build perception prompt payload
            payload = self._build_perception_payload(raw_input, multimodal_payload)

            # Query LLM with async timeout enforcement
            timeout_obj = httpx.Timeout(self._timeout)
            async with httpx.AsyncClient(timeout=timeout_obj) as client:
                response = await client.post(
                    self._llm_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                llm_result = response.json()

            # Parse LLM response and extract semantic signals
            latency = int((time.time() - start_time) * 1000)
            perception = self._parse_llm_response(llm_result, raw_input)
            perception.sensory_latency_lag = latency

            return perception

        except asyncio.TimeoutError:
            latency = int((time.time() - start_time) * 1000)
            return SemanticState(
                perception_confidence=0.0,
                raw_prompt=raw_input,
                sensory_latency_lag=latency,
                timeout_trauma=TimeoutTrauma(
                    latency_ms=latency,
                    severity=1.0,
                    context=f"Perception LLM timeout after {self._timeout}s"
                )
            )
        except httpx.TimeoutException:
            latency = int((time.time() - start_time) * 1000)
            return SemanticState(
                perception_confidence=0.0,
                raw_prompt=raw_input,
                sensory_latency_lag=latency,
                timeout_trauma=TimeoutTrauma(
                    latency_ms=latency,
                    severity=0.8,
                    context="Perception API timeout or network unreachable"
                )
            )
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            # Graceful degradation: return low-confidence state on any error
            return SemanticState(
                perception_confidence=0.1,
                raw_prompt=raw_input,
                sensory_latency_lag=latency,
                timeout_trauma=TimeoutTrauma(
                    latency_ms=latency,
                    severity=0.5,
                    context=f"Perception processing error: {type(e).__name__}"
                )
            )

    def _build_perception_payload(self, raw_input: str, multimodal_payload: dict | None) -> dict:
        """Build request payload for LLM perception endpoint."""
        payload = {
            "prompt": f"Analyze this situation and extract semantic signals: {raw_input}",
            "stream": False,
            "temperature": 0.3,  # Lower temp for deterministic perception
        }

        if multimodal_payload:
            payload["multimodal_context"] = multimodal_payload

        return payload

    def _parse_llm_response(self, llm_result: dict, raw_input: str) -> SemanticState:
        """Parse LLM JSON response and extract semantic signals."""
        response_text = llm_result.get("response", "")

        # Extract confidence from response (heuristic: check for keyword patterns)
        confidence = self._extract_confidence(response_text)

        # Extract visual entities if mentioned
        entities = self._extract_visual_entities(response_text)

        # Extract sentiment/audio cues
        sentiment = self._extract_sentiment(response_text)

        return SemanticState(
            perception_confidence=confidence,
            raw_prompt=raw_input,
            visual_entities=entities,
            audio_sentiment=sentiment,
            sensory_latency_lag=0  # Will be overwritten by caller
        )

    @staticmethod
    def _extract_confidence(text: str) -> float:
        """Heuristic: extract confidence from LLM response."""
        text_lower = text.lower()

        # Pattern-based confidence scoring
        if "high confidence" in text_lower or "clearly" in text_lower:
            return 0.9
        elif "moderate confidence" in text_lower or "appears" in text_lower:
            return 0.6
        elif "low confidence" in text_lower or "unclear" in text_lower:
            return 0.3
        else:
            return 0.5  # Default neutral

    @staticmethod
    def _extract_visual_entities(text: str) -> list[str]:
        """Heuristic: extract visual entities from LLM response."""
        entities = []

        # Pattern matching for common entity types
        keywords = ["person", "object", "vehicle", "animal", "structure", "hazard"]
        text_lower = text.lower()

        for keyword in keywords:
            if keyword in text_lower:
                entities.append(keyword)

        return entities

    @staticmethod
    def _extract_sentiment(text: str) -> float:
        """Heuristic: extract sentiment/emotional tone from LLM response."""
        text_lower = text.lower()

        # Simple sentiment scoring
        positive_words = ["calm", "safe", "friendly", "happy", "positive"]
        negative_words = ["angry", "distressed", "hostile", "fearful", "negative"]

        positive_count = sum(1 for w in positive_words if w in text_lower)
        negative_count = sum(1 for w in negative_words if w in text_lower)

        if positive_count > negative_count:
            return 0.7  # More positive
        elif negative_count > positive_count:
            return 0.3  # More negative
        else:
            return 0.5  # Neutral
