"""Map TradingAgents tickers to bytx exchange symbols (e.g. BTC-USD -> BTC/USDT)."""

from __future__ import annotations

from tradingagents.dataflows.symbols import crypto_base

# Extra bases beyond the Yahoo-facing set — bytx can trade many more coins.
_EXTRA_CRYPTO_BASES = frozenset({
    "BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "LTC", "BCH", "DOT", "AVAX", "LINK",
    "BNB", "TON", "TRX", "SUI", "NEAR", "APT", "ARB", "OP", "PEPE", "WIF", "UNI",
    "ATOM", "FIL", "AAVE", "MKR", "INJ", "SEI", "TIA", "ORDI",
})


def to_bytx_symbol(ticker: str, quote: str = "USDT") -> str | None:
    """Return a bytx pair like ``BTC/USDT``, or None if the ticker is not crypto.

    Accepts Yahoo-style (``BTC-USD``), compact (``BTCUSDT``), slash (``BTC/USDT``)
    and bare bases known as crypto (``BTC``).
    """
    if not isinstance(ticker, str) or not ticker.strip():
        return None

    raw = ticker.strip().upper().rstrip("+")

    if "/" in raw:
        base, _, q = raw.partition("/")
        base = base.strip()
        q = (q or quote).split(":")[0].strip()
        if base:
            return f"{base}/{q}"

    base = crypto_base(raw)
    if base:
        return f"{base}/{quote}"

    compact = raw.replace("-", "").replace("_", "")
    for q in ("USDT", "USDC", "USD"):
        if compact.endswith(q) and len(compact) > len(q):
            b = compact[: -len(q)]
            if b in _EXTRA_CRYPTO_BASES:
                return f"{b}/{quote}"
            return None

    if compact in _EXTRA_CRYPTO_BASES:
        return f"{compact}/{quote}"

    return None


def is_executable_crypto(ticker: str) -> bool:
    """Whether ``ticker`` can be sent to a crypto exchange via bytx."""
    return to_bytx_symbol(ticker) is not None
