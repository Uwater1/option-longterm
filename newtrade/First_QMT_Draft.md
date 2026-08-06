I need to write a QMT of this thing for real-time simulated trading. (have to do)
Based on many experiment, Top-10 features seems the best, I'll stick with that
480d tail IC weight proven useful, follow that. However, we might hand tune 
Will leave 300ETF for now, they don't have much TP. 500 and 159915 do have enough TP, but selecting the True TP is hard, previous experience prove that, chance of selecting FP == FP rate (or day-model-new adopt that methodology) 
I know this thing has much space to optimize, but the deadline for first draft of QMT is close
Must trade options, not ETF
AGENTS TODO: 
1. Hand pick 10 features, can do extensive experiments on it. (Most important, AGENTS can do extensive experiments on this one, please give me a good deliverable)
2. Impliment enter at 10:00, exit at 14:35, trailling stoploss (I guess thats all?)