"""
compare_alpha_phases.py — Cross-phase comparison report
========================================================
Reads the three validate_pnl_phaseN.json files and the Phase 1 statistical
JSON, then prints a per-ETF-per-regime comparison and writes a markdown summary
to backtest/alpha_phase_comparison.md.

Picks the best deployable phase per (ETF, regime); falls back to static filter
if no phase clears the deployability bar.
"""

import json
import os

ETFS = ["50", "300", "500"]
REGIMES = ["reg1", "reg2", "reg3", "reg4"]
REG_NAMES = {"reg1": "ST Fall", "reg2": "MT Fall", "reg3": "ST Crash", "reg4": "MT Crash"}
REG_CRASH = {"reg1": False, "reg2": False, "reg3": True, "reg4": True}


def load_phase(phase):
    path = f"backtest/validate_pnl_phase{phase}.json"
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def load_stat():
    path = "backtest/alpha_put_models.json"
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def main():
    p1, p2, p3 = load_phase(1), load_phase(2), load_phase(3)
    stat = load_stat()

    lines = []
    lines.append("# Alpha Model — Cross-Phase Comparison (OOS Put P&L)\n")
    lines.append("Cadence = cycle (monthly cycle start, fair vs baselines). OOS years >= 2021.\n")
    lines.append("`DEPLOY` = phase beats static filter on net P&L AND Sharpe>0 AND per-trigger>0.\n")
    lines.append("Statistical column: Phase 1 walk-forward OOS (lift for crash / mean_ret for fall).\n")

    header = (f"| ETF | Regime | Stat OOS | "
              f"P1 netPnL (N) | P2 netPnL (N) | P3 netPnL (N) | "
              f"Static netPnL (N) | **WINNER** |")
    sep = "|" + "---|" * 8
    lines.append(header)
    lines.append(sep)

    for etf in ETFS:
        for r in REGIMES:
            cell_p1 = p1.get(etf, {}).get(r, {})
            cell_p2 = p2.get(etf, {}).get(r, {})
            cell_p3 = p3.get(etf, {}).get(r, {})
            stat_cell = stat.get(etf, {}).get(r, {}).get("metrics", {})

            def fmt(c):
                if not c:
                    return "—"
                a = c.get("alpha", {})
                dep = c.get("deployable", False)
                mark = " ✅" if dep else ""
                n = a.get("n", 0)
                net = a.get("net_pnl", 0.0)
                return f"{net:+.0f} ({n}){mark}"

            static = cell_p3.get("baseline_static_filter", cell_p1.get("baseline_static_filter", {}))
            static_str = f"{static.get('net_pnl', 0):+.0f} ({static.get('n', 0)})" if static else "—"

            # Stat OOS
            raw = stat_cell.get("mean_oos_raw", 0)
            ci_lo = stat_cell.get("oos_ci_low", 0)
            unit = f"{raw:.2f}x" if REG_CRASH[r] else f"{raw*100:+.2f}%"
            stat_str = f"{unit} [CI {ci_lo:.2f}]"

            # Winner: deployable phase with highest net P&L; else static.
            candidates = []
            for ph, c in [(1, cell_p1), (2, cell_p2), (3, cell_p3)]:
                if c.get("deployable"):
                    candidates.append((ph, c["alpha"]["net_pnl"]))
            if candidates:
                candidates.sort(key=lambda x: -x[1])
                winner = f"Phase {candidates[0][0]} ✅"
            else:
                winner = "static filter (no alpha edge)"

            lines.append(f"| {etf} | {REG_NAMES[r]} | {stat_str} | "
                         f"{fmt(cell_p1)} | {fmt(cell_p2)} | {fmt(cell_p3)} | "
                         f"{static_str} | {winner} |")

    md = "\n".join(lines) + "\n"
    out = "backtest/alpha_phase_comparison.md"
    os.makedirs("backtest", exist_ok=True)
    with open(out, "w") as f:
        f.write(md)
    print(md)
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
