#!/usr/bin/env python3
"""
A/B Test Runner for Option Intraday Stop-Loss Methods in NewTrade.

Compares Baseline (no stoploss) against 5 option stoploss arms across 3 ETFs:
  - Baseline (Hold to 14:35)
  - opt_trailing_pct (Option Premium Trailing Stop)
  - opt_profit_lock_trailing (Option Profit-Lock Trailing Stop)
  - opt_time_decay_trailing (Option Premium Time-Decay Trailing Stop)
  - spot_trailing_pct (Underlying ETF Spot Trailing Stop)
  - spot_time_decay_trailing (Underlying ETF Spot Time-Decay Trailing Stop)

Generates tests/OPTION_STOPLOSS_AB_REPORT.md summarizing multi-arm results.
"""

import sys
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

# Path resolution
HERE = Path(__file__).resolve().parent
NEWTRADE_DIR = HERE.parent
REPO_ROOT = NEWTRADE_DIR.parent

sys.path.append(str(NEWTRADE_DIR))
sys.path.append(str(REPO_ROOT / "day-model-new"))
sys.path.append(str(REPO_ROOT / "day-model"))

from research_option_stoploss import run_option_stoploss_experiment


def run_full_option_stoploss_ab_test(etfs: list[str], scheme: str = "icw", start_date: str = "2022-01-01", end_date: str = "2026-07-20") -> str:
    """
    Executes full multi-ETF A/B test across all arms and generates markdown report.
    """
    all_experiments = []
    for etf in etfs:
        res = run_option_stoploss_experiment(etf, scheme=scheme, start_date=start_date, end_date=end_date)
        if res:
            all_experiments.append(res)

    # Generate Markdown report
    lines = []
    lines.append("# Option Intraday Stop-Loss A/B Testing Master Report\n")
    lines.append(f"**Evaluation Period**: OOS [{start_date} ~ {end_date}] | **Weighting Scheme**: `{scheme.upper()}`\n")
    lines.append("## Executive Summary\n")
    lines.append("This report benchmarks 5 option-tailored intraday stop-loss strategies against the baseline (holding position to 14:35 close) across capital-constrained option portfolios (100k RMB starting capital, 10% capital per trade, nearest OTM contracts).\n")

    # Table per ETF
    for exp in all_experiments:
        etf = exp["etf"]
        summary = exp["summary"]
        df_sum = pd.DataFrame(summary)

        lines.append(f"### {etf} Performance Comparison\n")
        lines.append("| Strategy Arm | Train Param | OOS Sharpe | Sharpe Lift | Net PnL (RMB) | Max DD (%) | Win Rate (%) | Stop Hit Rate (%) | DSR p-val |")
        lines.append("|---|---|---|---|---|---|---|---|---|")

        for _, row in df_sum.iterrows():
            m_name = row["method"]
            t_param = f"{row['train_param']:.4f}".rstrip("0").rstrip(".") if row["train_param"] > 0 else "N/A"
            sharpe_str = f"**{row['oos_sharpe']:.3f}**" if row["sharpe_lift"] > 0 else f"{row['oos_sharpe']:.3f}"
            lift_str = f"**{row['sharpe_lift']:+.3f}**" if row["sharpe_lift"] > 0 else f"{row['sharpe_lift']:+.3f}"
            pnl_str = f"{row['oos_pnl_rmb']:+,.0f}"
            
            lines.append(f"| `{m_name}` | `{t_param}` | {sharpe_str} | {lift_str} | {pnl_str} | {row['oos_max_dd_pct']:.2f}% | {row['oos_win_rate_pct']:.1f}% | {row['oos_stop_trig_pct']:.1f}% | `{row['dsr_pvalue']:.3f}` |")

        lines.append("\n")

    # Overall Recommendation
    lines.append("## Cross-ETF Synthesis & Recommendations\n")
    
    # Calculate average Sharpe lift per method across all ETFs
    arm_metrics = {}
    for exp in all_experiments:
        for row in exp["summary"]:
            m = row["method"]
            if m not in arm_metrics:
                arm_metrics[m] = {"lifts": [], "pnls": [], "max_dds": []}
            arm_metrics[m]["lifts"].append(row["sharpe_lift"])
            arm_metrics[m]["pnls"].append(row["oos_pnl_rmb"])
            arm_metrics[m]["max_dds"].append(row["oos_max_dd_pct"])

    lines.append("| Strategy Arm | Avg Sharpe Lift | Avg Net PnL (RMB) | Avg Max DD (%) | Strategy Recommendation |")
    lines.append("|---|---|---|---|---|")

    for m, data in arm_metrics.items():
        avg_lift = float(np.mean(data["lifts"]))
        avg_pnl = float(np.mean(data["pnls"]))
        avg_dd = float(np.mean(data["max_dds"]))
        status = "**Recommended**" if avg_lift > 0.05 else ("Viable" if avg_lift > 0 else "Not Recommended")
        lines.append(f"| `{m}` | `{avg_lift:+.3f}` | `{avg_pnl:+,.0f}` | `{avg_dd:.2f}%` | {status} |")

    report_content = "\n".join(lines)
    report_path = HERE / "OPTION_STOPLOSS_AB_REPORT.md"
    report_path.write_text(report_content, encoding="utf-8")
    print(f"\nSaved master A/B report to {report_path}")
    return report_content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Option Stop-Loss A/B Test Runner")
    parser.add_argument("--scheme", type=str, default="icw")
    parser.add_argument("--start-date", type=str, default="2022-01-01")
    parser.add_argument("--end-date", type=str, default="2026-07-20")
    args = parser.parse_args()

    etfs = ["300ETF", "500ETF", "159915ETF"]
    run_full_option_stoploss_ab_test(etfs, scheme=args.scheme, start_date=args.start_date, end_date=args.end_date)
