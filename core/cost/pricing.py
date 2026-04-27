"""Pricing configuration loader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - surfaced at runtime
    raise RuntimeError(
        "Missing dependency 'PyYAML'. Install with: pip install pyyaml"
    ) from exc


@dataclass(slots=True)
class ModelPricing:
    """Per-model token pricing config."""

    currency: str
    input_per_1k: float
    output_per_1k: float
    cached_input_per_1k: float


class PricingCatalog:
    """Resolves model pricing from local YAML config."""

    def __init__(self, pricing_file: Path) -> None:
        self._pricing_file = pricing_file
        self._raw = self._load()

    def _load(self) -> dict:
        if not self._pricing_file.exists():
            raise FileNotFoundError(f"Pricing config not found: {self._pricing_file}")
        with self._pricing_file.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        if "providers" not in data:
            raise ValueError("Invalid pricing config: missing top-level 'providers'")
        return data

    def refresh(self) -> None:
        self._raw = self._load()

    def resolve(self, provider: str, model: str) -> ModelPricing:
        provider_config = self._raw["providers"].get(provider)
        if not provider_config:
            raise KeyError(f"No pricing config for provider '{provider}'")
        model_config = provider_config.get(model)
        if not model_config:
            raise KeyError(
                f"No pricing config for model '{model}' under provider '{provider}'"
            )
        currency = model_config.get("currency", self._raw.get("currency", "USD"))
        return ModelPricing(
            currency=currency,
            input_per_1k=float(model_config["input_per_1k"]),
            output_per_1k=float(model_config["output_per_1k"]),
            cached_input_per_1k=float(model_config.get("cached_input_per_1k", 0.0)),
        )

