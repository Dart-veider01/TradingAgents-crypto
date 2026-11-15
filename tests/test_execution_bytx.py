"""Unit tests for the bytx execution layer (no network)."""

from __future__ import annotations

import pytest

from tradingagents.execution.decision import intent_from_state
from tradingagents.execution.executor import execute_decision
from tradingagents.execution.symbols import is_executable_crypto, to_bytx_symbol


@pytest.mark.unit
@pytest.mark.parametrize(
    "ticker,expected",
    [
        ("BTC-USD", "BTC/USDT"),
        ("BTCUSDT", "BTC/USDT"),
        ("btc/usdt", "BTC/USDT"),
        ("ETH", "ETH/USDT"),
        ("SOL-USDT", "SOL/USDT"),
        ("NVDA", None),
        ("0700.HK", None),
    ],
)
def test_to_bytx_symbol(ticker, expected):
    assert to_bytx_symbol(ticker) == expected


@pytest.mark.unit
def test_is_executable_crypto():
    assert is_executable_crypto("BTC-USD")
    assert not is_executable_crypto("AAPL")
    assert not is_executable_crypto("EURUSD")
    assert not is_executable_crypto("XAUUSD")


@pytest.mark.unit
def test_intent_buy_with_stop():
    state = {
        "company_of_interest": "BTC-USD",
        "final_rating": "Buy",
        "final_trade_decision": "**Rating**: Buy\n\n**Price Target**: 120000",
        "trader_investment_plan": (
            "**Action**: Buy\n\n**Stop Loss**: 90000\n\n**Entry Price**: 100000\n\n"
            "FINAL TRANSACTION PROPOSAL: **BUY**"
        ),
    }
    intent = intent_from_state(state)
    assert intent.should_trade
    assert intent.side == "long"
    assert intent.symbol == "BTC/USDT"
    assert intent.stop_loss == 90000.0
    assert intent.entry_price == 100000.0
    assert intent.take_profit == 120000.0


@pytest.mark.unit
def test_intent_hold_skips():
    state = {
        "company_of_interest": "ETH-USD",
        "final_rating": "Hold",
        "final_trade_decision": "**Rating**: Hold",
        "trader_investment_plan": "",
    }
    intent = intent_from_state(state)
    assert not intent.should_trade
    assert intent.side == "skip"


@pytest.mark.unit
def test_intent_sell_closes_by_default():
    state = {
        "company_of_interest": "BTCUSDT",
        "final_rating": "Sell",
        "final_trade_decision": "**Rating**: Sell",
        "trader_investment_plan": "",
    }
    intent = intent_from_state(state, allow_short=False)
    assert intent.side == "close"
    intent_short = intent_from_state(state, allow_short=True)
    assert intent_short.side == "short"


@pytest.mark.unit
def test_intent_equity_skipped():
    state = {
        "company_of_interest": "NVDA",
        "final_rating": "Buy",
        "final_trade_decision": "**Rating**: Buy",
        "trader_investment_plan": "",
    }
    intent = intent_from_state(state)
    assert not intent.should_trade
    assert intent.symbol is None


@pytest.mark.unit
def test_intent_reads_comma_prices():
    state = {
        "company_of_interest": "BTC-USD",
        "final_rating": "Buy",
        "final_trade_decision": "**Price Target**: 120,000",
        "trader_investment_plan": "**Stop Loss**: 90,000.5\n**Entry Price**: 100,000",
    }
    intent = intent_from_state(state)
    assert intent.stop_loss == 90000.5
    assert intent.entry_price == 100000.0
    assert intent.take_profit == 120000.0


@pytest.mark.unit
def test_okx_requires_passphrase():
    from tradingagents.execution.broker import _credential_error

    assert _credential_error("okx", {"api_key": "k", "secret": "s"}) == (
        "okx needs a passphrase: set BYTX_PASSWORD"
    )
    assert _credential_error("kucoin", {"api_key": "k", "secret": "s", "password": "p"}) is None
    assert _credential_error("bybit", {"api_key": "k", "secret": "s"}) is None


def test_near_limit_is_post_only_and_does_not_cross():
    from tradingagents.execution.broker import _maker_limit

    price, post_only = _maker_limit("long", 100.05, 100.0, bid=99.9, ask=100.1, near_bps=20)
    assert post_only
    assert price == 99.9

    price, post_only = _maker_limit("short", 99.95, 100.0, bid=99.9, ask=100.1, near_bps=20)
    assert post_only
    assert price == 100.1

    price, post_only = _maker_limit("long", 90.0, 100.0, bid=99.9, ask=100.1, near_bps=20)
    assert not post_only
    assert price == 90.0


def test_levels_drop_stop_on_the_wrong_side():
    from tradingagents.execution.broker import _levels
    from tradingagents.execution.decision import ExecutionIntent

    bad = ExecutionIntent(
        side="long", symbol="BTC/USDT", rating="Buy",
        stop_loss=120.0, take_profit=80.0,
    )
    assert _levels("long", bad, 100.0) == (None, None)

    good = ExecutionIntent(
        side="long", symbol="BTC/USDT", rating="Buy",
        stop_loss=90.0, take_profit=130.0,
    )
    assert _levels("long", good, 100.0) == (90.0, 130.0)


@pytest.mark.unit
def test_execute_disabled_by_default():
    state = {
        "company_of_interest": "BTC-USD",
        "final_rating": "Buy",
        "final_trade_decision": "**Rating**: Buy",
        "trader_investment_plan": "",
    }
    result = execute_decision(state, {"execution": {"enabled": False}})
    assert result.ok
    assert result.action == "disabled"
