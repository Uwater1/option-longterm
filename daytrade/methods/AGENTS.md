# Daytrade Execution Methods

Isolated research module evaluating trade execution variants for `daytrade` signals.

## Commands

```bash
source venv/bin/activate
python3 -m daytrade.methods.download_futures_data   # Download CFFEX index futures 5m data
python3 -m daytrade.methods.eval_execution          # Run comparative execution evaluation
```

## Structure & Scripts

```
daytrade/methods/
├── __init__.py                # Package marker (isolated research module)
├── AGENTS.md                  # Workflow & script guide
├── download_futures_data.py   # Futures 5m downloader via rqdatac
├── cost_model.py              # Transaction cost & slippage models
├── option_pricing.py          # Intraday option pricer (BS & real 5m quotes)
├── eval_execution.py          # Multi-instrument backtest engine
└── report.py                  # Comparative report generator
```

## Execution Variants Evaluated
- **Direct ETF**: Long/Short ETF (15bp baseline cost).
- **Index Futures**: IH (50ETF), IF (300ETF), IC/IM (500ETF). High leverage (~7x-10x), low friction.
- **Naked Options**: Buy OTM1 Call / Put. 2 RMB comm + 2 RMB slip per leg.
- **Vertical Spreads**: Bull Call / Bear Put debit spread (OTM1 buy + OTM2 sell). Defined risk, no margin requirement.

## Rules & Constraints
- Zero reverse imports into `daytrade/` core scripts or root workspace files.
