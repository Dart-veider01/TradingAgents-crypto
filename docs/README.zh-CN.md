<p align="center">
  <img src="../assets/TauricResearch.png" width="280" alt="TradingAgents">
  &nbsp;&nbsp;&nbsp;
  <img src="../assets/byttrade/logo_byt.svg" width="96" alt="BYTtrade">
</p>

# TradingAgents Crypto

面向加密资产的多智能体研究台。分析师、多空辩论、风险和组合经理给出 Buy、Hold 或 Sell。这个分支通过 [BYTtrade](https://byttrade.com) 的 [bytx](https://github.com/byttrade/bytx) 把决定发到交易所。

[English](../README.md) | [Русский](README.ru.md) | **中文** | [Español](README.es.md) | [Português](README.pt-BR.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Türkçe](README.tr.md)

## 两层

研究仍由 TradingAgents 完成。执行由 bytx 完成：Binance、Bybit、OKX、BingX、KuCoin、Bitget 等交易所使用同一次调用。驱动默认关闭。打开后，订单进入交易所 demo，直到你自己选择 live。

<p align="center">
  <img src="../assets/schema.png" width="100%" alt="TradingAgents 智能体">
</p>

<p align="center">
  <img src="../assets/byttrade/one_api.gif" width="100%" alt="bytx 统一接口">
</p>

| 研究 | 执行 |
|---|---|
| Yahoo 价格和新闻、Reddit、StockTwits | 市价单，或贴近市价的 post-only 限价单 |
| Buy 和 Overweight 开多 | Underweight 和 Sell 平仓 |
| Hold 和 REVIEW 不发单 | 股票会被跳过，只发送加密资产 |
| 止损和目标来自智能体 | OKX、KuCoin、Bitget、BloFin 需要 passphrase |

架构图来自 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)。执行画面和 BYT 标志来自 [BYTtrade](https://byttrade.com) 与 [byttrade/bytx](https://github.com/byttrade/bytx)。

## 谁做决定

<p align="center">
  <img src="../assets/analyst.png" width="48%" alt="分析师">
  <img src="../assets/researcher.png" width="48%" alt="研究员">
</p>

<p align="center">
  <img src="../assets/trader.png" width="48%" alt="交易员">
  <img src="../assets/risk.png" width="48%" alt="风险与组合经理">
</p>

分析师阅读 K 线、指标和新闻。多头和空头辩论。交易员提出交易。组合经理给出最终评级。加密资产不运行基本面分析师：代币没有公司财报。

## 订单如何到达交易所

距离市价 20 个基点以内的限价单以 post-only 发送，不会吃掉价差。更远的限价单保持普通限价。没有入场价时下市价单。默认名义金额为 100 USDT，会抬到交易所最小量，但不会超过你所填金额的三倍。

<p align="center">
  <img src="../assets/byttrade/order_book.gif" width="78%" alt="bytx 订单簿">
</p>

<p align="center">
  <img src="../assets/byttrade/paper.gif" width="78%" alt="bytx 模拟交易">
</p>

## 运行

```bash
pip install ".[bytx]"
```

```env
BYTX_API_KEY=
BYTX_SECRET=
BYTX_PASSWORD=
BYTX_EXCHANGE=bybit
TRADINGAGENTS_EXECUTION_ENABLED=true
TRADINGAGENTS_EXECUTION_DEMO=true
TRADINGAGENTS_EXECUTION_NOTIONAL=100
```

`BYTX_PASSWORD` 是 API passphrase。只有 OKX、KuCoin、Bitget 和 BloFin 需要它。Bybit 和 Binance 只需要 key 和 secret。

```bash
tradingagents --ticker BTC-USD --execute
```

```python
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

config = DEFAULT_CONFIG.copy()
config["execution"]["enabled"] = True
config["execution"]["demo"] = True

ta = TradingAgentsGraph(debug=True, config=config)
state, decision = ta.propagate("BTC-USD", "2026-11-14", asset_type="crypto")
print(decision, state.get("execution_result"))
```

Paper 不需要密钥：`config["execution"]["paper"] = True`。这不是投资建议。实盘可能亏损。

完整的英文上游文档：[README.md](../README.md)。
