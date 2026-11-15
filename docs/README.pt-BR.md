<p align="center">
  <img src="../assets/TauricResearch.png" width="280" alt="TradingAgents">
  &nbsp;&nbsp;&nbsp;
  <img src="../assets/byttrade/logo_byt.svg" width="96" alt="BYTtrade">
</p>

# TradingAgents Crypto

Mesa de pesquisa multiagente para cripto. Analistas, um debate de alta e de baixa, risco e um gestor de carteira chegam a Buy, Hold ou Sell. Este fork envia a decisão à corretora pelo [bytx](https://github.com/byttrade/bytx) da [BYTtrade](https://byttrade.com).

[English](../README.md) | [Русский](README.ru.md) | [中文](README.zh-CN.md) | [Español](README.es.md) | **Português** | [日本語](README.ja.md) | [한국어](README.ko.md) | [Türkçe](README.tr.md)

## Duas camadas

A pesquisa continua no TradingAgents. A execução é do bytx: uma chamada na Binance, Bybit, OKX, BingX, KuCoin, Bitget e outras. O driver fica desligado por padrão. Ligado, a ordem vai para o demo da corretora até você escolher live.

<p align="center">
  <img src="../assets/schema.png" width="100%" alt="Mesa de agentes do TradingAgents">
</p>

<p align="center">
  <img src="../assets/byttrade/one_api.gif" width="100%" alt="Uma API bytx para todas as corretoras">
</p>

| Pesquisa | Execução |
|---|---|
| Preços e notícias da Yahoo, Reddit, StockTwits | Ordem a mercado, ou limite post-only perto do mercado |
| Buy e Overweight abrem um long | Underweight e Sell fecham a posição |
| Hold e REVIEW não enviam nada | Ações são ignoradas; só cripto segue |
| Stop e alvo vêm dos agentes | OKX, KuCoin, Bitget e BloFin pedem passphrase |

Os diagramas vêm de [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents). As imagens de execução e a marca BYT vêm da [BYTtrade](https://byttrade.com) e de [byttrade/bytx](https://github.com/byttrade/bytx).

## Quem decide

<p align="center">
  <img src="../assets/analyst.png" width="48%" alt="Analistas">
  <img src="../assets/researcher.png" width="48%" alt="Pesquisadores">
</p>

<p align="center">
  <img src="../assets/trader.png" width="48%" alt="Trader">
  <img src="../assets/risk.png" width="48%" alt="Risco e gestor de carteira">
</p>

Os analistas leem candles, indicadores e notícias. Altistas e baixistas debatem. O trader propõe a operação. O gestor de carteira define a nota final. Em cripto o analista fundamental não roda: uma moeda não tem balanço de empresa.

## Como a ordem chega à corretora

Um limite a menos de 20 pontos-base do mercado sai como post-only e não cruza o spread. Um limite mais longe continua normal. Sem preço de entrada, a ordem é a mercado. O tamanho padrão é 100 USDT. Ele sobe até o mínimo da corretora e nunca passa de três vezes o valor pedido.

<p align="center">
  <img src="../assets/byttrade/order_book.gif" width="78%" alt="Livro de ofertas bytx">
</p>

<p align="center">
  <img src="../assets/byttrade/paper.gif" width="78%" alt="Paper trading bytx">
</p>

## Como rodar

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

`BYTX_PASSWORD` é a passphrase da API. Só OKX, KuCoin, Bitget e BloFin exigem. Bybit e Binance usam a chave e o segredo.

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

Paper não precisa de chaves: `config["execution"]["paper"] = True`. Isto não é recomendação financeira. No live dá para perder dinheiro.

A documentação upstream completa está em inglês: [README.md](../README.md).
