"""Sync entrypoint: map a finished run to a bytx order when execution is on."""

from __future__ import annotations

import asyncio
import logging

from tradingagents.execution.broker import ExecutionResult, _cfg, execute_intent_async
from tradingagents.execution.decision import ExecutionIntent, intent_from_state

logger = logging.getLogger(__name__)


def build_intent(final_state: dict, config: dict | None = None) -> ExecutionIntent:
    cfg = _cfg(config)
    return intent_from_state(
        final_state,
        allow_short=bool(cfg.get("allow_short")),
        quote=str(cfg.get("quote") or "USDT"),
    )


def execute_decision(
    final_state: dict,
    config: dict | None = None,
    *,
    force: bool = False,
) -> ExecutionResult:
    """Execute the run's rating via bytx when ``execution.enabled`` (or ``force``).

    Safe defaults: disabled, demo mode, crypto-only. Never raises — failures
    come back as ``ExecutionResult(ok=False, ...)``.
    """
    cfg = _cfg(config)
    if not force and not cfg.get("enabled"):
        return ExecutionResult(
            ok=True, action="disabled",
            detail="execution.enabled is false — analysis only",
        )

    intent = build_intent(final_state, config)
    if cfg.get("require_crypto") and intent.symbol is None:
        return ExecutionResult(
            ok=True, action="skip",
            detail=intent.reason or "non-crypto ticker; execution skipped",
        )

    logger.info(
        "Execution intent: side=%s symbol=%s rating=%s (%s)",
        intent.side, intent.symbol, intent.rating, intent.reason,
    )

    try:
        return asyncio.run(execute_intent_async(intent, config))
    except RuntimeError:
        # Already inside an event loop (e.g. notebook) — run on a fresh loop thread.
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(
                asyncio.run, execute_intent_async(intent, config)
            ).result()
