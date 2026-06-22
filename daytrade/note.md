Agree with document on why current implementation failed:

Clipped target error: Linear regression (Lasso/Huber) performs poorly on max(0, y). Zero-inflation (half of targets are 0) violates linear assumptions. Noisy feature selection.
Threshold dilution: Single model uses sign for natural 50% split. Dual model predicts positive values most days. Percentile base is too wide → lower threshold → selects low-quality trades.
Fake dual system: Hybrid mode still gates direction using single-model sign. Inherits same linear limits.
Disagree that dual models are fundamentally worse: Dual models can beat single model if designed differently:

Model type: Use Tobit regression (for censored data) or binary classification (probability of positive day) instead of linear regression on clipped target.
Normalisation: Convert dual scores to rolling percentile ranks before thresholding to stop dilution.
True dual execution: Remove single-model sign gating. Let long and short models trade independently, resolving conflicts at decision bar using margin.