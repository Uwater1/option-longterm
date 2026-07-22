"""
Central registry of admitted feature pools across all ETFs and trading sides for Day-Model Rewrite v3.
Serves as the single source of truth for downstream execution and models.
"""

POOLS = {
    "300ETF": {
        "single": [
            {
                "feature_name": "combo_ifelse__gap_pct__max_up_ret__option_oi_growth",
                "sign": 1,
                "overall_ic": 0.24751555615534512,
                "deflated_ic": 0.10218504739356571,
                "ic_ir": 0.6849694030175358,
                "monotonicity": 0.7401759530791789,
                "recipe": {
                    "op": "ifelse",
                    "feature_cond": "gap_pct",
                    "feature_a": "max_up_ret",
                    "feature_b": "option_oi_growth"
                }
            },
            {
                "feature_name": "combo_ifelse__gap_pct__first_bar_return__short_sell_cover_spread",
                "sign": 1,
                "overall_ic": 0.24026403647904546,
                "deflated_ic": 0.09493352771726604,
                "ic_ir": 0.5227518729836941,
                "monotonicity": 0.7008797653958945,
                "recipe": {
                    "op": "ifelse",
                    "feature_cond": "gap_pct",
                    "feature_a": "first_bar_return",
                    "feature_b": "short_sell_cover_spread"
                }
            },
            {
                "feature_name": "combo_ifelse__gap_pct__first_bar_return__growth_momentum_ratio",
                "sign": 1,
                "overall_ic": 0.21060498263558589,
                "deflated_ic": 0.06527447387380647,
                "ic_ir": 0.6420713424835212,
                "monotonicity": 0.718475073313783,
                "recipe": {
                    "op": "ifelse",
                    "feature_cond": "gap_pct",
                    "feature_a": "first_bar_return",
                    "feature_b": "growth_momentum_ratio"
                }
            },
            {
                "feature_name": "combo_max__max_up_ret__first_bar_return",
                "sign": 1,
                "overall_ic": 0.1950445128779248,
                "deflated_ic": 0.04971400411614538,
                "ic_ir": 0.6338466263797919,
                "monotonicity": 0.7231671554252199,
                "recipe": {
                    "op": "max",
                    "feature_a": "max_up_ret",
                    "feature_b": "first_bar_return"
                }
            }
        ],
        "long": [],
        "short": []
    },
    "50ETF": {
        "single": [],
        "long": [],
        "short": []
    },
    "500ETF": {
        "single": [
            {
                "feature_name": "max_up_ret",
                "sign": 1,
                "overall_ic": 0.24996371957717006,
                "deflated_ic": 0.11431174579152262,
                "ic_ir": 0.7453776715531585,
                "monotonicity": 0.7788856304985338
            },
            {
                "feature_name": "total_balance",
                "sign": -1,
                "overall_ic": 0.17731478442465665,
                "deflated_ic": 0.0416628106390092,
                "ic_ir": 0.6015474514944631,
                "monotonicity": 0.7225806451612903
            }
        ],
        "long": [],
        "short": []
    },
    "588000ETF": {
        "single": [
            {
                "feature_name": "combo_rank_max__first_30min_return__volume_weighted_price_position",
                "sign": 1,
                "overall_ic": 0.27963286649098,
                "deflated_ic": 0.2795134452320513,
                "ic_ir": 0.9316781821635415,
                "monotonicity": 0.8193484698914116,
                "recipe": {
                    "op": "rank_max",
                    "feature_a": "first_30min_return",
                    "feature_b": "volume_weighted_price_position"
                }
            },
            {
                "feature_name": "max_up_ret",
                "sign": 1,
                "overall_ic": 0.1934996544494661,
                "deflated_ic": 0.19338354973585473,
                "ic_ir": 0.6050890044419849,
                "monotonicity": 0.7265547877591313
            },
            {
                "feature_name": "vix_rolling_percentile_60d",
                "sign": 1,
                "overall_ic": 0.19119057706837445,
                "deflated_ic": 0.19232172124799546,
                "ic_ir": 0.337899900519694,
                "monotonicity": 0.6288252714708786
            }
        ],
        "long": [
            {
                "feature_name": "body_to_range_ratio",
                "sign": 1,
                "overall_ic": 0.2756258937138496,
                "deflated_ic": 0.06860857757582242,
                "ic_ir": 0.32148686110927105,
                "monotonicity": 0.6377097729516288
            }
        ],
        "short": []
    },
    "159915ETF": {
        "single": [
            {
                "feature_name": "yesterday_afternoon_momentum",
                "sign": -1,
                "overall_ic": 0.22286535147108438,
                "deflated_ic": 0.0879530022394861,
                "ic_ir": 0.6290455039242624,
                "monotonicity": 0.7008797653958945
            },
            {
                "feature_name": "max_up_ret",
                "sign": 1,
                "overall_ic": 0.20650868962298052,
                "deflated_ic": 0.07159634039138224,
                "ic_ir": 0.5608215981336928,
                "monotonicity": 0.7038123167155426
            }
        ],
        "long": [],
        "short": []
    }
}

def get_admitted_pool(etf: str, side: str) -> list:
    """Retrieve the list of admitted feature dictionaries for a specific ETF and side."""
    return POOLS.get(etf, {}).get(side, [])
