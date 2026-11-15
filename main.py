from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

# DEFAULT_CONFIG already applies TRADINGAGENTS_* env-var overrides
# (llm_provider, deep_think_llm, quick_think_llm, backend_url, etc.),
# so users can switch models or endpoints purely via .env without
# editing this script. Override individual keys here only when you
# want a hard-coded value that should ignore the environment.
config = DEFAULT_CONFIG.copy()

# Optional: send the final crypto decision to bytx (demo by default).
# Requires: pip install bytx  and BYTX_API_KEY / BYTX_SECRET in .env
# config["execution"]["enabled"] = True
# config["execution"]["demo"] = True
# config["execution"]["exchange"] = "bybit"
# config["execution"]["notional_usdt"] = 100

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate (use a crypto ticker when testing execution)
_, decision = ta.propagate("NVDA", "2026-09-01")
print(decision)
