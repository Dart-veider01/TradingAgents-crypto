"""Turn a finished TradingAgents run into a concrete execution intent."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from tradingagents.agents.rating import RATING_REVIEW, is_review, run_rating
from tradingagents.execution.symbols import to_bytx_symbol

Side = Literal["long", "short", "close", "skip"]

_NUM = r"([0-9][0-9,]*(?:\.[0-9]+)?)"
_STOP_RE = re.compile(rf"\*\*Stop Loss\*\*:\s*{_NUM}", re.IGNORECASE)
_ENTRY_RE = re.compile(rf"\*\*Entry Price\*\*:\s*{_NUM}", re.IGNORECASE)
_TARGET_RE = re.compile(rf"\*\*Price Target\*\*:\s*{_NUM}", re.IGNORECASE)

# Portfolio Manager 5-tier -> trade action
_RATING_TO_SIDE: dict[str, Side] = {
    "Buy": "long",
    "Overweight": "long",
    "Hold": "skip",
    "Underweight": "close",
    "Sell": "close",
}


@dataclass(frozen=True)
class ExecutionIntent:
    """What the execution layer should do with a finished analysis."""

    side: Side
    symbol: str | None
    rating: str
    stop_loss: float | None = None
    take_profit: float | None = None
    entry_price: float | None = None
    reason: str = ""

    @property
    def should_trade(self) -> bool:
        return self.side in ("long", "short", "close") and bool(self.symbol)


def _parse_optional_float(pattern: re.Pattern[str], text: str) -> float | None:
    if not text:
        return None
    m = pattern.search(text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def intent_from_state(
    final_state: dict,
    *,
    allow_short: bool = False,
    quote: str = "USDT",
) -> ExecutionIntent:
    """Build an ExecutionIntent from a run's final state.

    Hold and REVIEW never trade. Sell closes an open position; with
    ``allow_short=True`` a Sell with no existing position opens a short
    (handled later by the broker when flat).
    """
    ticker = final_state.get("company_of_interest") or ""
    rating = run_rating(final_state)
    symbol = to_bytx_symbol(ticker, quote=quote)

    if is_review(rating) or rating == RATING_REVIEW:
        return ExecutionIntent(
            side="skip", symbol=symbol, rating=rating,
            reason="rating is REVIEW — not tradeable",
        )

    if symbol is None:
        return ExecutionIntent(
            side="skip", symbol=None, rating=rating,
            reason=f"ticker {ticker!r} is not a crypto pair for bytx",
        )

    side = _RATING_TO_SIDE.get(rating, "skip")
    # Sell + allow_short → open/flip short; Underweight always just closes.
    if rating == "Sell" and allow_short:
        side = "short"

    trader_plan = final_state.get("trader_investment_plan") or ""
    decision = final_state.get("final_trade_decision") or ""
    stop = _parse_optional_float(_STOP_RE, trader_plan)
    entry = _parse_optional_float(_ENTRY_RE, trader_plan)
    target = _parse_optional_float(_TARGET_RE, decision)

    return ExecutionIntent(
        side=side,
        symbol=symbol,
        rating=rating,
        stop_loss=stop,
        take_profit=target,
        entry_price=entry,
        reason=f"rating={rating}",
    )
