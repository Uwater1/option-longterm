# Day-Model Rolling Training Report

Generated: 2026-07-08 12:46
Quarters: ['2024-03-01', '2024-06-01', '2024-09-01', '2024-12-01', '2025-03-01', '2025-06-01', '2025-09-01', '2025-12-01']
Window: 6 years (rolling)

## Model Health Summary

| Quarter | Tag | ETF | Side | Outer IC | Outer Tail IC | Deflated Val IC | Status | Reason |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| 2024Q1 | 159915ETF_long_r202403 | 159915ETF | `long` | +0.0438 | -0.1446 | +0.0399 | WARN | outer_tail_IC=-0.1446<0 |
| 2024Q1 | 159915ETF_r202403 | 159915ETF | `single` | +0.0581 | +0.0695 | +0.0252 | OK | - |
| 2024Q1 | 159915ETF_short_r202403 | 159915ETF | `short` | +0.0570 | -0.2475 | +0.0649 | WARN | outer_tail_IC=-0.2475<0 |
| 2024Q1 | 300ETF_long_r202403 | 300ETF | `long` | -0.0392 | -0.1716 | +0.0222 | ALERT | outer_IC=-0.0392<0, outer_tail_IC=-0.1716<0 |
| 2024Q1 | 300ETF_r202403 | 300ETF | `single` | -0.0018 | +0.1350 | +0.0151 | WARN | outer_IC=-0.0018<0 |
| 2024Q1 | 300ETF_short_r202403 | 300ETF | `short` | -0.0583 | -0.0711 | +0.0065 | ALERT | outer_IC=-0.0583<0, outer_tail_IC=-0.0711<0 |
| 2024Q1 | 500ETF_long_r202403 | 500ETF | `long` | +0.1226 | +0.0882 | +0.0544 | OK | - |
| 2024Q1 | 500ETF_r202403 | 500ETF | `single` | +0.1502 | +0.2343 | +0.0016 | OK | - |
| 2024Q1 | 500ETF_short_r202403 | 500ETF | `short` | +0.0918 | +0.4387 | -0.0207 | OK | - |
| 2024Q1 | 50ETF_long_r202403 | 50ETF | `long` | +0.0008 | -0.1103 | +0.0348 | WARN | outer_tail_IC=-0.1103<0 |
| 2024Q1 | 50ETF_r202403 | 50ETF | `single` | -0.0165 | -0.1959 | +0.0004 | ALERT | outer_IC=-0.0165<0, outer_tail_IC=-0.1959<0 |
| 2024Q1 | 50ETF_short_r202403 | 50ETF | `short` | -0.0102 | -0.1250 | +0.0225 | ALERT | outer_IC=-0.0102<0, outer_tail_IC=-0.1250<0 |
| 2024Q1 | 588000ETF_long_r202403 | 588000ETF | `long` | +0.1388 | +0.1471 | +0.0203 | OK | - |
| 2024Q1 | 588000ETF_r202403 | 588000ETF | `single` | +0.1177 | +0.1666 | -0.0230 | OK | - |
| 2024Q1 | 588000ETF_short_r202403 | 588000ETF | `short` | +0.1921 | +0.1349 | +0.0200 | OK | - |
| 2024Q2 | 159915ETF_long_r202406 | 159915ETF | `long` | +0.1210 | +0.4448 | +0.0377 | OK | - |
| 2024Q2 | 159915ETF_r202406 | 159915ETF | `single` | +0.1966 | +0.2435 | +0.0255 | OK | - |
| 2024Q2 | 159915ETF_short_r202406 | 159915ETF | `short` | +0.1744 | -0.2157 | +0.0383 | WARN | outer_tail_IC=-0.2157<0 |
| 2024Q2 | 300ETF_long_r202406 | 300ETF | `long` | +0.0535 | +0.1950 | -0.0100 | OK | - |
| 2024Q2 | 300ETF_r202406 | 300ETF | `single` | +0.0358 | +0.3409 | -0.0273 | OK | - |
| 2024Q2 | 300ETF_short_r202406 | 300ETF | `short` | +0.0466 | -0.1063 | -0.0172 | WARN | outer_tail_IC=-0.1063<0 |
| 2024Q2 | 500ETF_long_r202406 | 500ETF | `long` | +0.2057 | -0.0691 | +0.0007 | WARN | outer_tail_IC=-0.0691<0 |
| 2024Q2 | 500ETF_r202406 | 500ETF | `single` | +0.0993 | +0.3217 | +0.0895 | OK | - |
| 2024Q2 | 500ETF_short_r202406 | 500ETF | `short` | +0.1075 | +0.1290 | +0.0114 | OK | - |
| 2024Q2 | 50ETF_long_r202406 | 50ETF | `long` | -0.0482 | -0.0836 | +0.0173 | ALERT | outer_IC=-0.0482<0, outer_tail_IC=-0.0836<0 |
| 2024Q2 | 50ETF_r202406 | 50ETF | `single` | -0.0511 | -0.3513 | +0.0130 | ALERT | outer_IC=-0.0511<0, outer_tail_IC=-0.3513<0 |
| 2024Q2 | 50ETF_short_r202406 | 50ETF | `short` | -0.0424 | -0.4634 | +0.0146 | ALERT | outer_IC=-0.0424<0, outer_tail_IC=-0.4634<0 |
| 2024Q2 | 588000ETF_long_r202406 | 588000ETF | `long` | +0.1557 | +0.0423 | +0.0496 | OK | - |
| 2024Q2 | 588000ETF_r202406 | 588000ETF | `single` | +0.1576 | +0.4383 | +0.0129 | OK | - |
| 2024Q2 | 588000ETF_short_r202406 | 588000ETF | `short` | +0.1172 | -0.0382 | +0.0386 | WARN | outer_tail_IC=-0.0382<0 |
| 2024Q3 | 159915ETF_long_r202409 | 159915ETF | `long` | +0.0499 | +0.5397 | +0.0070 | ALERT | IC_decay=59%>50% |
| 2024Q3 | 159915ETF_r202409 | 159915ETF | `single` | +0.0461 | +0.4052 | +0.0131 | ALERT | IC_decay=77%>50% |
| 2024Q3 | 159915ETF_short_r202409 | 159915ETF | `short` | +0.0489 | +0.1868 | +0.0155 | ALERT | IC_decay=72%>50% |
| 2024Q3 | 300ETF_long_r202409 | 300ETF | `long` | +0.0038 | -0.2673 | -0.0250 | ALERT | outer_tail_IC=-0.2673<0, IC_decay=93%>50% |
| 2024Q3 | 300ETF_r202409 | 300ETF | `single` | +0.0434 | -0.0904 | -0.0372 | WARN | outer_tail_IC=-0.0904<0 |
| 2024Q3 | 300ETF_short_r202409 | 300ETF | `short` | -0.0259 | -0.2281 | -0.0370 | ALERT | outer_IC=-0.0259<0, outer_tail_IC=-0.2281<0, IC_decay=155%>50% |
| 2024Q3 | 500ETF_long_r202409 | 500ETF | `long` | +0.0153 | +0.0712 | +0.0671 | ALERT | IC_decay=93%>50% |
| 2024Q3 | 500ETF_r202409 | 500ETF | `single` | +0.0173 | +0.0009 | +0.0776 | ALERT | IC_decay=83%>50% |
| 2024Q3 | 500ETF_short_r202409 | 500ETF | `short` | +0.0233 | -0.5129 | +0.0560 | ALERT | outer_tail_IC=-0.5129<0, IC_decay=78%>50% |
| 2024Q3 | 50ETF_long_r202409 | 50ETF | `long` | -0.0438 | +0.1228 | -0.0151 | WARN | outer_IC=-0.0438<0 |
| 2024Q3 | 50ETF_r202409 | 50ETF | `single` | -0.0187 | -0.1061 | -0.0090 | ALERT | outer_IC=-0.0187<0, outer_tail_IC=-0.1061<0 |
| 2024Q3 | 50ETF_short_r202409 | 50ETF | `short` | -0.0623 | +0.0815 | -0.0220 | WARN | outer_IC=-0.0623<0 |
| 2024Q3 | 588000ETF_long_r202409 | 588000ETF | `long` | -0.0162 | +0.2301 | +0.0595 | ALERT | outer_IC=-0.0162<0, IC_decay=110%>50% |
| 2024Q3 | 588000ETF_r202409 | 588000ETF | `single` | -0.0193 | +0.0248 | +0.0618 | ALERT | outer_IC=-0.0193<0, IC_decay=112%>50% |
| 2024Q3 | 588000ETF_short_r202409 | 588000ETF | `short` | +0.0190 | -0.2344 | +0.0358 | ALERT | outer_tail_IC=-0.2344<0, IC_decay=84%>50% |
| 2024Q4 | 159915ETF_long_r202412 | 159915ETF | `long` | +0.1559 | +0.2693 | +0.0805 | OK | - |
| 2024Q4 | 159915ETF_r202412 | 159915ETF | `single` | +0.1536 | +0.5470 | +0.0371 | OK | - |
| 2024Q4 | 159915ETF_short_r202412 | 159915ETF | `short` | +0.1617 | +0.4427 | +0.0667 | OK | - |
| 2024Q4 | 300ETF_long_r202412 | 300ETF | `long` | -0.0971 | -0.1434 | -0.0857 | ALERT | outer_IC=-0.0971<0, outer_tail_IC=-0.1434<0 |
| 2024Q4 | 300ETF_r202412 | 300ETF | `single` | -0.0991 | +0.2487 | +0.0547 | ALERT | outer_IC=-0.0991<0, IC_decay=329%>50% |
| 2024Q4 | 300ETF_short_r202412 | 300ETF | `short` | -0.0695 | -0.1847 | -0.0764 | ALERT | outer_IC=-0.0695<0, outer_tail_IC=-0.1847<0 |
| 2024Q4 | 500ETF_long_r202412 | 500ETF | `long` | +0.0216 | -0.2219 | +0.0793 | WARN | outer_tail_IC=-0.2219<0 |
| 2024Q4 | 500ETF_r202412 | 500ETF | `single` | +0.0105 | +0.0539 | +0.1104 | OK | - |
| 2024Q4 | 500ETF_short_r202412 | 500ETF | `short` | -0.0738 | -0.3560 | -0.0264 | ALERT | outer_IC=-0.0738<0, outer_tail_IC=-0.3560<0, IC_decay=416%>50% |
| 2024Q4 | 50ETF_long_r202412 | 50ETF | `long` | -0.1300 | +0.0402 | +0.0059 | WARN | outer_IC=-0.1300<0 |
| 2024Q4 | 50ETF_r202412 | 50ETF | `single` | -0.1546 | +0.0087 | -0.0035 | WARN | outer_IC=-0.1546<0 |
| 2024Q4 | 50ETF_short_r202412 | 50ETF | `short` | -0.1323 | +0.1166 | +0.0045 | WARN | outer_IC=-0.1323<0 |
| 2024Q4 | 588000ETF_long_r202412 | 588000ETF | `long` | +0.0666 | +0.4337 | +0.0738 | OK | - |
| 2024Q4 | 588000ETF_r202412 | 588000ETF | `single` | +0.0742 | +0.0862 | +0.1004 | OK | - |
| 2024Q4 | 588000ETF_short_r202412 | 588000ETF | `short` | +0.0669 | -0.1706 | +0.0970 | WARN | outer_tail_IC=-0.1706<0 |
| 2025Q1 | 159915ETF_long_r202503 | 159915ETF | `long` | +0.2186 | +0.4436 | +0.0247 | OK | - |
| 2025Q1 | 159915ETF_r202503 | 159915ETF | `single` | +0.1896 | +0.5291 | +0.0300 | OK | - |
| 2025Q1 | 159915ETF_short_r202503 | 159915ETF | `short` | +0.2225 | -0.0882 | +0.0200 | WARN | outer_tail_IC=-0.0882<0 |
| 2025Q1 | 300ETF_long_r202503 | 300ETF | `long` | -0.0653 | +0.0539 | -0.0867 | WARN | outer_IC=-0.0653<0 |
| 2025Q1 | 300ETF_r202503 | 300ETF | `single` | -0.1955 | -0.2185 | -0.0883 | ALERT | outer_IC=-0.1955<0, outer_tail_IC=-0.2185<0 |
| 2025Q1 | 300ETF_short_r202503 | 300ETF | `short` | -0.0672 | +0.0049 | -0.1007 | WARN | outer_IC=-0.0672<0 |
| 2025Q1 | 500ETF_long_r202503 | 500ETF | `long` | +0.0463 | -0.0490 | +0.0673 | WARN | outer_tail_IC=-0.0490<0 |
| 2025Q1 | 500ETF_r202503 | 500ETF | `single` | +0.0562 | +0.0378 | +0.0492 | OK | - |
| 2025Q1 | 500ETF_short_r202503 | 500ETF | `short` | +0.0511 | -0.1127 | +0.0529 | WARN | outer_tail_IC=-0.1127<0 |
| 2025Q1 | 50ETF_long_r202503 | 50ETF | `long` | -0.1121 | -0.2843 | -0.0901 | ALERT | outer_IC=-0.1121<0, outer_tail_IC=-0.2843<0 |
| 2025Q1 | 50ETF_r202503 | 50ETF | `single` | -0.1462 | -0.2027 | -0.0486 | ALERT | outer_IC=-0.1462<0, outer_tail_IC=-0.2027<0 |
| 2025Q1 | 50ETF_short_r202503 | 50ETF | `short` | -0.1452 | -0.0319 | -0.0527 | ALERT | outer_IC=-0.1452<0, outer_tail_IC=-0.0319<0 |
| 2025Q1 | 588000ETF_long_r202503 | 588000ETF | `long` | +0.1856 | +0.4880 | +0.0162 | OK | - |
| 2025Q1 | 588000ETF_r202503 | 588000ETF | `single` | +0.1691 | -0.1271 | +0.0624 | WARN | outer_tail_IC=-0.1271<0 |
| 2025Q1 | 588000ETF_short_r202503 | 588000ETF | `short` | +0.1894 | -0.3286 | +0.0604 | WARN | outer_tail_IC=-0.3286<0 |
| 2025Q2 | 159915ETF_long_r202506 | 159915ETF | `long` | +0.2219 | -0.0098 | +0.0494 | WARN | outer_tail_IC=-0.0098<0 |
| 2025Q2 | 159915ETF_r202506 | 159915ETF | `single` | +0.2243 | +0.5110 | +0.0409 | OK | - |
| 2025Q2 | 159915ETF_short_r202506 | 159915ETF | `short` | +0.2276 | +0.0123 | +0.0357 | OK | - |
| 2025Q2 | 300ETF_long_r202506 | 300ETF | `long` | +0.1316 | +0.2230 | -0.2026 | OK | - |
| 2025Q2 | 300ETF_r202506 | 300ETF | `single` | +0.0678 | +0.2649 | -0.1262 | OK | - |
| 2025Q2 | 300ETF_short_r202506 | 300ETF | `short` | +0.1127 | -0.0589 | -0.2203 | WARN | outer_tail_IC=-0.0589<0 |
| 2025Q2 | 500ETF_long_r202506 | 500ETF | `long` | +0.2834 | +0.3578 | +0.0051 | OK | - |
| 2025Q2 | 500ETF_r202506 | 500ETF | `single` | +0.2935 | +0.4692 | +0.0042 | OK | - |
| 2025Q2 | 500ETF_short_r202506 | 500ETF | `short` | +0.2820 | +0.5221 | -0.0090 | OK | - |
| 2025Q2 | 50ETF_long_r202506 | 50ETF | `long` | +0.1715 | -0.3407 | -0.1445 | WARN | outer_tail_IC=-0.3407<0 |
| 2025Q2 | 50ETF_r202506 | 50ETF | `single` | +0.0808 | +0.2885 | -0.1324 | OK | - |
| 2025Q2 | 50ETF_short_r202506 | 50ETF | `short` | +0.1249 | +0.2059 | -0.1344 | OK | - |
| 2025Q2 | 588000ETF_long_r202506 | 588000ETF | `long` | +0.1548 | -0.0049 | +0.0414 | WARN | outer_tail_IC=-0.0049<0 |
| 2025Q2 | 588000ETF_r202506 | 588000ETF | `single` | +0.1532 | +0.0062 | +0.0423 | OK | - |
| 2025Q2 | 588000ETF_short_r202506 | 588000ETF | `short` | +0.1386 | -0.2647 | +0.0284 | WARN | outer_tail_IC=-0.2647<0 |
| 2025Q3 | 159915ETF_long_r202509 | 159915ETF | `long` | +0.2476 | +0.0960 | +0.0919 | OK | - |
| 2025Q3 | 159915ETF_r202509 | 159915ETF | `single` | +0.2580 | +0.2374 | +0.0951 | OK | - |
| 2025Q3 | 159915ETF_short_r202509 | 159915ETF | `short` | +0.2630 | -0.0506 | +0.0820 | WARN | outer_tail_IC=-0.0506<0 |
| 2025Q3 | 300ETF_long_r202509 | 300ETF | `long` | +0.1288 | +0.4551 | -0.1275 | OK | - |
| 2025Q3 | 300ETF_r202509 | 300ETF | `single` | +0.1347 | +0.3882 | -0.1282 | OK | - |
| 2025Q3 | 300ETF_short_r202509 | 300ETF | `short` | +0.0948 | +0.2884 | -0.1484 | OK | - |
| 2025Q3 | 500ETF_long_r202509 | 500ETF | `long` | +0.2058 | +0.0175 | +0.0294 | OK | - |
| 2025Q3 | 500ETF_r202509 | 500ETF | `single` | +0.1426 | +0.1165 | +0.0292 | ALERT | IC_decay=51%>50% |
| 2025Q3 | 500ETF_short_r202509 | 500ETF | `short` | +0.2038 | +0.3560 | +0.0074 | OK | - |
| 2025Q3 | 50ETF_long_r202509 | 50ETF | `long` | +0.1346 | +0.0423 | -0.0734 | OK | - |
| 2025Q3 | 50ETF_r202509 | 50ETF | `single` | +0.1423 | +0.3913 | -0.0886 | OK | - |
| 2025Q3 | 50ETF_short_r202509 | 50ETF | `short` | +0.1346 | +0.0795 | -0.0895 | OK | - |
| 2025Q3 | 588000ETF_long_r202509 | 588000ETF | `long` | +0.0769 | +0.0939 | +0.0819 | ALERT | IC_decay=50%>50% |
| 2025Q3 | 588000ETF_r202509 | 588000ETF | `single` | +0.0955 | +0.1184 | +0.0902 | OK | - |
| 2025Q3 | 588000ETF_short_r202509 | 588000ETF | `short` | +0.0951 | +0.0021 | +0.0906 | OK | - |
| 2025Q4 | 159915ETF_long_r202512 | 159915ETF | `long` | +0.0909 | -0.3478 | +0.0924 | ALERT | outer_tail_IC=-0.3478<0, IC_decay=63%>50% |
| 2025Q4 | 159915ETF_r202512 | 159915ETF | `single` | +0.1233 | +0.0896 | +0.0362 | ALERT | IC_decay=52%>50% |
| 2025Q4 | 159915ETF_short_r202512 | 159915ETF | `short` | +0.1077 | +0.5707 | +0.0840 | ALERT | IC_decay=59%>50% |
| 2025Q4 | 300ETF_long_r202512 | 300ETF | `long` | +0.1035 | +0.2095 | +0.0413 | OK | - |
| 2025Q4 | 300ETF_r202512 | 300ETF | `single` | +0.1051 | +0.0217 | +0.0196 | OK | - |
| 2025Q4 | 300ETF_short_r202512 | 300ETF | `short` | +0.1205 | +0.1249 | +0.0265 | OK | - |
| 2025Q4 | 500ETF_long_r202512 | 500ETF | `long` | +0.0413 | +0.4407 | +0.0054 | ALERT | IC_decay=80%>50% |
| 2025Q4 | 500ETF_r202512 | 500ETF | `single` | +0.0413 | +0.0426 | +0.0045 | ALERT | IC_decay=71%>50% |
| 2025Q4 | 500ETF_short_r202512 | 500ETF | `short` | +0.0380 | -0.1331 | +0.0020 | ALERT | outer_tail_IC=-0.1331<0, IC_decay=81%>50% |
| 2025Q4 | 50ETF_long_r202512 | 50ETF | `long` | +0.1074 | -0.3209 | +0.0332 | WARN | outer_tail_IC=-0.3209<0 |
| 2025Q4 | 50ETF_r202512 | 50ETF | `single` | +0.1060 | -0.2052 | +0.0534 | WARN | outer_tail_IC=-0.2052<0 |
| 2025Q4 | 50ETF_short_r202512 | 50ETF | `short` | +0.1120 | -0.3209 | +0.0145 | WARN | outer_tail_IC=-0.3209<0 |
| 2025Q4 | 588000ETF_long_r202512 | 588000ETF | `long` | +0.0399 | +0.1269 | +0.0701 | OK | - |
| 2025Q4 | 588000ETF_r202512 | 588000ETF | `single` | +0.0494 | +0.2870 | +0.0489 | OK | - |
| 2025Q4 | 588000ETF_short_r202512 | 588000ETF | `short` | +0.1164 | +0.0960 | +0.0395 | OK | - |

### Warning Levels

- **OK**: Outer validation IC >= 0 and no significant decay.
- **WARNING**: Outer IC < 0 OR outer Tail IC < 0 (single metric negative).
- **ALERT**: Both outer IC and Tail IC negative, OR IC decay > 50% vs previous quarter.

## IC Timeline by ETF

### 300ETF (long side)

| Quarter | Outer IC | Outer Tail IC | Inner IC | # Selected | # Active |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 2024Q1 | -0.0392 | -0.1716 | +0.0671 | 21 | 21 |
| 2024Q2 | +0.0535 | +0.1950 | +0.0670 | 13 | 9 |
| 2024Q3 | +0.0038 | -0.2673 | +0.0567 | 7 | 3 |
| 2024Q4 | -0.0971 | -0.1434 | +0.0062 | 18 | 16 |
| 2025Q1 | -0.0653 | +0.0539 | -0.0477 | 19 | 19 |
| 2025Q2 | +0.1316 | +0.2230 | -0.1226 | 14 | 14 |
| 2025Q3 | +0.1288 | +0.4551 | -0.0787 | 15 | 15 |
| 2025Q4 | +0.1035 | +0.2095 | +0.0859 | 17 | 17 |

### 500ETF (long side)

| Quarter | Outer IC | Outer Tail IC | Inner IC | # Selected | # Active |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 2024Q1 | +0.1226 | +0.0882 | +0.1099 | 8 | 5 |
| 2024Q2 | +0.2057 | -0.0691 | +0.0604 | 20 | 19 |
| 2024Q3 | +0.0153 | +0.0712 | +0.1378 | 19 | 19 |
| 2024Q4 | +0.0216 | -0.2219 | +0.1970 | 17 | 17 |
| 2025Q1 | +0.0463 | -0.0490 | +0.1280 | 15 | 15 |
| 2025Q2 | +0.2834 | +0.3578 | +0.0212 | 16 | 16 |
| 2025Q3 | +0.2058 | +0.0175 | +0.0793 | 16 | 15 |
| 2025Q4 | +0.0413 | +0.4407 | +0.0736 | 15 | 15 |

### 588000ETF (long side)

| Quarter | Outer IC | Outer Tail IC | Inner IC | # Selected | # Active |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 2024Q1 | +0.1388 | +0.1471 | +0.0517 | 22 | 22 |
| 2024Q2 | +0.1557 | +0.0423 | +0.1047 | 20 | 20 |
| 2024Q3 | -0.0162 | +0.2301 | +0.1373 | 23 | 23 |
| 2024Q4 | +0.0666 | +0.4337 | +0.1971 | 21 | 21 |
| 2025Q1 | +0.1856 | +0.4880 | +0.1220 | 21 | 19 |
| 2025Q2 | +0.1548 | -0.0049 | +0.0917 | 21 | 20 |
| 2025Q3 | +0.0769 | +0.0939 | +0.1918 | 23 | 22 |
| 2025Q4 | +0.0399 | +0.1269 | +0.1842 | 23 | 22 |

### 159915ETF (long side)

| Quarter | Outer IC | Outer Tail IC | Inner IC | # Selected | # Active |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 2024Q1 | +0.0438 | -0.1446 | +0.1452 | 22 | 22 |
| 2024Q2 | +0.1210 | +0.4448 | +0.2043 | 9 | 8 |
| 2024Q3 | +0.0499 | +0.5397 | +0.1132 | 19 | 19 |
| 2024Q4 | +0.1559 | +0.2693 | +0.1523 | 20 | 20 |
| 2025Q1 | +0.2186 | +0.4436 | +0.0579 | 18 | 18 |
| 2025Q2 | +0.2219 | -0.0098 | +0.1217 | 17 | 17 |
| 2025Q3 | +0.2476 | +0.0960 | +0.2053 | 16 | 16 |
| 2025Q4 | +0.0909 | -0.3478 | +0.2009 | 20 | 20 |

### 50ETF (long side)

| Quarter | Outer IC | Outer Tail IC | Inner IC | # Selected | # Active |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 2024Q1 | +0.0008 | -0.1103 | +0.0988 | 19 | 19 |
| 2024Q2 | -0.0482 | -0.0836 | +0.0646 | 17 | 17 |
| 2024Q3 | -0.0438 | +0.1228 | -0.0055 | 14 | 14 |
| 2024Q4 | -0.1300 | +0.0402 | +0.0357 | 15 | 14 |
| 2025Q1 | -0.1121 | -0.2843 | -0.0480 | 17 | 17 |
| 2025Q2 | +0.1715 | -0.3407 | -0.0942 | 15 | 15 |
| 2025Q3 | +0.1346 | +0.0423 | -0.0450 | 14 | 14 |
| 2025Q4 | +0.1074 | -0.3209 | +0.1074 | 17 | 17 |

## Feature Stability Across Quarters

### 300ETF (long side)

| Feature | 2024Q1 | 2024Q2 | 2024Q3 | 2024Q4 | 2025Q1 | 2025Q2 | 2025Q3 | 2025Q4 | Freq |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| bar_body_rng_2 | - | - | - | Y | Y | Y | Y | Y | 5/8 |
| bar_ret_0 | - | - | - | - | - | - | Y | - | 1/8 |
| bar_rng_0 | - | - | - | - | Y | - | Y | Y | 3/8 |
| bar_rng_3 | Y | - | - | - | Y | - | - | - | 2/8 |
| bar_rng_5 | Y | Y | - | - | - | - | - | - | 2/8 |
| bar_vol_4 | Y | - | - | Y | - | - | - | - | 2/8 |
| bar_vol_5 | - | - | - | - | - | - | Y | Y | 2/8 |
| bar_vwap_dev_1 | Y | - | - | - | - | - | - | - | 1/8 |
| capital_large_order_ratio | - | - | - | - | Y | Y | Y | Y | 4/8 |
| capital_net_ratio | - | - | - | Y | - | - | - | - | 1/8 |
| capital_net_value | Y | - | - | - | - | - | - | - | 1/8 |
| consecutive_inside_bars_3d | - | - | - | - | - | - | Y | Y | 2/8 |
| early_kurtosis | Y | - | - | - | Y | Y | - | - | 3/8 |
| early_vwap_dev | Y | - | - | - | - | - | - | - | 1/8 |
| first_bar_return | Y | Y | Y | Y | Y | Y | - | Y | 7/8 |
| gap_pct | Y | Y | - | Y | Y | Y | Y | Y | 7/8 |
| growth_momentum_ratio | Y | - | - | - | - | - | - | - | 1/8 |
| iv_diff_1d | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| margin_net_buy | Y | - | - | - | Y | Y | Y | - | 4/8 |
| max_up_ret | Y | Y | Y | - | - | - | - | - | 3/8 |
| measured_move_proximity | Y | - | - | - | - | - | - | - | 1/8 |
| option_oi_growth | Y | - | - | Y | Y | Y | Y | Y | 6/8 |
| outside_bar_reversal_day | Y | - | - | - | - | - | - | - | 1/8 |
| short_sell_cover_spread | Y | - | - | - | - | - | - | - | 1/8 |
| sma100_dist | - | - | - | Y | Y | Y | Y | Y | 5/8 |
| vix_iv_spread | - | Y | - | Y | - | Y | - | Y | 4/8 |
| volume_slope | - | - | - | - | Y | - | - | Y | 2/8 |
| yearly_low_distance | - | - | - | - | - | Y | - | Y | 2/8 |
| yesterday_afternoon_momentum | - | - | - | - | - | - | Y | - | 1/8 |
| yesterday_body_ratio | Y | - | - | Y | Y | - | - | Y | 4/8 |
| yesterday_cvd_close | - | - | - | Y | Y | - | - | - | 2/8 |
| yesterday_day_pm_am_vol_ratio | - | - | - | - | Y | Y | Y | - | 3/8 |
| yesterday_day_vwap_dev | Y | Y | - | Y | Y | - | - | - | 4/8 |
| yesterday_early_momentum | - | - | - | - | Y | Y | Y | Y | 4/8 |
| yesterday_early_range | - | Y | - | Y | Y | - | - | Y | 4/8 |
| yesterday_early_vwap_dev | - | - | - | Y | - | - | - | - | 1/8 |
| yesterday_gap | Y | - | - | Y | Y | Y | Y | Y | 6/8 |
| yesterday_northbound_net_ratio | Y | Y | - | Y | - | - | - | - | 3/8 |

### 500ETF (long side)

| Feature | 2024Q1 | 2024Q2 | 2024Q3 | 2024Q4 | 2025Q1 | 2025Q2 | 2025Q3 | 2025Q4 | Freq |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| bar_body_rng_2 | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| bar_ret_0 | Y | - | - | - | - | - | - | Y | 2/8 |
| bar_rng_3 | - | Y | Y | Y | Y | Y | Y | Y | 7/8 |
| bar_vol_4 | - | Y | Y | Y | Y | - | Y | Y | 6/8 |
| bar_vwap_dev_1 | - | Y | Y | Y | Y | - | - | - | 4/8 |
| capital_buy_volume | - | - | - | - | - | - | - | Y | 1/8 |
| cvd_divergence_day | - | Y | Y | Y | Y | Y | Y | Y | 7/8 |
| early_skew | - | Y | Y | Y | Y | Y | Y | - | 6/8 |
| early_vwap_dev | - | Y | Y | - | - | - | - | - | 2/8 |
| first_bar_return | - | Y | Y | Y | Y | Y | Y | - | 6/8 |
| gap_pct | - | Y | Y | Y | Y | - | - | - | 4/8 |
| iv | - | - | - | Y | - | - | - | - | 1/8 |
| margin_extreme_rank_252d | - | - | - | - | - | Y | Y | Y | 3/8 |
| margin_net_buy | - | - | - | - | - | Y | - | - | 1/8 |
| max_up_ret | Y | Y | Y | - | - | - | - | - | 3/8 |
| measured_move_proximity | - | Y | - | - | - | Y | - | - | 2/8 |
| northbound_net | - | - | - | Y | - | - | - | Y | 2/8 |
| option_oi_growth | - | - | - | - | - | - | Y | - | 1/8 |
| roc60 | - | - | Y | - | - | - | - | - | 1/8 |
| short_sell_cover_spread | - | - | Y | Y | - | - | - | Y | 3/8 |
| short_sell_quantity | - | Y | Y | Y | Y | Y | Y | Y | 7/8 |
| sma100_dist | - | - | - | - | - | Y | Y | Y | 3/8 |
| sma200_dist | - | - | - | Y | Y | - | - | - | 2/8 |
| vix_diff_1d | - | - | Y | - | - | - | - | Y | 2/8 |
| volume_slope | - | - | - | - | - | - | - | Y | 1/8 |
| yesterday_afternoon_momentum | - | - | Y | Y | Y | Y | Y | - | 5/8 |
| yesterday_body_ratio | - | - | - | - | Y | Y | Y | - | 3/8 |
| yesterday_day_close_pos | - | - | Y | Y | - | - | - | - | 2/8 |
| yesterday_day_pm_am_vol_ratio | - | Y | - | - | - | - | - | - | 1/8 |
| yesterday_day_range | - | Y | - | - | - | Y | Y | - | 3/8 |
| yesterday_day_realized_vol | - | Y | - | - | - | - | - | - | 1/8 |
| yesterday_day_vwap_dev | - | Y | - | - | Y | Y | - | - | 3/8 |
| yesterday_early_momentum | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| yesterday_gap_pct | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| yesterday_northbound_net_ratio | - | Y | Y | - | - | - | - | - | 2/8 |

### 588000ETF (long side)

| Feature | 2024Q1 | 2024Q2 | 2024Q3 | 2024Q4 | 2025Q1 | 2025Q2 | 2025Q3 | 2025Q4 | Freq |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| bar_ret_0 | - | - | - | - | - | Y | - | - | 1/8 |
| bar_rng_2 | - | Y | Y | Y | Y | Y | Y | - | 6/8 |
| bar_rng_3 | Y | Y | - | - | - | - | - | - | 2/8 |
| bar_rng_5 | - | - | Y | - | Y | Y | - | - | 3/8 |
| bar_vol_4 | - | - | - | - | - | - | - | Y | 1/8 |
| bar_vwap_dev_1 | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| capital_large_order_ratio | - | - | - | - | - | - | - | Y | 1/8 |
| capital_net_ratio | Y | Y | Y | Y | Y | Y | Y | - | 7/8 |
| cl_pos_in_range | Y | Y | Y | Y | - | - | - | - | 4/8 |
| consecutive_inside_bars_3d | Y | Y | Y | Y | Y | - | - | - | 5/8 |
| early_kurtosis | Y | Y | - | Y | - | Y | Y | Y | 6/8 |
| early_skew | - | - | - | - | Y | Y | Y | Y | 4/8 |
| first_30min_return | - | Y | - | Y | - | - | Y | - | 3/8 |
| first_bar_return | Y | Y | Y | Y | Y | - | Y | Y | 7/8 |
| iv | - | - | - | - | Y | - | - | - | 1/8 |
| margin_extreme_rank_252d | - | Y | Y | - | - | - | - | - | 2/8 |
| max_up_ret | Y | - | Y | - | Y | Y | - | Y | 5/8 |
| measured_move_proximity | Y | - | Y | - | - | - | - | - | 2/8 |
| northbound_sell | Y | - | - | - | - | - | - | - | 1/8 |
| outside_bar_reversal_day | - | - | - | - | Y | Y | Y | Y | 4/8 |
| roc5 | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| short_sell_cover_spread | Y | Y | Y | Y | Y | Y | - | Y | 7/8 |
| sma100_dist | - | Y | Y | Y | Y | Y | Y | Y | 7/8 |
| tech_value_rotation | - | - | - | Y | - | - | - | - | 1/8 |
| vix | - | - | - | - | - | - | Y | Y | 2/8 |
| vix_diff_1d | - | - | - | - | - | - | - | Y | 1/8 |
| vol5 | - | Y | Y | Y | Y | Y | Y | - | 6/8 |
| vol60 | Y | Y | Y | Y | - | Y | Y | Y | 7/8 |
| vol_ratio_10_60 | Y | Y | Y | Y | Y | Y | Y | - | 7/8 |
| vol_ratio_5_20 | Y | - | - | - | - | - | - | - | 1/8 |
| volatility_percentile_20d | - | Y | Y | Y | Y | Y | Y | Y | 7/8 |
| volume_percentile_20d | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| volume_slope | - | - | - | - | - | Y | Y | Y | 3/8 |
| yearly_high_distance | Y | - | - | - | - | - | Y | - | 2/8 |
| yesterday_body_ratio | Y | - | - | - | - | - | - | - | 1/8 |
| yesterday_day_kurtosis | Y | - | - | - | - | - | - | Y | 2/8 |
| yesterday_day_realized_vol | - | Y | Y | - | - | - | - | Y | 3/8 |
| yesterday_day_skew | Y | Y | Y | Y | - | - | - | Y | 5/8 |
| yesterday_first_30min_return | - | - | Y | Y | Y | Y | Y | - | 5/8 |
| yesterday_gap | Y | - | - | - | - | - | Y | Y | 3/8 |
| yesterday_lunch_gap | Y | - | Y | Y | - | - | Y | - | 4/8 |
| yesterday_stoch_rsi_cross | - | - | Y | Y | Y | Y | Y | Y | 6/8 |

### 159915ETF (long side)

| Feature | 2024Q1 | 2024Q2 | 2024Q3 | 2024Q4 | 2025Q1 | 2025Q2 | 2025Q3 | 2025Q4 | Freq |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| bar_body_rng_0 | Y | Y | Y | Y | Y | - | - | - | 5/8 |
| bar_ret_0 | - | - | - | - | - | Y | Y | Y | 3/8 |
| bar_rng_2 | - | - | - | Y | Y | - | - | - | 2/8 |
| bar_rng_3 | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| bar_vol_4 | Y | Y | Y | Y | Y | Y | - | - | 6/8 |
| bar_vol_5 | - | - | - | - | - | - | Y | Y | 2/8 |
| body_to_range_ratio | Y | - | - | - | - | - | Y | Y | 3/8 |
| capital_net_ratio | - | - | - | - | - | Y | - | Y | 2/8 |
| capital_net_value | - | - | Y | Y | Y | - | - | - | 3/8 |
| consecutive_inside_bars_3d | Y | - | - | - | - | - | - | - | 1/8 |
| early_kurtosis | Y | - | - | - | - | - | - | - | 1/8 |
| early_range | Y | Y | Y | Y | Y | - | - | - | 5/8 |
| gap_pct | Y | - | Y | Y | Y | Y | Y | Y | 7/8 |
| growth_momentum_ratio | - | - | - | - | - | Y | - | - | 1/8 |
| margin_buy_repayment_spread | Y | - | Y | Y | - | - | - | - | 3/8 |
| margin_net_buy | - | - | - | - | Y | Y | Y | Y | 4/8 |
| max_up_ret | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| mfi14 | Y | - | - | - | - | - | - | - | 1/8 |
| northbound_net | Y | - | Y | Y | Y | - | - | Y | 5/8 |
| outside_bar_reversal_day | Y | - | Y | Y | - | Y | Y | - | 5/8 |
| roc60 | - | - | Y | Y | - | - | - | - | 2/8 |
| short_repayment_quantity | Y | - | - | - | - | - | - | - | 1/8 |
| sma100_dist | - | - | - | - | Y | Y | Y | Y | 4/8 |
| tech_value_rotation | Y | - | Y | Y | Y | Y | Y | Y | 7/8 |
| vix_diff_1d | - | - | - | - | - | - | - | Y | 1/8 |
| volatility_percentile_20d | - | - | Y | - | - | - | - | - | 1/8 |
| volume_percentile_20d | Y | - | Y | Y | Y | Y | Y | Y | 7/8 |
| volume_slope | - | - | - | - | - | Y | Y | Y | 3/8 |
| yearly_low_distance | Y | - | - | - | - | - | - | - | 1/8 |
| yesterday_afternoon_momentum | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| yesterday_body_ratio | - | - | - | - | - | - | - | Y | 1/8 |
| yesterday_day_vwap_dev | Y | Y | Y | Y | Y | - | - | Y | 6/8 |
| yesterday_early_momentum | Y | Y | - | - | - | Y | Y | Y | 5/8 |
| yesterday_early_vwap_dev | - | - | Y | Y | Y | - | - | - | 3/8 |
| yesterday_first_bar_volume | - | - | - | Y | - | - | - | - | 1/8 |
| yesterday_gap | Y | - | Y | Y | Y | Y | Y | Y | 7/8 |
| yesterday_lunch_gap | Y | - | Y | Y | Y | Y | Y | Y | 7/8 |

### 50ETF (long side)

| Feature | 2024Q1 | 2024Q2 | 2024Q3 | 2024Q4 | 2025Q1 | 2025Q2 | 2025Q3 | 2025Q4 | Freq |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| bar_body_rng_2 | - | - | - | - | Y | Y | - | - | 2/8 |
| bar_ret_0 | Y | - | - | Y | - | - | - | - | 2/8 |
| bar_rng_5 | Y | Y | Y | Y | - | - | - | - | 4/8 |
| bar_vol_4 | Y | - | Y | Y | - | - | - | Y | 4/8 |
| bar_vwap_dev_3 | - | - | Y | - | Y | Y | Y | Y | 5/8 |
| body_to_range_ratio | - | - | - | - | Y | - | Y | Y | 3/8 |
| capital_large_order_ratio | - | - | - | - | - | - | - | Y | 1/8 |
| capital_net_accel | - | - | - | - | - | - | - | Y | 1/8 |
| cvd_divergence_day | - | - | - | - | - | Y | Y | Y | 3/8 |
| early_kurtosis | Y | Y | Y | - | - | - | - | - | 3/8 |
| early_realized_vol | - | - | - | Y | Y | Y | Y | Y | 5/8 |
| first_bar_return | - | Y | Y | - | Y | Y | Y | Y | 6/8 |
| gap_pct | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| growth_momentum_ratio | Y | Y | - | - | - | - | - | - | 2/8 |
| high_beta_vol_ratio | - | - | - | - | - | - | Y | Y | 2/8 |
| iv_corridor_width | Y | Y | - | Y | - | - | - | Y | 4/8 |
| margin_buy_repayment_spread | Y | Y | - | - | - | - | - | - | 2/8 |
| margin_net_buy | - | - | Y | - | - | - | - | - | 1/8 |
| max_up_ret | - | Y | - | - | - | - | - | - | 1/8 |
| measured_move_proximity | Y | Y | - | - | - | - | - | - | 2/8 |
| northbound_net | Y | Y | Y | - | - | - | - | - | 3/8 |
| option_oi_growth | - | - | - | - | Y | Y | Y | Y | 4/8 |
| outside_bar_reversal_day | - | Y | - | - | - | - | - | - | 1/8 |
| sma100_dist | - | Y | Y | Y | Y | Y | Y | Y | 7/8 |
| sma200_dist | Y | - | - | - | - | - | - | - | 1/8 |
| vix | Y | - | - | - | - | - | - | - | 1/8 |
| vix_diff_1d | Y | Y | Y | Y | Y | Y | Y | - | 7/8 |
| vix_realized_spread | - | - | - | Y | Y | - | - | - | 2/8 |
| volume_slope | - | - | - | Y | - | - | - | - | 1/8 |
| yesterday_body_ratio | Y | - | - | - | - | - | - | Y | 2/8 |
| yesterday_cvd_close | - | - | - | - | Y | - | - | - | 1/8 |
| yesterday_day_kurtosis | Y | Y | - | Y | Y | Y | Y | Y | 7/8 |
| yesterday_day_pm_am_vol_ratio | - | - | - | - | Y | Y | Y | - | 3/8 |
| yesterday_day_vwap_dev | Y | Y | Y | Y | Y | Y | Y | - | 7/8 |
| yesterday_first_bar_volume | - | - | Y | - | Y | Y | - | - | 3/8 |
| yesterday_gap | - | Y | - | Y | Y | Y | - | - | 4/8 |
| yesterday_illiquidity_amihud | Y | - | Y | Y | Y | Y | Y | Y | 7/8 |
| yesterday_lunch_gap | Y | - | - | - | - | - | - | - | 1/8 |
| yesterday_stoch_rsi_cross | Y | Y | Y | - | - | - | - | Y | 4/8 |

## Methodology

1. **Rolling Window**: Each model trains on the most recent 6 years of data before the lockbox date.
2. **Relative Validation Blocks**: 6 non-overlapping 3-month blocks placed backward from the lockbox with 10-day embargo gaps.
   - 4 inner blocks (for Optuna tuning)
   - 2 outer blocks (held-out, closest to lockbox — most recent and most relevant)
3. **Warning System**: Based on pre-lockbox outer validation IC only (no OOS peeking).
4. **Artifacts**: Models in `models/rolling/`, results in `data/rolling/`, plots in `plots/rolling/`.
