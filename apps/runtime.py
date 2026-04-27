"""Runtime wiring for token monitor components."""

from __future__ import annotations

import os
from dotenv import load_dotenv
from pathlib import Path

from adapters.storage.sqlite.repository import TokenUsageRepository
from adapters.telemetry.usage_logger import UsageLogger
from core.cost.budget import BudgetPolicy
from core.cost.pricing import PricingCatalog
from core.tasks.llm_wrapper import LLMChatWrapper

load_dotenv()

def resolve_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_db_path() -> Path:
    env_path = os.environ.get("TOKEN_USAGE_DB_PATH")
    if env_path:
        return Path(env_path)
    return resolve_repo_root() / "data" / "private" / "token_usage.db"


def build_runtime() -> tuple[TokenUsageRepository, UsageLogger, LLMChatWrapper]:
    repo_root = resolve_repo_root()
    repository = TokenUsageRepository(resolve_db_path())
    pricing = PricingCatalog(repo_root / "config" / "token_pricing.yaml")
    budget = BudgetPolicy(repo_root / "config" / "token_budgets.yaml")
    logger = UsageLogger(repository=repository, pricing_catalog=pricing, budget_policy=budget)
    wrapper = LLMChatWrapper(usage_logger=logger)
    return repository, logger, wrapper

