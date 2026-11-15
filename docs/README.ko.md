<p align="center">
  <img src="../assets/TauricResearch.png" width="280" alt="TradingAgents">
  &nbsp;&nbsp;&nbsp;
  <img src="../assets/byttrade/logo_byt.svg" width="96" alt="BYTtrade">
</p>

# TradingAgents Crypto

암호화폐용 멀티에이전트 리서치 데스크입니다. 애널리스트, 강세와 약세 토론, 리스크, 포트폴리오 매니저가 Buy, Hold, Sell로 모입니다. 이 포크는 그 결정을 [BYTtrade](https://byttrade.com)의 [bytx](https://github.com/byttrade/bytx)로 거래소에 보냅니다.

[English](../README.md) | [Русский](README.ru.md) | [中文](README.zh-CN.md) | [Español](README.es.md) | [Português](README.pt-BR.md) | [日本語](README.ja.md) | **한국어** | [Türkçe](README.tr.md)

## 두 층

리서치는 TradingAgents에 남습니다. 체결은 bytx입니다. Binance, Bybit, OKX, BingX, KuCoin, Bitget 등을 같은 호출로 다룹니다. 드라이버는 기본적으로 꺼져 있습니다. 켜면 live를 고르기 전까지 주문은 거래소 demo로 갑니다.

<p align="center">
  <img src="../assets/schema.png" width="100%" alt="TradingAgents 에이전트">
</p>

<p align="center">
  <img src="../assets/byttrade/one_api.gif" width="100%" alt="모든 거래소를 위한 하나의 bytx API">
</p>

| 리서치 | 체결 |
|---|---|
| Yahoo 가격과 뉴스, Reddit, StockTwits | 시장가, 또는 시세에 가까운 post-only 지정가 |
| Buy와 Overweight는 롱을 연다 | Underweight와 Sell은 포지션을 닫는다 |
| Hold와 REVIEW는 아무것도 보내지 않는다 | 주식은 건너뛰고 암호화폐만 보낸다 |
| 손절과 목표는 에이전트 판단에서 온다 | OKX, KuCoin, Bitget, BloFin은 passphrase가 필요하다 |

도식은 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)에서 가져왔습니다. 체결 화면과 BYT 마크는 [BYTtrade](https://byttrade.com)와 [byttrade/bytx](https://github.com/byttrade/bytx)의 것입니다.

## 누가 결정하는가

<p align="center">
  <img src="../assets/analyst.png" width="48%" alt="애널리스트">
  <img src="../assets/researcher.png" width="48%" alt="리서처">
</p>

<p align="center">
  <img src="../assets/trader.png" width="48%" alt="트레이더">
  <img src="../assets/risk.png" width="48%" alt="리스크와 포트폴리오 매니저">
</p>

애널리스트는 캔들, 지표, 뉴스를 읽습니다. 강세와 약세가 토론합니다. 트레이더가 거래를 제안하고, 포트폴리오 매니저가 최종 등급을 정합니다. 암호화폐에서는 펀더멘털 애널리스트가 돌지 않습니다. 코인에는 회사 실적이 없습니다.

## 주문이 거래소에 닿기까지

시세에서 20bp 이내의 지정가는 post-only로 나가 스프레드를 넘지 않습니다. 더 먼 지정가는 일반 지정가로 남습니다. 진입가가 없으면 시장가입니다. 기본 크기는 100 USDT입니다. 거래소 최소 수량까지 올리고, 요청한 크기의 세 배를 넘지 않습니다.

<p align="center">
  <img src="../assets/byttrade/order_book.gif" width="78%" alt="bytx 호가">
</p>

<p align="center">
  <img src="../assets/byttrade/paper.gif" width="78%" alt="bytx 페이퍼 트레이딩">
</p>

## 실행

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

`BYTX_PASSWORD`는 API passphrase입니다. OKX, KuCoin, Bitget, BloFin만 필요합니다. Bybit와 Binance는 키와 시크릿이면 됩니다.

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

페이퍼는 키가 필요 없습니다. `config["execution"]["paper"] = True`. 투자 조언이 아닙니다. 라이브에서는 손실이 날 수 있습니다.

업스트림 전문은 영어입니다: [README.md](../README.md).
