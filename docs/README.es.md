<p align="center">
  <img src="../assets/TauricResearch.png" width="280" alt="TradingAgents">
  &nbsp;&nbsp;&nbsp;
  <img src="../assets/byttrade/logo_byt.svg" width="96" alt="BYTtrade">
</p>

# TradingAgents Crypto

Mesa de investigación multiagente para cripto. Analistas, un debate alcista y bajista, riesgo y un gestor de cartera llegan a Buy, Hold o Sell. Este fork envía esa decisión a un exchange con [bytx](https://github.com/byttrade/bytx) de [BYTtrade](https://byttrade.com).

[English](../README.md) | [Русский](README.ru.md) | [中文](README.zh-CN.md) | **Español** | [Português](README.pt-BR.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Türkçe](README.tr.md)

## Dos capas

La investigación sigue en TradingAgents. La ejecución la hace bytx: una llamada en Binance, Bybit, OKX, BingX, KuCoin, Bitget y más. El driver está apagado por defecto. Si lo activas, la orden va al demo del exchange hasta que elijas live.

<p align="center">
  <img src="../assets/schema.png" width="100%" alt="Mesa de agentes de TradingAgents">
</p>

<p align="center">
  <img src="../assets/byttrade/one_api.gif" width="100%" alt="Una API bytx para todos los exchanges">
</p>

| Investigación | Ejecución |
|---|---|
| Precios y noticias de Yahoo, Reddit, StockTwits | Orden a mercado, o límite post-only cerca del mercado |
| Buy y Overweight abren un long | Underweight y Sell cierran la posición |
| Hold y REVIEW no envían nada | Las acciones se omiten; solo sale cripto |
| El stop y el objetivo salen de los agentes | OKX, KuCoin, Bitget y BloFin piden passphrase |

Los diagramas vienen de [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents). Las imágenes de ejecución y la marca BYT vienen de [BYTtrade](https://byttrade.com) y [byttrade/bytx](https://github.com/byttrade/bytx).

## Quién decide

<p align="center">
  <img src="../assets/analyst.png" width="48%" alt="Analistas">
  <img src="../assets/researcher.png" width="48%" alt="Investigadores">
</p>

<p align="center">
  <img src="../assets/trader.png" width="48%" alt="Trader">
  <img src="../assets/risk.png" width="48%" alt="Riesgo y gestor de cartera">
</p>

Los analistas leen velas, indicadores y noticias. Alcistas y bajistas debaten. El trader propone la operación. El gestor de cartera fija la nota final. En cripto no corre el analista fundamental: una moneda no tiene cuentas de empresa.

## Cómo llega la orden al exchange

Un límite a menos de 20 puntos básicos del mercado sale como post-only y no cruza el spread. Un límite más lejos sigue siendo un límite normal. Sin precio de entrada, la orden es a mercado. El tamaño por defecto es 100 USDT. Sube hasta el mínimo del exchange y nunca pasa de tres veces lo pedido.

<p align="center">
  <img src="../assets/byttrade/order_book.gif" width="78%" alt="Libro de órdenes bytx">
</p>

<p align="center">
  <img src="../assets/byttrade/paper.gif" width="78%" alt="Paper trading bytx">
</p>

## Arranque

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

`BYTX_PASSWORD` es la passphrase de la API. Solo OKX, KuCoin, Bitget y BloFin la exigen. Bybit y Binance bastan con la clave y el secreto.

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

El paper no necesita claves: `config["execution"]["paper"] = True`. Esto no es asesoramiento financiero. En live se puede perder dinero.

La documentación upstream completa está en inglés: [README.md](../README.md).
