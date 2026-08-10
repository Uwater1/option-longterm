# -*- coding: utf-8 -*-
"""Smoke test for QMT logging fixes: per-day audit file, dedup scan,
decision_detail persistence + RERUN re-print. Run from repo root."""
import datetime
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "QMT_short"))
import qmt_strategy as Q  # noqa: E402
import numpy as np  # noqa: E402

tmp = tempfile.mkdtemp(prefix="qmt_smoke_")
Q.AUDIT_LOG_PREFIX = os.path.join(tmp, "qmt_audit_log")
Q.AUDIT_DATE_OVERRIDE = "20260810"
Q.STATE_DIR = os.path.join(tmp, "qmt_state")

# 1. per-day audit file naming
assert Q._audit_log_path() == os.path.join(tmp, "qmt_audit_log_20260810.txt"), \
    Q._audit_log_path()
assert Q._audit_log_path("20260809").endswith("qmt_audit_log_20260809.txt")

# 2. forced fixed file still works (replay tooling contract)
forced = os.path.join(tmp, "forced.log")
Q.AUDIT_LOG_FILE = forced
assert Q._audit_log_path("20260101") == forced
Q.AUDIT_LOG_FILE = ""

# 3. disabled switch
Q.AUDIT_LOG_ENABLED = False
assert Q._audit_log_path() == ""
Q.AUDIT_LOG_ENABLED = True

# 4. audit_decision writes to the dated file; dedup scan finds it
raw = {"bar_ret_0": 0.001, "gap_pct": np.float32(-0.002)}
detail = {"f1": {"raw": 0.5, "z": np.float32(1.25), "sign": 1}}
Q.audit_decision("500ETF", 7829.36, 1.2e8, raw, 0.83, detail, 0.7, 1.2, "long")
Q.audit_skip("159915ETF", "no_bars")
path = Q._audit_log_path()
assert os.path.exists(path), path
body = open(path, encoding="utf-8").read()
assert "AUDIT 20260810 DECISION 500ETF" in body
assert "AUDIT 20260810 SKIP 159915ETF REASON=no_bars" in body
assert "ZSIGNED=[f1=1.25000000]" in body  # selected-feature z now written
assert Q._audit_history_today("20260810") == {
    "500ETF": {"DECISION"}, "159915ETF": {"SKIP"}}

# 4b. ENTRY/SKIP backstop + open-position reconstruction from audit file
with open(path, "a", encoding="utf-8") as f:
    f.write("AUDIT 20260810 ENTRY 159915ETF CONTRACT=90007778.SZO SIDE=short "
            "ask=0.106900 order_price=0.107000 composite=-1.02949925 TIME=10:04:57\n")
    f.write("AUDIT 20260810 ENTRY 500ETF CONTRACT=10008001.SHO SIDE=long "
            "ask=0.050000 order_price=0.050100 composite=0.90000000 TIME=10:00:05\n")
    f.write("AUDIT 20260810 STOP 500ETF CONTRACT=10008001.SHO price=0.040000 "
            "stop=0.040000 peak=0.050000 TIME=11:20:00\n")
hist = Q._audit_history_today("20260810")
assert hist["159915ETF"] == {"SKIP", "ENTRY"}, hist
assert hist["500ETF"] == {"DECISION", "ENTRY"}, hist  # STOP not a backstop kind
opens = Q._open_positions_from_audit("20260810")
assert list(opens) == ["159915ETF"], opens  # 500ETF was stopped -> closed
assert opens["159915ETF"]["contract"] == "90007778.SZO"
assert abs(opens["159915ETF"]["entry_price"] - 0.1069) < 1e-9

# 4c. parse the REAL live log from the QMT sim install (if present)
live = r"E:\中信证券QMT交易终端仿真\bin.x64\qmt_audit_log.txt"
if os.path.exists(live):
    Q.AUDIT_DATE_OVERRIDE = ""
    Q.AUDIT_LOG_FILE = live
    h = Q._audit_history_today("20260810")
    assert h.get("159915ETF") == {"DECISION", "ENTRY", "SKIP"}, h
    o = Q._open_positions_from_audit("20260810")
    print("live-log parse OK:", {k: v["contract"] for k, v in o.items()})
    d = Q._decisions_from_audit("20260810")
    assert set(d) == {"500ETF", "159915ETF"}, sorted(d)
    r = d["159915ETF"]
    assert r["side"] == "short", r.keys()
    assert abs(float(r["composite"]) - (-1.02949925)) < 1e-6
    assert len(r["features"]) == 24
    # today's live lines predate the ZSIGNED fix -> empty; the RERUN print
    # falls back to raw feature values for those
    assert r["zsigned"] == {}
    print("live DECISION reparse OK: 159915ETF side=%s composite=%s "
          "zsigned=%d feats=%d" % (r["side"], r["composite"],
                                   len(r["zsigned"]), len(r["features"])))
    Q.AUDIT_LOG_FILE = ""
    Q.AUDIT_DATE_OVERRIDE = "20260810"

# 4d. legacy-file fallback: no per-day file -> readers use qmt_audit_log.txt
tmp2 = tempfile.mkdtemp(prefix="qmt_smoke_legacy_")
Q.AUDIT_LOG_PREFIX = os.path.join(tmp2, "qmt_audit_log")
Q.AUDIT_DATE_OVERRIDE = "20260809"
legacy = os.path.join(tmp2, "qmt_audit_log.txt")
with open(legacy, "w", encoding="utf-8") as f:
    f.write("AUDIT 20260809 DECISION 500ETF prev_close=1.000000 exp_bar_vol=1.000000 "
            "FEATURES=[a=1.00000000] ZSIGNED=[f1=0.50000000] composite=0.50000000 "
            "TH=long:0.7000/short:1.2000 SIDE=long TIME=10:00:01\n")
    f.write("AUDIT 20260809 ENTRY 500ETF CONTRACT=X.SHO SIDE=long ask=0.050000 "
            "order_price=0.050100 composite=0.50000000 TIME=10:00:02\n")
    f.write("AUDIT 20260811 SKIP 500ETF REASON=no_bars TIME=10:00:03\n")  # other day
assert Q._audit_read_path("20260809") == legacy
assert Q._audit_history_today("20260809") == {"500ETF": {"DECISION", "ENTRY"}}
assert Q._open_positions_from_audit("20260809")["500ETF"]["contract"] == "X.SHO"
d09 = Q._decisions_from_audit("20260809")
assert d09["500ETF"]["side"] == "long" and d09["500ETF"]["zsigned"] == {"f1": 0.5}
# once the per-day file appears it takes precedence over the legacy file
with open(os.path.join(tmp2, "qmt_audit_log_20260809.txt"), "w", encoding="utf-8") as f:
    f.write("AUDIT 20260809 SKIP 500ETF REASON=no_bars TIME=10:00:05\n")
assert Q._audit_read_path("20260809").endswith("qmt_audit_log_20260809.txt")
assert Q._audit_history_today("20260809") == {"500ETF": {"SKIP"}}
Q.AUDIT_LOG_PREFIX = os.path.join(tmp, "qmt_audit_log")
Q.AUDIT_DATE_OVERRIDE = "20260810"

# 5. decision_detail JSON round-trip (state file) incl. numpy scalars
state = Q._load_state("20260810")
state["decided"]["500ETF"] = "long"
state.setdefault("decision_detail", {})["500ETF"] = {
    "time": "10:00:03", "composite": 0.83, "side": "long",
    "detail": {"f1": {"raw": np.float32(0.5), "z": np.float32(1.25), "sign": 1}},
}
Q._save_state("20260810", state)
state2 = Q._load_state("20260810")
det = state2["decision_detail"]["500ETF"]
assert abs(float(det["composite"]) - 0.83) < 1e-9

# 6. RERUN re-print path used by init()
print("--- RERUN block (as printed by init on mid-day restart) ---")
Q._log_decision_block("500ETF", float(det["composite"]), det["detail"],
                      det["side"], det["time"], tag="RERUN")
print("--- live DECISION block ---")
Q._log_decision_block("500ETF", 0.83, detail, "long", "10:00:03", late=False)

print("ALL SMOKE CHECKS PASSED")
