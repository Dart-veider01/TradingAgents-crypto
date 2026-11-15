"""Thin async wrapper around bytx. Market orders by notional, then TP/SL."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

from tradingagents.execution.decision import ExecutionIntent

logger = logging.getLogger(__name__)


def _order_id(order: Any) -> str | None:
    oid = getattr(order, "id", None)
    return str(oid) if oid is not None else None


@dataclass
class ExecutionResult:
    """Outcome of one execution attempt (including skips)."""

    ok: bool
    action: str
    symbol: str | None = None
    order_id: str | None = None
    detail: str = ""
    raw: Any = field(default=None, repr=False)


def _cfg(config: dict | None) -> dict:
    """Execution sub-dict from the run config, with safe defaults."""
    base = {
        "enabled": False,
        "driver": "bytx",
        "exchange": os.getenv("BYTX_EXCHANGE", "bybit"),
        "market": "swap",
        "margin_mode": "cross",
        "demo": True,
        "paper": False,
        "notional_usdt": 50.0,
        "risk_usdt": None,
        "leverage": None,
        "order_type": "market",
        "post_only_bps": 20,  # limit within this many bps of the market goes post-only
        "allow_short": False,
        "quote": "USDT",
        "require_crypto": True,
    }
    if not config:
        return base
    return {**base, **(config.get("execution") or {})}


def _credentials() -> dict[str, str | None]:
    return {
        "api_key": os.getenv("BYTX_API_KEY") or os.getenv("BYTX_KEY"),
        "secret": os.getenv("BYTX_SECRET") or os.getenv("BYTX_API_SECRET"),
        # bytx calls the API passphrase "password" (OKX, KuCoin, Bitget, BloFin).
        "password": os.getenv("BYTX_PASSWORD") or os.getenv("BYTX_PASSPHRASE"),
    }


def _credential_error(exchange: str, creds: dict) -> str | None:
    """Missing key or passphrase for this venue, before any request is sent."""
    from bytx import exchange_info

    needed = exchange_info(exchange).credentials
    if ("api_key" in needed and not creds.get("api_key")) or ("secret" in needed and not creds.get("secret")):
        return "BYTX_API_KEY / BYTX_SECRET required (demo too)"
    if "password" in needed and not creds.get("password"):
        return f"{exchange} needs a passphrase: set BYTX_PASSWORD"
    return None


def _held_side(position: Any) -> str | None:
    """'long' / 'short' when the venue reports an open size, else None."""
    if position is None:
        return None
    size = getattr(position, "size", 0) or 0
    if size <= 0:
        return None
    side = getattr(position, "side", None)
    return side if side in ("long", "short") else None


def _maker_limit(
    side: str,
    price: float | None,
    last: float | None,
    bid: float | None,
    ask: float | None,
    near_bps: float,
) -> tuple[float | None, bool]:
    """Post-only when the limit sits near the market, parked so it does not cross."""
    if price is None or not last or last <= 0:
        return price, False
    if abs(price - last) / last * 10_000 > near_bps:
        return price, False
    if side == "long":
        touch = bid or last
        return min(price, touch), True
    touch = ask or last
    return max(price, touch), True


def _levels(side: str, intent: ExecutionIntent, last: float | None) -> tuple[float | None, float | None]:
    """Drop a stop or target that sits on the wrong side of the last price."""
    stop, tp = intent.stop_loss, intent.take_profit
    if last is None:
        return stop, tp
    if side == "long":
        if stop is not None and stop >= last:
            stop = None
        if tp is not None and tp <= last:
            tp = None
    else:
        if stop is not None and stop <= last:
            stop = None
        if tp is not None and tp >= last:
            tp = None
    return stop, tp


async def _ticker(ex, symbol: str):
    try:
        return await ex.ticker(symbol)
    except Exception as exc:  # noqa: BLE001
        logger.warning("ticker(%s) failed: %s", symbol, exc)
        return None


def _mid(ticker) -> float | None:
    if ticker is None:
        return None
    return getattr(ticker, "mark", None) or getattr(ticker, "last", None)


async def _last_price(ex, symbol: str) -> float | None:
    return _mid(await _ticker(ex, symbol))


async def _position_side(ex, symbol: str, market: str) -> str | None:
    if market == "spot":
        return None
    try:
        return _held_side(await ex.position(symbol))
    except Exception as exc:  # noqa: BLE001
        logger.warning("position(%s) failed: %s", symbol, exc)
        return None


async def _protect(ex, symbol: str, side: str, stop: float | None, tp: float | None) -> str:
    if stop is None and tp is None:
        return ""
    try:
        await ex.set_tp_sl(symbol, stop_loss=stop, take_profit=tp, side=side)
    except Exception as exc:  # noqa: BLE001 — entry already filled
        logger.warning("set_tp_sl(%s) failed: %s", symbol, exc)
        return f"; tp/sl not set: {exc}"
    return f"; stop={stop}, tp={tp}"


async def _fit_notional(ex, symbol: str, notional: float) -> tuple[float, str]:
    """Lift the quote size up to the venue minimum, within 3x of what was asked."""
    last = await _last_price(ex, symbol)
    market = await ex.market(symbol)
    need = float(notional)
    if getattr(market, "min_cost", None):
        need = max(need, float(market.min_cost))
    step = getattr(market, "min_amount", None) or getattr(market, "amount_step", None)
    if step and last:
        need = max(need, float(step) * float(last) * 1.02)
    if need <= notional * 1.001:
        return notional, ""
    if need > notional * 3:
        raise ValueError(
            f"exchange minimum is about {need:.0f} USDT, configured notional is {notional:g}"
        )
    return need, f" (raised from {notional:g} to clear the minimum)"


async def _close(ex, symbol: str, market: str):
    if market == "spot":
        return await ex.sell_all(symbol)
    return await ex.close_position(symbol)


async def _open(ex, intent: ExecutionIntent, cfg: dict, side: str) -> ExecutionResult:
    symbol = intent.symbol
    assert symbol is not None
    market = cfg.get("market") or "swap"
    notional = float(cfg["notional_usdt"])
    held = await _position_side(ex, symbol, market)

    if side == "short" and market == "spot":
        return ExecutionResult(
            ok=False, action="error", symbol=symbol,
            detail="short needs market=swap",
        )
    if held == side:
        return ExecutionResult(
            ok=True, action="skip", symbol=symbol,
            detail=f"already {side}",
        )
    if held and held != side:
        await _close(ex, symbol, market)

    ticker = await _ticker(ex, symbol)
    last = _mid(ticker)
    stop, tp = _levels(side, intent, last)
    leverage = cfg.get("leverage")
    if leverage and market != "spot":
        try:
            await ex.set_leverage(symbol, float(leverage))
        except Exception as exc:  # noqa: BLE001
            logger.warning("set_leverage(%s) skipped: %s", symbol, exc)

    risk = cfg.get("risk_usdt")
    price = intent.entry_price if cfg.get("order_type") == "limit" else None
    price, post_only = _maker_limit(
        side, price, last,
        getattr(ticker, "bid", None) if ticker else None,
        getattr(ticker, "ask", None) if ticker else None,
        float(cfg.get("post_only_bps") or 0),
    )
    if risk and stop is not None and market != "spot" and not post_only:
        result = await ex.open_position(
            symbol, side, risk_usdt=float(risk), stop=stop,
            take_profit=tp, leverage=float(leverage) if leverage else None,
            price=price,
        )
        order = getattr(result, "order", None) or result
        return ExecutionResult(
            ok=True, action=f"open_{side}", symbol=symbol,
            order_id=_order_id(order),
            detail=f"risk_usdt={risk}, stop={stop}",
            raw=result,
        )

    try:
        notional, bump = await _fit_notional(ex, symbol, notional)
    except ValueError as exc:
        return ExecutionResult(ok=False, action="error", symbol=symbol, detail=str(exc))

    place = ex.buy if side == "long" else ex.sell
    order = await place(symbol, notional=notional, price=price, post_only=post_only)
    note = await _protect(ex, symbol, side, stop, tp)
    maker = "; post_only" if post_only else ""
    return ExecutionResult(
        ok=True, action="buy" if side == "long" else "open_short", symbol=symbol,
        order_id=_order_id(order),
        detail=f"notional={notional:g}{bump}{maker}{note}",
        raw=order,
    )


async def _run_intent(ex, intent: ExecutionIntent, cfg: dict) -> ExecutionResult:
    symbol = intent.symbol
    assert symbol is not None
    market = cfg.get("market") or "swap"

    if intent.side in ("long", "short"):
        return await _open(ex, intent, cfg, intent.side)

    if intent.side == "close":
        order = await _close(ex, symbol, market)
        if order is None:
            return ExecutionResult(
                ok=True, action="close", symbol=symbol,
                detail="no open position to close",
            )
        return ExecutionResult(
            ok=True, action="close", symbol=symbol,
            order_id=_order_id(order),
            detail="closed position",
            raw=order,
        )

    return ExecutionResult(ok=True, action="skip", symbol=symbol, detail=intent.reason)


async def execute_intent_async(
    intent: ExecutionIntent,
    config: dict | None = None,
) -> ExecutionResult:
    """Place the trade described by ``intent`` through bytx."""
    cfg = _cfg(config)

    if not intent.should_trade:
        return ExecutionResult(
            ok=True, action="skip", symbol=intent.symbol, detail=intent.reason or "no trade",
        )

    try:
        from bytx import create_exchange
        from bytx.paper import PaperConfig
    except ImportError as exc:
        return ExecutionResult(
            ok=False, action="error", symbol=intent.symbol,
            detail="bytx is not installed; run: pip install bytx",
            raw=exc,
        )

    market = cfg.get("market") or "swap"
    kwargs: dict[str, Any] = {
        "market": market,
        "demo": bool(cfg.get("demo", True)),
    }
    if market != "spot" and cfg.get("margin_mode"):
        kwargs["margin_mode"] = cfg["margin_mode"]
    exchange_name = str(cfg.get("exchange") or "bybit")
    if cfg.get("paper"):
        kwargs["paper"] = True
        kwargs["paper_config"] = PaperConfig(
            balance={"USDT": max(float(cfg["notional_usdt"]) * 20, 1000)},
        )
    else:
        creds = {k: v for k, v in _credentials().items() if v}
        if missing := _credential_error(exchange_name, creds):
            return ExecutionResult(
                ok=False, action="error", symbol=intent.symbol, detail=missing,
            )
        kwargs.update(creds)
    ex = create_exchange(exchange_name, **kwargs)
    try:
        await ex.connect()
        return await _run_intent(ex, intent, cfg)
    except Exception as exc:  # noqa: BLE001
        logger.exception("bytx execution failed for %s", intent.symbol)
        return ExecutionResult(
            ok=False, action="error", symbol=intent.symbol,
            detail=str(exc), raw=exc,
        )
    finally:
        try:
            await ex.close()
        except Exception:  # noqa: BLE001
            logger.warning("bytx close(%s) failed", exchange_name)
