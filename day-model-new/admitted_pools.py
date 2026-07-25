"""
Central registry of admitted feature pools across all ETFs and trading sides for Day-Model Rewrite v3.
Serves as the single source of truth for downstream execution and models.
"""

POOLS = {
    "300ETF": {
        "single": [
            {
                "feature_name": "combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0",
                "sign": 1,
                "overall_ic": 0.29490969371122033,
                "deflated_ic": 0.2949530200687909,
                "ic_ir": 0.7631529175656666,
                "monotonicity": 0.7278592375366569,
                "recipe": {
                    "op": "tri_min",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "max_up_ret",
                    "feature_c": "bar_body_rng_0"
                }
            },
            {
                "feature_name": "combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret",
                "sign": 1,
                "overall_ic": 0.293874629109404,
                "deflated_ic": 0.2938955025722574,
                "ic_ir": 0.5738193504355892,
                "monotonicity": 0.7126099706744868,
                "recipe": {
                    "op": "rank_min",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "max_up_ret"
                }
            },
            {
                "feature_name": "combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret",
                "sign": 1,
                "overall_ic": 0.2659682075409771,
                "deflated_ic": 0.26583076524306315,
                "ic_ir": 0.6108586752936174,
                "monotonicity": 0.7002932551319648,
                "recipe": {
                    "op": "mean",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "max_up_ret"
                }
            },
            {
                "feature_name": "combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_sentiment",
                "sign": 1,
                "overall_ic": 0.23860517130709885,
                "deflated_ic": 0.2386841065260558,
                "ic_ir": 0.5427975333615599,
                "monotonicity": 0.6903225806451613,
                "recipe": {
                    "op": "tri_median",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "bar_body_rng_0",
                    "feature_c": "first_bar_sentiment"
                }
            },
            {
                "feature_name": "rbreaker_sell_setup_proximity_early",
                "sign": 1,
                "overall_ic": 0.22943301912845318,
                "deflated_ic": 0.22989033212837187,
                "ic_ir": 0.5549579561217975,
                "monotonicity": 0.7413489736070381
            },
            {
                "feature_name": "combo_rank_min__star50_limit_proximity_early__bar_body_rng_0",
                "sign": 1,
                "overall_ic": 0.22665522235145696,
                "deflated_ic": 0.22646187402263063,
                "ic_ir": 0.5951699995022809,
                "monotonicity": 0.6697947214076246,
                "recipe": {
                    "op": "rank_min",
                    "feature_a": "star50_limit_proximity_early",
                    "feature_b": "bar_body_rng_0"
                }
            },
            {
                "feature_name": "combo_z_sum__max_up_ret__volume_weighted_price_position",
                "sign": 1,
                "overall_ic": 0.21243120869659468,
                "deflated_ic": 0.2110872496152803,
                "ic_ir": 0.6660478982234405,
                "monotonicity": 0.7395894428152493,
                "recipe": {
                    "op": "z_sum",
                    "feature_a": "max_up_ret",
                    "feature_b": "volume_weighted_price_position"
                }
            },
            {
                "feature_name": "combo_product__rbreaker_sell_setup_proximity_early__max_up_ret",
                "sign": 1,
                "overall_ic": 0.2042078523984789,
                "deflated_ic": 0.2034005533705841,
                "ic_ir": 0.4801542559788733,
                "monotonicity": 0.6346041055718475,
                "recipe": {
                    "op": "product",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "max_up_ret"
                }
            },
            {
                "feature_name": "combo_ratio__limit_down_proximity_early__volume_concentration",
                "sign": 1,
                "overall_ic": 0.1928046395679181,
                "deflated_ic": 0.19349947945326954,
                "ic_ir": 0.6002637237827422,
                "monotonicity": 0.7348973607038123,
                "recipe": {
                    "op": "ratio",
                    "feature_a": "limit_down_proximity_early",
                    "feature_b": "volume_concentration"
                }
            },
            {
                "feature_name": "combo_ratio__first_bar_sentiment__volume_surge_direction",
                "sign": 1,
                "overall_ic": 0.12770488457329465,
                "deflated_ic": 0.12779929449993463,
                "ic_ir": 0.6294578480307299,
                "monotonicity": 0.7454545454545455,
                "recipe": {
                    "op": "ratio",
                    "feature_a": "first_bar_sentiment",
                    "feature_b": "volume_surge_direction"
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
                "feature_name": "combo_tri_median__rbreaker_sell_setup_proximity_early__close_vs_open_range__first_bar_sentiment",
                "sign": 1,
                "overall_ic": 0.31896336778633083,
                "deflated_ic": 0.3180562191362472,
                "ic_ir": 0.8001489347063341,
                "monotonicity": 0.7788856304985338,
                "recipe": {
                    "op": "tri_median",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "close_vs_open_range",
                    "feature_c": "first_bar_sentiment"
                }
            },
            {
                "feature_name": "combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration",
                "sign": 1,
                "overall_ic": 0.327824696808812,
                "deflated_ic": 0.327261415263403,
                "ic_ir": 0.7514438562805872,
                "monotonicity": 0.7624633431085044,
                "recipe": {
                    "op": "rel_diff",
                    "feature_a": "star50_limit_proximity_early",
                    "feature_b": "volume_weighted_momentum_acceleration"
                }
            },
            {
                "feature_name": "combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__close_vs_open_range",
                "sign": 1,
                "overall_ic": 0.2937042504438518,
                "deflated_ic": 0.293482304255924,
                "ic_ir": 1.053489742134534,
                "monotonicity": 0.8287390029325513,
                "recipe": {
                    "op": "tri_mean",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "max_up_ret",
                    "feature_c": "close_vs_open_range"
                }
            },
            {
                "feature_name": "combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment",
                "sign": 1,
                "overall_ic": 0.34346882618715985,
                "deflated_ic": 0.3430002220826533,
                "ic_ir": 1.05293856587096,
                "monotonicity": 0.8357771260997068,
                "recipe": {
                    "op": "tri_min",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "max_up_ret",
                    "feature_c": "first_bar_sentiment"
                }
            },
            {
                "feature_name": "combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0",
                "sign": 1,
                "overall_ic": 0.3072164119144839,
                "deflated_ic": 0.3071452869721479,
                "ic_ir": 0.6261520711336281,
                "monotonicity": 0.7313782991202346,
                "recipe": {
                    "op": "rank_min",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "bar_ret_0"
                }
            },
            {
                "feature_name": "combo_rel_diff__max_up_ret__late_bar_momentum",
                "sign": 1,
                "overall_ic": 0.2751890773506337,
                "deflated_ic": 0.2745978054083703,
                "ic_ir": 0.9765411225804081,
                "monotonicity": 0.7777126099706745,
                "recipe": {
                    "op": "rel_diff",
                    "feature_a": "max_up_ret",
                    "feature_b": "late_bar_momentum"
                }
            },
            {
                "feature_name": "combo_sig_product__max_up_ret__close_vs_open_range",
                "sign": 1,
                "overall_ic": 0.2835103906353759,
                "deflated_ic": 0.28320396476334225,
                "ic_ir": 0.8379681433887454,
                "monotonicity": 0.7607038123167156,
                "recipe": {
                    "op": "sig_product",
                    "feature_a": "max_up_ret",
                    "feature_b": "close_vs_open_range"
                }
            },
            {
                "feature_name": "combo_min__star50_limit_proximity_early__max_down_ret",
                "sign": 1,
                "overall_ic": 0.2590514643892672,
                "deflated_ic": 0.2585921490731544,
                "ic_ir": 0.7790387550067208,
                "monotonicity": 0.7618768328445747,
                "recipe": {
                    "op": "min",
                    "feature_a": "star50_limit_proximity_early",
                    "feature_b": "max_down_ret"
                }
            },
            {
                "feature_name": "combo_rank_max__first_bar_sentiment__max_down_ret",
                "sign": 1,
                "overall_ic": 0.26563604629878323,
                "deflated_ic": 0.2648648579678612,
                "ic_ir": 0.6328204612688342,
                "monotonicity": 0.7313782991202346,
                "recipe": {
                    "op": "rank_max",
                    "feature_a": "first_bar_sentiment",
                    "feature_b": "max_down_ret"
                }
            },
            {
                "feature_name": "combo_clamp_diff__first_bar_return__demark_setup_reversal_early",
                "sign": 1,
                "overall_ic": 0.30277879159528526,
                "deflated_ic": 0.30222071554515484,
                "ic_ir": 0.7520384764986776,
                "monotonicity": 0.7653958944281525,
                "recipe": {
                    "op": "clamp_diff",
                    "feature_a": "first_bar_return",
                    "feature_b": "demark_setup_reversal_early"
                }
            },
            {
                "feature_name": "combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration",
                "sign": 1,
                "overall_ic": 0.31769451604786136,
                "deflated_ic": 0.31747296729876545,
                "ic_ir": 0.896500528340376,
                "monotonicity": 0.7964809384164223,
                "recipe": {
                    "op": "clamp_diff",
                    "feature_a": "max_up_ret",
                    "feature_b": "volume_weighted_momentum_acceleration"
                }
            },
            {
                "feature_name": "combo_min__star50_limit_proximity_early__bar_ret_0",
                "sign": 1,
                "overall_ic": 0.2965232245546598,
                "deflated_ic": 0.29607871239328526,
                "ic_ir": 0.5517851252664555,
                "monotonicity": 0.6961876832844575,
                "recipe": {
                    "op": "min",
                    "feature_a": "star50_limit_proximity_early",
                    "feature_b": "bar_ret_0"
                }
            },
            {
                "feature_name": "combo_ratio__max_down_ret__volume_weighted_momentum_acceleration",
                "sign": 1,
                "overall_ic": 0.2642237109048559,
                "deflated_ic": 0.26238100417301324,
                "ic_ir": 0.9245001368674545,
                "monotonicity": 0.8187683284457478,
                "recipe": {
                    "op": "ratio",
                    "feature_a": "max_down_ret",
                    "feature_b": "volume_weighted_momentum_acceleration"
                }
            },
            {
                "feature_name": "combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration",
                "sign": 1,
                "overall_ic": 0.2870538774251558,
                "deflated_ic": 0.28670067638872265,
                "ic_ir": 0.7018156059578935,
                "monotonicity": 0.7225806451612903,
                "recipe": {
                    "op": "diff",
                    "feature_a": "star50_limit_proximity_early",
                    "feature_b": "volume_weighted_momentum_acceleration"
                }
            },
            {
                "feature_name": "combo_rank_min__close_vs_open_range__bar_ret_0",
                "sign": 1,
                "overall_ic": 0.2425940452621087,
                "deflated_ic": 0.24185967125550603,
                "ic_ir": 0.7706083013736793,
                "monotonicity": 0.763049853372434,
                "recipe": {
                    "op": "rank_min",
                    "feature_a": "close_vs_open_range",
                    "feature_b": "bar_ret_0"
                }
            },
            {
                "feature_name": "combo_rank_min__bar_ret_0__rbreaker_buy_setup_proximity_early",
                "sign": 1,
                "overall_ic": 0.25423301240762003,
                "deflated_ic": 0.253372233769559,
                "ic_ir": 0.4653691985283152,
                "monotonicity": 0.632258064516129,
                "recipe": {
                    "op": "rank_min",
                    "feature_a": "bar_ret_0",
                    "feature_b": "rbreaker_buy_setup_proximity_early"
                }
            },
            {
                "feature_name": "combo_rank_max__max_up_ret__early_body_momentum",
                "sign": 1,
                "overall_ic": 0.24429889634472957,
                "deflated_ic": 0.2434724668391465,
                "ic_ir": 0.9504363172716715,
                "monotonicity": 0.8111436950146628,
                "recipe": {
                    "op": "rank_max",
                    "feature_a": "max_up_ret",
                    "feature_b": "early_body_momentum"
                }
            },
            {
                "feature_name": "combo_rank_min__net_volume_flow__star50_limit_proximity_early",
                "sign": 1,
                "overall_ic": 0.2849809569812078,
                "deflated_ic": 0.284059141865439,
                "ic_ir": 0.7264421447830155,
                "monotonicity": 0.7354838709677419,
                "recipe": {
                    "op": "rank_min",
                    "feature_a": "net_volume_flow",
                    "feature_b": "star50_limit_proximity_early"
                }
            },
            {
                "feature_name": "combo_tri_min__net_volume_flow__star50_limit_proximity_early__close_vs_open_range",
                "sign": 1,
                "overall_ic": 0.29142629465042186,
                "deflated_ic": 0.29033239576913766,
                "ic_ir": 0.6385109110352651,
                "monotonicity": 0.7390029325513197,
                "recipe": {
                    "op": "tri_min",
                    "feature_a": "net_volume_flow",
                    "feature_b": "star50_limit_proximity_early",
                    "feature_c": "close_vs_open_range"
                }
            },
            {
                "feature_name": "combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration",
                "sign": 1,
                "overall_ic": 0.2551600176387181,
                "deflated_ic": 0.25418432510594774,
                "ic_ir": 0.7886139674753255,
                "monotonicity": 0.7695014662756599,
                "recipe": {
                    "op": "sig_product",
                    "feature_a": "max_up_ret",
                    "feature_b": "volume_weighted_momentum_acceleration"
                }
            },
            {
                "feature_name": "combo_rel_diff__max_up_ret__early_order_flow_imbalance",
                "sign": 1,
                "overall_ic": 0.25469512750858836,
                "deflated_ic": 0.2554319799648392,
                "ic_ir": 0.6509686204618971,
                "monotonicity": 0.7237536656891496,
                "recipe": {
                    "op": "rel_diff",
                    "feature_a": "max_up_ret",
                    "feature_b": "early_order_flow_imbalance"
                }
            },
            {
                "feature_name": "combo_mean__bar_ret_0__max_down_ret",
                "sign": 1,
                "overall_ic": 0.22711991707642495,
                "deflated_ic": 0.226309045229397,
                "ic_ir": 0.5667445686315962,
                "monotonicity": 0.6480938416422287,
                "recipe": {
                    "op": "mean",
                    "feature_a": "bar_ret_0",
                    "feature_b": "max_down_ret"
                }
            },
            {
                "feature_name": "combo_rank_min__max_up_ret__close_vs_open_range",
                "sign": 1,
                "overall_ic": 0.2606991085547769,
                "deflated_ic": 0.2599974525443105,
                "ic_ir": 0.7361998797892939,
                "monotonicity": 0.7870967741935484,
                "recipe": {
                    "op": "rank_min",
                    "feature_a": "max_up_ret",
                    "feature_b": "close_vs_open_range"
                }
            },
            {
                "feature_name": "combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret",
                "sign": 1,
                "overall_ic": 0.20825077318048751,
                "deflated_ic": 0.2077734273779077,
                "ic_ir": 0.6710178315597944,
                "monotonicity": 0.7284457478005865,
                "recipe": {
                    "op": "rank_max",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "max_up_ret"
                }
            },
            {
                "feature_name": "combo_mean__star50_limit_proximity_early__close_vs_open_range",
                "sign": 1,
                "overall_ic": 0.2594982757330997,
                "deflated_ic": 0.25879083654433027,
                "ic_ir": 0.7484991969415183,
                "monotonicity": 0.750733137829912,
                "recipe": {
                    "op": "mean",
                    "feature_a": "star50_limit_proximity_early",
                    "feature_b": "close_vs_open_range"
                }
            },
            {
                "feature_name": "combo_max__star50_limit_proximity_early__bar_ret_0",
                "sign": 1,
                "overall_ic": 0.19514732215778377,
                "deflated_ic": 0.1945644141290487,
                "ic_ir": 0.7259924149985724,
                "monotonicity": 0.7214076246334311,
                "recipe": {
                    "op": "max",
                    "feature_a": "star50_limit_proximity_early",
                    "feature_b": "bar_ret_0"
                }
            },
            {
                "feature_name": "combo_ratio__max_down_ret__net_volume_flow",
                "sign": 1,
                "overall_ic": 0.2239801210085021,
                "deflated_ic": 0.22354064612127214,
                "ic_ir": 0.8477758665935772,
                "monotonicity": 0.7882697947214077,
                "recipe": {
                    "op": "ratio",
                    "feature_a": "max_down_ret",
                    "feature_b": "net_volume_flow"
                }
            },
            {
                "feature_name": "combo_ratio__max_down_ret__early_order_flow_imbalance",
                "sign": 1,
                "overall_ic": 0.16141205726737345,
                "deflated_ic": 0.16180190880366419,
                "ic_ir": 0.4571285727234313,
                "monotonicity": 0.6715542521994134,
                "recipe": {
                    "op": "ratio",
                    "feature_a": "max_down_ret",
                    "feature_b": "early_order_flow_imbalance"
                }
            },
            {
                "feature_name": "rbreaker_sell_setup_proximity_early",
                "sign": 1,
                "overall_ic": 0.2831687430636231,
                "deflated_ic": 0.2830982391512385,
                "ic_ir": 0.6705005705387909,
                "monotonicity": 0.7337243401759531
            },
            {
                "feature_name": "combo_rel_diff__max_up_ret__early_body_momentum",
                "sign": 1,
                "overall_ic": 0.24066581980322077,
                "deflated_ic": 0.24166767338793466,
                "ic_ir": 0.6394621551059533,
                "monotonicity": 0.7067448680351907,
                "recipe": {
                    "op": "rel_diff",
                    "feature_a": "max_up_ret",
                    "feature_b": "early_body_momentum"
                }
            },
            {
                "feature_name": "combo_sig_product__star50_limit_proximity_early__bar_ret_0",
                "sign": 1,
                "overall_ic": 0.20066467092377657,
                "deflated_ic": 0.19993369851304005,
                "ic_ir": 0.3439052206107904,
                "monotonicity": 0.6633431085043988,
                "recipe": {
                    "op": "sig_product",
                    "feature_a": "star50_limit_proximity_early",
                    "feature_b": "bar_ret_0"
                }
            },
            {
                "feature_name": "combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret",
                "sign": 1,
                "overall_ic": 0.20060559803161543,
                "deflated_ic": 0.20126779086317065,
                "ic_ir": 0.3379076210799859,
                "monotonicity": 0.6129032258064516,
                "recipe": {
                    "op": "sig_product",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "max_up_ret"
                }
            }
        ],
        "long": [],
        "short": []
    },
    "588000ETF": {
        "single": [
            {
                "feature_name": "max_up_ret",
                "sign": 1,
                "overall_ic": 0.1934996544494661,
                "deflated_ic": 0.19338354973585473,
                "ic_ir": 0.6050890044419849,
                "monotonicity": 0.7265547877591313
            }
        ],
        "long": [],
        "short": []
    },
    "159915ETF": {
        "single": [
            {
                "feature_name": "combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0",
                "sign": 1,
                "overall_ic": 0.2895468941144045,
                "deflated_ic": 0.2871778670190403,
                "ic_ir": 0.6249310567796941,
                "monotonicity": 0.7096774193548387,
                "recipe": {
                    "op": "tri_min",
                    "feature_a": "star50_limit_proximity_early",
                    "feature_b": "first_bar_sentiment",
                    "feature_c": "bar_body_rng_0"
                }
            },
            {
                "feature_name": "combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0",
                "sign": 1,
                "overall_ic": 0.2695974376622982,
                "deflated_ic": 0.267460142565745,
                "ic_ir": 0.5630881455823089,
                "monotonicity": 0.6527859237536657,
                "recipe": {
                    "op": "rank_min",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "bar_body_rng_0"
                }
            },
            {
                "feature_name": "combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0",
                "sign": 1,
                "overall_ic": 0.2613817644463645,
                "deflated_ic": 0.25941369399037006,
                "ic_ir": 0.7321816765250103,
                "monotonicity": 0.7390029325513197,
                "recipe": {
                    "op": "mean",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "bar_ret_0"
                }
            },
            {
                "feature_name": "combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment",
                "sign": 1,
                "overall_ic": 0.2592860430875877,
                "deflated_ic": 0.2577043890594975,
                "ic_ir": 0.5679684330125068,
                "monotonicity": 0.6920821114369502,
                "recipe": {
                    "op": "rank_max",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "first_bar_sentiment"
                }
            },
            {
                "feature_name": "combo_min__star50_limit_proximity_early__yesterday_first_30min_return",
                "sign": 1,
                "overall_ic": 0.25098822857718595,
                "deflated_ic": 0.25128182964203283,
                "ic_ir": 0.5263152633562241,
                "monotonicity": 0.6961876832844575,
                "recipe": {
                    "op": "min",
                    "feature_a": "star50_limit_proximity_early",
                    "feature_b": "yesterday_first_30min_return"
                }
            },
            {
                "feature_name": "combo_mean__rbreaker_sell_setup_proximity_early__early_range",
                "sign": 1,
                "overall_ic": 0.2502368481713917,
                "deflated_ic": 0.2498444866194768,
                "ic_ir": 0.5420801177091585,
                "monotonicity": 0.6856304985337244,
                "recipe": {
                    "op": "mean",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "early_range"
                }
            },
            {
                "feature_name": "combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret",
                "sign": 1,
                "overall_ic": 0.245491641236465,
                "deflated_ic": 0.24427935316223987,
                "ic_ir": 0.591172803628981,
                "monotonicity": 0.7331378299120235,
                "recipe": {
                    "op": "mean",
                    "feature_a": "rbreaker_sell_setup_proximity_early",
                    "feature_b": "max_up_ret"
                }
            },
            {
                "feature_name": "combo_clamp_diff__bar_ret_0__demark_setup_reversal_early",
                "sign": 1,
                "overall_ic": 0.22323564681343766,
                "deflated_ic": 0.22128611546334892,
                "ic_ir": 0.4123884502981297,
                "monotonicity": 0.6744868035190615,
                "recipe": {
                    "op": "clamp_diff",
                    "feature_a": "bar_ret_0",
                    "feature_b": "demark_setup_reversal_early"
                }
            },
            {
                "feature_name": "combo_rank_max__max_up_ret__opening_auction_imbalance",
                "sign": 1,
                "overall_ic": 0.21990382923440943,
                "deflated_ic": 0.21861785992095414,
                "ic_ir": 0.6600251678640738,
                "monotonicity": 0.7818181818181819,
                "recipe": {
                    "op": "rank_max",
                    "feature_a": "max_up_ret",
                    "feature_b": "opening_auction_imbalance"
                }
            },
            {
                "feature_name": "combo_z_sum__max_up_ret__first_bar_sentiment",
                "sign": 1,
                "overall_ic": 0.21540750824893834,
                "deflated_ic": 0.21292501906618044,
                "ic_ir": 0.5452097402543926,
                "monotonicity": 0.7079178885630498,
                "recipe": {
                    "op": "z_sum",
                    "feature_a": "max_up_ret",
                    "feature_b": "first_bar_sentiment"
                }
            },
            {
                "feature_name": "combo_ratio__max_up_ret__volume_weighted_price_position",
                "sign": 1,
                "overall_ic": 0.19489838732906045,
                "deflated_ic": 0.19353488417781342,
                "ic_ir": 0.5324329016329371,
                "monotonicity": 0.6997067448680352,
                "recipe": {
                    "op": "ratio",
                    "feature_a": "max_up_ret",
                    "feature_b": "volume_weighted_price_position"
                }
            }
        ],
        "long": [],
        "short": []
    }
}

def get_admitted_pool(etf: str, side: str = "single"):
    """Return admitted feature pool list for given ETF and side."""
    return POOLS.get(etf, {}).get(side, [])
