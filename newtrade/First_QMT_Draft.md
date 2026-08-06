I need to write a QMT of this thing for real-time simulated trading. (have to do)
Based on many experiment, Top-10 features seems the best, I'll stick with that
480d tail IC weight + EW proven useful, follow that. However, you can hand tune weight if you think necessary.
Will leave 300ETF for now, they don't have much TP. 500 and 159915 do have enough TP, but selecting the True TP is hard, previous experience prove that, chance of selecting FP == FP rate (or day-model-new adopt that methodology) 
Can use either the 2017_2025 set or 2018_2026 set
I know this thing has much space to optimize, but the deadline for first draft of QMT is close
Must trade options, not ETF
Notice that in newtrade, I have a hard cutoff at 2026-01, thats intentional, for true OOS that even human unsee during development, for this task you need to use it.
See newtrade\previous_failed_project.py.py for reference of a runnable, but unprofitable code. Use buy 2 and sell 2 this time to ensure enter and exit
Yes, data jump all over the place when data change, but Raw Sharpe or Return for option rarely go negative, so worth trying
Each model with be used for 1 week only
Any questions? Ask me

AGENTS TODO: 
1. Hand pick 10 features, can do extensive experiments on it. (Most important, AGENTS can do extensive experiments on this one, please give me a good deliverable)
2. Impliment enter at 10:00, exit at 14:35, trailling stoploss (I guess thats all?)