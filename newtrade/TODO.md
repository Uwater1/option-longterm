## 1. Noon Exit System

Two options you listed. Recommend **Option A (binary close-decision classifier)** over Option B (predict 13:05-15:00 return) — reason below.

**Why noon matters, literature-wise:**
China A-share/ETF market has structural overnight/lunch asymmetry not seen in US. Studies find arbitrageurs sell heavily on T+1-affected stocks around open (pushing overnight return negative) while buying near close drives significant last-30-min positive returns. Separately, asymmetric overnight anomaly work shows negative overnight returns follow negative daytime returns specifically — the anomaly doesn't fire on positive-daytime days. Lunch break (11:30-13:00 in futures, gap in ETF) is structurally similar to overnight — a market closure with info leakage risk. That's your economic rationale for "sometimes better exit at noon than hold to 14:35."

**Why binary close-decision > direct 13:05-15:00 return prediction:**
Your own finding: predicting 10:00-13:05 return has low IC. Predicting a *shorter, later-window* return (13:05-15:00) will likely be even noisier — smaller sample of minutes, less signal decay runway. A binary classifier ("hold vs close-now") is a *meta-labeling* problem, not a return-prediction problem — matches literature: triple-barrier method replaces fixed-horizon prediction with dynamic barriers adapting to volatility, meta-labeling adds secondary filter on primary signal, improving net profitability over raw directional accuracy. You already have primary signal (Z_composite at 10:00). Noon exit = secondary meta-model asking "is this position still good, or should we cut early."

**Concrete design:**
- Label: apply triple-barrier logic intraday. Barriers = current +stoploss / normal 14:35 exit / early noon-cut. At 11:25 (pre-lunch), snapshot features: running P&L since entry, realized vol since entry vs expected, Z_composite decay (has conviction weakened using only 10:00-11:25 bars), volume/turnover ratio vs normal, whether position is currently profitable (path-dependence — cf. why triple-barrier beats fixed horizon: two trades with identical +5% fixed-horizon return can have totally different risk paths — one hit +10% and pulled back, one dipped to -5% and recovered, and treating them as the same label is wrong).
- Target: binary — would holding through lunch to 14:35 beat closing now (net of fees), computed OOS in training only.
- Model: same gate mentality you use elsewhere — logistic or shallow tree, judged by **meta-IC / TP′ hit-rate harness you already built for FQ score** (§3.7 of your plan). Reuse that harness verbatim — don't build new judgment machinery.
- Gate: don't act unless P(early-cut better) exceeds trained threshold + buffer (same conviction-buffer pattern as §4.1).

**Validation**: CPCV + DSR like everything else in your report. Also run a **null test**: does the "close at noon" decision merely proxy for "stoploss would've fired anyway"? If yes, no incremental value — kill it. This is the kind of trap your FQ meta-IC work already caught once (tailIC≤0 gate was near-no-op because ICW shrinkage already zeroed those factors).

## TODO:
[ ] Meta labelling: labelling all the trades happen in In the sample, lable the diff between exit at 11:25, 13:05 and 14:35 (now), and analyzesis whether its worth the effort
[ ] If yes, train a binary classifier to predict whether the trade should have exited at 11:25 or 13:05 or 14:35. (I should probably leave only one, 11:25 or 13:05)