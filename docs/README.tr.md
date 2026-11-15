<p align="center">
  <img src="../assets/TauricResearch.png" width="280" alt="TradingAgents">
  &nbsp;&nbsp;&nbsp;
  <img src="../assets/byttrade/logo_byt.svg" width="96" alt="BYTtrade">
</p>

# TradingAgents Crypto

Kripto için çok ajanlı bir araştırma masası. Analistler, boğa ve ayı tartışması, risk ve portföy yöneticisi Buy, Hold veya Sell kararında buluşur. Bu fork kararı [BYTtrade](https://byttrade.com) ürünü [bytx](https://github.com/byttrade/bytx) ile borsaya gönderir.

[English](../README.md) | [Русский](README.ru.md) | [中文](README.zh-CN.md) | [Español](README.es.md) | [Português](README.pt-BR.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | **Türkçe**

## İki katman

Araştırma TradingAgents'te kalır. Emri bytx gönderir: Binance, Bybit, OKX, BingX, KuCoin, Bitget ve diğerlerinde tek çağrı. Sürücü varsayılan olarak kapalıdır. Açılınca emir, siz live seçene kadar borsanın demosuna gider.

<p align="center">
  <img src="../assets/schema.png" width="100%" alt="TradingAgents ajan masası">
</p>

<p align="center">
  <img src="../assets/byttrade/one_api.gif" width="100%" alt="Tüm borsalar için tek bytx API">
</p>

| Araştırma | Emir |
|---|---|
| Yahoo fiyat ve haber, Reddit, StockTwits | Piyasa emri ya da piyasaya yakın post-only limit |
| Buy ve Overweight long açar | Underweight ve Sell pozisyonu kapatır |
| Hold ve REVIEW hiçbir şey göndermez | Hisseler atlanır; yalnızca kripto gider |
| Stop ve hedef ajanların kararından gelir | OKX, KuCoin, Bitget ve BloFin passphrase ister |

Şemalar [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) kaynağındandır. Emir görüntüleri ve BYT işareti [BYTtrade](https://byttrade.com) ile [byttrade/bytx](https://github.com/byttrade/bytx) kaynağındandır.

## Kararı kim verir

<p align="center">
  <img src="../assets/analyst.png" width="48%" alt="Analistler">
  <img src="../assets/researcher.png" width="48%" alt="Araştırmacılar">
</p>

<p align="center">
  <img src="../assets/trader.png" width="48%" alt="Trader">
  <img src="../assets/risk.png" width="48%" alt="Risk ve portföy yöneticisi">
</p>

Analistler mum, gösterge ve haber okur. Boğalar ve ayılar tartışır. Trader işlemi önerir. Portföy yöneticisi son notu koyar. Kriptoda temel analiz ajanı çalışmaz: bir coinin şirket bilançosu yoktur.

## Emir borsaya nasıl varır

Piyasaya 20 baz puan içindeki limit post-only gider ve spreadi kesmez. Daha uzak limit normal limit kalır. Giriş fiyatı yoksa emir piyasadandır. Varsayılan büyüklük 100 USDT'dir. Borsa minimumuna çıkar ve istediğiniz büyüklüğün üç katını geçmez.

<p align="center">
  <img src="../assets/byttrade/order_book.gif" width="78%" alt="bytx emir defteri">
</p>

<p align="center">
  <img src="../assets/byttrade/paper.gif" width="78%" alt="bytx paper trading">
</p>

## Çalıştırma

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

`BYTX_PASSWORD` API passphrase'idir. Yalnızca OKX, KuCoin, Bitget ve BloFin ister. Bybit ve Binance için anahtar ve secret yeter.

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

Paper anahtar istemez: `config["execution"]["paper"] = True`. Bu finansal tavsiye değildir. Live işlemde para kaybedilebilir.

Upstream belgelerinin tamamı İngilizcedir: [README.md](../README.md).
