Beyond Correlation: A Unified Framework
for Stable Predictive Modeling in
Financial Time Series Using Causal
Inference and Distributional Robustness

This report outlines a comprehensive, theoretically grounded, and algorithmically
detailed research framework for stability selection tailored for financial time series. The
objective is to establish a foundational baseline for future empirical studies by unifying
methodological approaches from resampling theory, causal inference, and distributionally
robust optimization. While empirical validation is outside the scope of this work, the
framework provides clear specifications for implementation, enabling rigorous data-
driven research. The analysis synthesizes recent academic literature to propose a multi-
stage methodology that moves beyond traditional correlation-based feature selection
towards the construction of more robust, stable, and interpretable predictive models
capable of withstanding the inherent non-stationarity and uncertainty of financial
markets.




Theoretical Underpinnings: Integrating Resampling,
Causality, and Distributional Robustness

A robust framework for stability selection in financial time series necessitates a synthesis
of three distinct but complementary theoretical domains: resampling methods for
statistical inference on dependent data, causal inference for identifying true drivers
rather than spurious associations, and distributionally robust optimization for formalizing
and ensuring out-of-sample performance guarantees. This integration creates a holistic
methodology where each component addresses a specific weakness of the others, leading
to a more resilient modeling paradigm. The core idea is to use resampling not just as a
tool for estimating variability, but as a mechanism to probe model stability; to leverage
causality not merely as an interpretability layer, but as a guiding principle for feature
construction; and to frame the final model not as a single point estimate, but as a
solution to a robust optimization problem designed to hedge against distributional shifts.

    The foundation of stability selection is resampling, which Meinshausen and Bühlmann
    introduced to reduce false positives in high-dimensional variable selection 95 177  . The
bootstrap is a versatile technique for estimating the sampling distribution of a statistic by
repeatedly resampling from the original dataset 2 66 . For independent and identically
distributed (i.i.d.) data, simple random sampling suffices. However, financial time series
violate the i.i.d. assumption due to serial dependence, such as autocorrelation and
    volatility clustering 68 193    . Applying standard bootstrap methods would destroy these
    critical temporal dependencies, leading to inconsistent estimates and invalid inference
    156    . Consequently, specialized bootstrap methods for time series have been developed,
    primarily falling into two categories: block-based and model-based approaches 101  . Block
    bootstrap techniques, such as the Moving Block Bootstrap (MBB), preserve local
    dependence by resampling contiguous blocks of observations, thereby maintaining the
    order and correlation structure within each block 43 103   . Model-based approaches, like
    the sieve bootstrap, first fit a parametric model (e.g., an autoregressive model) to the
    data, then resample the residuals and re-simulate the time series, allowing the model to
    capture the underlying data-generating process 100126       . These resampling mechanisms
    form the engine of stability selection, providing the diverse subsamples needed to assess
    the consistency of feature selection across different data fragments.

    While resampling addresses the statistical challenge of dependency, it operates on the
    given set of features and does not inherently distinguish between causal predictors and
    statistically correlated noise. In finance, confounding variables are ubiquitous, and
    selecting features based purely on correlation risks identifying spurious relationships that
    may not hold under different market conditions    8 92   . This is where causal inference
offers a powerful complement. The Structural Causal Model (SCM) provides a formal
language for describing causal relationships through a directed acyclic graph (DAG) and
functional equations, moving the focus from joint probability distributions to functional
dependencies 14 45 . Causal feature selection aims to identify the direct causes of a
response variable, which are expected to be more stable across environments because
they reflect the underlying structural invariance of the system 15 76 . By integrating
causal principles, the feature pool for stability selection can be refined to include only
those variables that plausibly drive the outcome, significantly reducing the risk of
selecting features based on transient correlations. Techniques have been developed to
adapt causal discovery algorithms, such as the Fast Causal Inference (FCI) algorithm, for
time series data to infer effective connectivity networks 116149.

    Finally, even if a stable set of causal features is identified, financial time series are
    characterized by non-stationarity and regime shifts, meaning the statistical properties of
    the data can change over time 121227    . A model optimized solely on historical data may

perform poorly when faced with a new regime. Distributionally Robust Optimization
(DRO) provides a principled framework to address this issue 162163. Instead of optimizing
for performance on the empirical distribution of the training data, DRO optimizes for the
worst-case expected performance over a set of plausible distributions, known as an
ambiguity set, centered around the empirical one 72 183. This approach explicitly hedges
against uncertainty in the data-generating process. The Wasserstein metric has become a
popular choice for defining the ambiguity set due to its strong finite-sample statistical
guarantees, tractable reformulations for many problems, and intuitive interpretation 97
125222. There is also a deep conceptual link between DRO and stability; notions of
minimax optimal estimation under distribution shift are closely related to stability criteria
96 , and paradigms like Invariant Risk Minimization (IRM) can be formulated as specific
instances of DRO, highlighting a shared goal of learning invariant, causal structures 7 9
175.




    Algorithmic Specification of the Resampling Engine for
    Time Series

    The resampling engine is the operational heart of any stability selection framework,
    responsible for generating the diverse subsamples that allow for the assessment of feature
    selection stability. For financial time series, the choice of resampling algorithm is critical,
    as it must respect the inherent temporal dependence structure to produce valid results.
    The primary challenge is to balance the preservation of local correlation with sufficient
    variability between resampled datasets. The literature presents two dominant families of
    adapted bootstrap methods: block-based and model-based, each with distinct algorithmic
    implementations and parameter choices 101102.

    Block bootstrap methods operate by treating the time series as a sequence of overlapping
    or non-overlapping blocks of consecutive observations. The most common variant is the
    Moving Block Bootstrap (MBB), where blocks of a fixed length m are drawn with
    replacement from the original series, and adjacent blocks are concatenated to form a new
    time series of the same length 43 103. The key algorithmic parameter for MBB is the block
    length m. A small m fails to capture the serial correlation, while a large m results in highly
    correlated and less diverse resamples 4 69 . Consequently, automatic block-length
    selection procedures are crucial for practical application. Politis and White (2004)
    developed a prominent method that estimates the optimal block length from the data's

    autocorrelation structure     4                                          . Other approaches involve minimizing an estimator of the
    mean squared error of the statistic of interest     63                                       . The consistency of the MBB for non-
    stationary time series has been established under certain conditions, though the proofs
    can be complex     64 221                                       . Other block bootstrap variants include the Stationary Bootstrap,
    which uses a random block length to ensure stationarity in the resampled series, and the
    Circular Block Bootstrap, which treats the time series as circular to avoid edge effects     101                                    .

    Model-based bootstrap methods offer an alternative strategy by first approximating the
    data-generating process with a parametric model. The sieve bootstrap is a notable
    example in this class     126                                   . Its algorithm proceeds in several steps: 1. Model Fitting: Fit a
sequence of autoregressive (AR) models of increasing order p(n) to the observed time
series, where p(n) grows with the sample size n. This "sieve" progressively approximates
a general linear process 126. 2. Residual Bootstrapping: Estimate the model residuals
and create a new set of bootstrap residuals by sampling with replacement from the
original estimated residuals. 3. Re-simulation: Generate a new synthetic time series of
the same length by simulating the AR process using the bootstrap residuals.

The sieve bootstrap is particularly well-suited for linear processes and can be
computationally efficient 100. Another model-based approach is the AR-sieve bootstrap,
which is considered best for linear data 100. More generally, model-based techniques can
be applied to various models like SARIMA and TBATS, where resampling is performed on
the model's innovations or residuals 3 .

    The following table summarizes the key characteristics of these primary resampling
    algorithms.

    Feature          Moving Block Bootstrap (MBB)                               Sieve Bootstrap

    Core Principle   Resamples contiguous blocks of data to preserve local      Approximates the data-generating process with a
                     dependence 103.                                            parametric model (e.g., AR) and resamples the model's
                                                                                innovations 126.

    Key              Block length (m). Requires an automatic selection method   Model order (p), which should increase with sample size
    Parameter        4 .                                                        126.

    Assumptions      Weak mixing conditions are often assumed for theoretical   Assumes the underlying process can be well-approximated
                     guarantees 157. Consistency has been shown for non-        by a sequence of AR models 126. Often assumes linearity
                     stationary series  64 .                                    100.

    Advantages       Intuitive, model-free approach. Widely used in financial   Can be computationally efficient for linear processes.
                     applications 3 179.                                        Provides a clear model-based interpretation.

    Disadvantages Sensitive to block length choice. May struggle with long-     Relies on the validity of the specified parametric model.
                     range dependence.                                          Less flexible than block bootstrap.

For the proposed unified framework, the choice of resampling algorithm should be
treated as a configurable option. The Moving Block Bootstrap is a strong default
candidate due to its flexibility and widespread adoption, especially when combined with
a robust automatic block-length selection procedure 65 67 . However, the framework
should also accommodate the sieve bootstrap for cases where the data exhibits a clear
parametric structure. The practitioner must acknowledge that the theoretical properties
of these methods, such as consistency, rely on assumptions about the data's dependence
structure (e.g., β-mixing or α-mixing conditions) which may be violated in real-world
financial data 157219.




Causal Feature Selection as a Guiding Principle for
Model Construction

Integrating causal inference into the stability selection framework elevates the process
from correlational feature identification to the discovery of potentially stable, causal
drivers. This is particularly valuable in financial markets, where spurious correlations
abound and features selected based on association alone may lack generalizability across
different market regimes 8 76 . The goal is to shift the feature selection criterion from
"which variables are associated with the outcome?" to "which variables are direct causes
of the outcome?". This aligns perfectly with the objective of stability selection, which
seeks to identify features that are consistently selected, as direct causal features are
hypothesized to be more invariant and thus more likely to be stably selected 13 .

The theoretical foundation for this approach is the Structural Causal Model (SCM), a
framework formalized by Judea Pearl that uses directed graphs and structural equations
to represent causal relationships 16 180244. Within an SCM, the effect of external
interventions can be simulated using the do() operator, distinguishing mere observation
from active manipulation 245. Causal feature selection focuses on identifying the parent
nodes of a target variable in the causal graph, as these represent the direct causes 15 .
Identifying these direct causal features enhances model stability because they correspond
to the fundamental mechanisms driving the system, which are more likely to remain
constant than indirect correlations that can arise from unobserved confounders 13 76 .
Recent research has provided necessary and sufficient conditions for causal feature
selection even in the presence of latent variables, further strengthening the theoretical
basis 12 248.

There are several ways to integrate causal principles into a stability selection framework.
One approach is causal pre-filtering. Before applying the stability selection algorithm, a
causal discovery phase is conducted on the full dataset to learn a local causal graph.
Algorithms like the Fast Causal Inference (FCI) algorithm, which has been adapted for
time series, can be used to infer conditional independence relations and orient edges to
find potential causal links 116. The parent nodes of the target variable in this learned
graph would then constitute the candidate feature set for the subsequent stability
selection step. This dramatically reduces the dimensionality of the search space and
ensures that the stability selection process is focused only on variables with a plausible
direct causal connection to the outcome.

Another strategy involves using causal concepts for validation and refinement. After an
initial set of features is selected using a standard stability selection procedure (e.g., based
on Lasso), causal strength metrics can be applied to the selected features to differentiate
between those with a direct causal effect and those selected due to indirect correlations
249. For instance, one could estimate the direct causal effect (DCE) of each selected
feature and examine if there is a clear boundary between features with large DCEs
(causal) and those with small DCEs (non-causal) 249. Features found to be primarily
associated through indirect paths could be deprioritized or removed, leading to a more
parsimonious and potentially more stable final model.

Furthermore, recent advances suggest a more deeply integrated approach where causal
reasoning is woven into the resampling process itself. Work combining bagging with
causal graphical model algorithms has shown promise in improving the stability of
graphical model learning 98 99 . In such a framework, each bootstrap sample would be
used to learn a local causal model, and feature stability would be assessed based on the
consistency of the causal graph structures or the selection of causal parents across the
bootstrap samples. This represents a more sophisticated fusion of the two paradigms,
moving beyond simple feature pre-filtering to an iterative process of learning stable
causal structures from resampled data.

    The following table contrasts the different levels of integration for causal inference within
    the stability selection framework.

    Integration     Description                                Pros                                 Cons
    Level

    Causal Pre-     Use a causal discovery algorithm on        Reduces dimensionality, focuses      Computationally intensive; causal discovery
    filtering       the full dataset to identify a pool of     search on plausible features,        algorithms may have high false positive/
                    direct cause candidates before             improves interpretability.           negative rates; relies on assumptions like
                    applying stability selection.                                                   faithfulness 75 .

    Causal          Apply a causal strength metric to          Can be applied as a post-hoc step;   Does not prevent the inclusion of non-causal
    Validation      features already selected by a             leverages existing selection         features during the initial selection phase;
                    standard stability selection method to     outputs.                             may be difficult if the number of selected
                    validate their causal status.                                                   features is large.

    Integrated      Learn a local causal model on each         Most theoretically aligned;          Highly complex to implement; requires a
    Learning        bootstrap sample and aggregate the         directly assesses the stability of   combination of resampling and causal
                    results to derive a stable causal          causal relationships, not just       discovery algorithms 98 99 .
                    structure.                                 associations.


For the proposed unified framework, a modular approach is recommended. The
framework should include a dedicated module for causal feature identification. Initially,
this could be implemented as a pre-filtering step to define the feature pool. As the field
matures, this could evolve into a more integrated learning scheme. It is important to note
that all causal inference methods rely on assumptions about the data-generating process,
such as the absence of unmeasured confounders or the faithfulness assumption, which
can be challenging to verify in practice 92 147. Acknowledging these limitations is
essential for the proper application of causal principles.




Distributionally Robust Optimization as a Formalism for
Out-of-Sample Performance

Distributionally Robust Optimization (DRO) provides the third pillar of the unified
framework, offering a formal and mathematically rigorous way to address the pervasive
uncertainty and non-stationarity in financial time series. Standard machine learning
approaches typically optimize a model's performance based on the empirical distribution
of the training data, implicitly assuming that future data will follow the same
distribution. This assumption is frequently violated in financial markets, where regime
shifts, structural breaks, and changing volatility patterns are common 121193. DRO
mitigates this risk by seeking a solution that performs well against a range of possible
future distributions, effectively hedging against model misspecification and data
uncertainty 36 162.

The central concept in DRO is the ambiguity set, which is a collection of probability
distributions that are deemed "close" to the empirical distribution derived from the
observed data 17 183. The DRO problem is then formulated as a minimax optimization:
minimize the worst-case expected loss over all distributions contained within this
ambiguity set. Mathematically, this can be expressed as:

                                     min max EP[Loss(y,ξ)]
                                     y∈Y P∈A

    where y is the decision or model parameter to be optimized, Y is the feasible set, P is a
    probability distribution in the ambiguity set \mathcal{A}, and \xi represents the
    uncertain data. The critical element of this formulation is the definition of the ambiguity
    set \mathcal{A}. The choice of the distance metric used to construct this set
    determines the nature of the robustness being achieved.

    The Wasserstein metric has emerged as a particularly attractive tool for constructing
    ambiguity sets in data-driven DRO. Several papers highlight its benefits, including the
    fact that it can be defined using the Wasserstein distance to constrain the set of
    distributions considered 178182  . Modern measure concentration results guarantee that,
under mild assumptions, the true underlying distribution lies within a Wasserstein ball of
a certain radius around the empirical distribution with a high probability that can be
quantified 97 222. This provides finite-sample, non-asymptotic guarantees, which is a
significant advantage over asymptotic arguments. Furthermore, DRO problems
formulated with Wasserstein ambiguity sets can often be reformulated into
computationally tractable convex optimization problems, making them applicable to a
    wide range of machine learning tasks 125260 . The radius of the Wasserstein ball can be
interpreted as a budget for the permissible distributional perturbation, linking the level of
conservatism in the model to a concrete statistical quantity 168232.

    There are deeper connections between DRO and the other components of the framework.
    Firstly, the concept of stability is intrinsically linked to distributional robustness. Research
    has shown that minimax optimal estimators under distribution shift are related to notions
    of stability, suggesting that DRO provides a formal mathematical language for what it
    means for a model to be "stable" 96 . Secondly, the paradigm of Invariant Risk
Minimization (IRM), which aims to learn predictors based on invariant causal
associations that hold across different environments, can be cast as a specific type of DRO
problem 7 9 175. This connection bridges the gap between the goal of learning stable
causal features (from the causal inference pillar) and the formal machinery of DRO. By
framing the final model as a DRO problem, the framework explicitly optimizes for the
kind of stability that IRM aims to achieve.

Advanced DRO formulations further enrich the framework. Decision-dependent DRO
allows the ambiguity set to depend on the decision variable y itself. This can be used to
calibrate the level of robustness dynamically, balancing the desire for robustness against
the potential loss in nominal performance 47 169173. Group-wise DRO applies the robust
optimization principle separately to predefined subgroups of the data (e.g., bull markets,
bear markets), ensuring that the model is not only robust on average but also performs
well within each specific regime 34 . These advanced concepts provide additional tools for
tailoring the robustness of the final predictive model to the specific needs of the financial
application.




An Integrated Algorithmic Blueprint for Stable
Predictive Modeling

Synthesizing the theoretical pillars of resampling, causality, and distributional robustness
yields a comprehensive, multi-stage algorithmic blueprint for stability selection in
financial time series. This framework is designed to be modular, allowing for the
incorporation of different methods at each stage while maintaining a coherent overall
structure. The goal is to transform a raw dataset into a robust, predictive model with
formal guarantees on its stability and out-of-sample performance. The process can be
broken down into three main stages: Data Preparation and Feature Generation,
Resampling and Stable Selection, and finally, Robust Modeling via Distributional
Optimization.

Stage 1: Data Preparation and Feature Generation This initial stage focuses on
transforming the raw input data into a more informative feature space and, optionally,
refining the feature pool using causal insights. 1. Input: A multivariate financial time
series dataset, consisting of a target variable (e.g., future returns) and a set of candidate
predictor variables. 2. Temporal Representation Learning: Raw time series are
processed to extract richer representations. This can involve standard techniques like
creating lagged variables, rolling window statistics (mean, volatility), and technical
indicators. More advanced methods, such as shapelet-based transformations or signature
kernels, can be employed to capture complex temporal motifs and nonlinear dynamics,
providing the model with more powerful inputs 77 124239. 3. (Optional) Causal Pre-
filtering: To enhance stability and interpretability, a causal discovery algorithm suitable
for time series (e.g., tsFCI) can be applied to the dataset 116. The output is a causal graph
from which the parent nodes of the target variable are identified. These nodes form the

    reduced set of candidate features for the next stage, effectively filtering out variables that
    are not direct causes 249.

    Stage 2: Resampling and Stable Selection This core stage executes the stability
    selection procedure, using resampling to assess the consistency of feature selection across
    different data fragments. 1. Define Resampling Strategy: Select a resampling algorithm
    appropriate for time series. The Moving Block Bootstrap (MBB) is a recommended default
    due to its model-free nature 101   . If the MBB is chosen, an automatic block-length selection
method (e.g., based on spectral density or cross-validation) must be specified to
determine the block size m 4 65 . 2. Bootstrap Loop: Execute the following steps B
times, where B is a large number of iterations (e.g., 1000). a. Draw a bootstrap sample
S^(b) of the same length as the original series using the chosen resampling method. b.
On the subsample S^(b), train a base selection model. The choice of the base algorithm
is a configurable parameter; options include penalized regression (e.g., Lasso), tree-based
methods (e.g., Random Forests, Gradient Boosting), or other high-dimensional selection
algorithms 94 . c. Record the set of features, Ŝ^(b), that are selected by the base model
on this particular subsample. 3. Aggregation and Final Selection: Aggregate the results
from all B bootstrap iterations to derive a stable set of features. a. Calculate the selection
        1
frequency for each candidate feature j as π^<emb=′′1′′>j= B ∑</em>), where I(⋅) is
    the indicator function 95 . b. Derive the final stable feature set,
    \hat{S}}^{B} I(j \in \hat{S}^{(b)<em _text_thr="\text{thr">{\text{stable}}      ,
using one of two common aggregation strategies. The threshold-based approach selects
all features whose frequency exceeds a predefined threshold π</em>. The rank-based
approach selects the top }q features with the highest selection frequencies 95 .
Theoretical analysis suggests the rank-based approach may be more robust to certain
types of contamination 95 .

Stage 3: Robust Modeling via Distributional Optimization This final stage takes the
stable set of features and builds a predictive model that is formally robust to
distributional uncertainty. 1. Train Robust Model: Instead of simply fitting a standard
regression or classification model to the full dataset using the features in S^stable,
formulate the problem as a Distributionally Robust Optimization task. 2. Define
Ambiguity Set: Construct a Wasserstein ambiguity set around the empirical joint
distribution of the selected features and the response variable. The radius of this set,
\epsilon, must be calibrated from the data. Methods exist to choose \epsilon such
that the true distribution is contained within the set with a high probability, providing
finite-sample guarantees 166168233. 3. Solve DRO Problem: Solve the resulting minimax
optimization problem. The objective is typically to minimize the worst-case expected loss
(e.g., squared error for regression, log-loss for classification) over the Wasserstein

ambiguity set. This can often be reformulated into a tractable convex optimization
problem 125178. The solution yields a robust model parameter (e.g., regression
coefficients) and provides a prediction that is guaranteed to have good performance
across a range of plausible future scenarios.

This integrated blueprint provides a complete, theoretically motivated workflow. It begins
by creating informative features, uses resampling to filter for stable predictors, and
concludes by building a model that is explicitly designed to be robust to the uncertainties
inherent in financial time series. Each stage is supported by a rich body of academic
literature, making it a solid foundation for future empirical investigation.




    Synthesis, Limitations, and Directions for Future
    Research

    This report has presented a unified theoretical and algorithmic framework for stability
    selection in financial time series, integrating resampling theory, causal inference, and
    distributionally robust optimization. The proposed framework moves beyond traditional
    methods by addressing three critical weaknesses of conventional modeling pipelines.
    First, it acknowledges the non-i.i.d. nature of financial data by employing specialized
    resampling techniques like the Moving Block Bootstrap. Second, it seeks to mitigate the
    problem of spurious correlations prevalent in finance by incorporating causal principles
    to guide feature selection towards more stable, direct causes. Third, it confronts the
    challenge of non-stationarity and regime shifts by framing the final model as a
    distributionally robust optimization problem, which provides formal guarantees on out-
    of-sample performance. Together, these components create a cohesive methodology for
    constructing predictive models that are not only accurate on historical data but are also
    fundamentally designed for stability and reliability in dynamic environments.

    Despite its theoretical coherence, the proposed framework is subject to several limitations
    and presents significant challenges for future research. A primary concern is
    computational complexity. While DRO problems with Wasserstein ambiguity sets are
    often reformulatable into tractable forms, the dimensionality of the problem can grow
    rapidly with the number of features and samples 131133  . Similarly, causal discovery on
    multivariate time series can be computationally demanding, and running these
    algorithms within a bootstrap loop for stability selection could be prohibitive for very
    large datasets. Developing more efficient algorithms for each stage of the framework is a
    critical area for future work.

    A second major limitation is the reliance on assumptions and hyperparameter tuning.
    The consistency of block bootstrap methods depends on weak dependence conditions like
    mixing, which may not hold perfectly in financial data 64 219. Causal discovery algorithms
rely on assumptions such as the faithfulness condition, which posits that all statistical
dependencies are consequences of the causal structure, an assumption that is difficult to
verify and may be violated 75 . Furthermore, the framework introduces several
hyperparameters whose optimal values are not known a priori: the number of bootstrap
samples B, the block length for MBB, the selection threshold π_thr, and the radius of the
Wasserstein ambiguity set. The sensitivity of the final model to these choices requires
careful investigation, and automated methods for calibration are needed.

    The integration of the three pillars also poses a significant engineering and
    methodological challenge. While the theoretical connections between bootstrapping,
    causality, and DRO are becoming clearer, developing a seamless, end-to-end software
    implementation that integrates these disparate components is a non-trivial task. The
    interfaces between the causal pre-filtering module, the resampling engine, and the DRO
    solver need to be carefully designed to ensure compatibility and efficiency. Moreover, the
    theoretical guarantees of each component (e.g., consistency of the MBB, soundness of the
    causal discovery algorithm, optimality of the DRO solution) are typically derived under
    separate, often idealized, assumptions. Proving composite guarantees for the entire
    integrated framework remains a profound open question.

Future research should focus on several key directions. Empirical validation of the
framework's superiority over traditional methods on real financial datasets is paramount.
This includes benchmarking its performance across different market regimes and asset
classes. Research into scalable algorithms, particularly for causal discovery and DRO, is
essential for practical adoption. Investigating adaptive methods for hyperparameter
selection, perhaps using meta-learning or Bayesian optimization, could help automate
parts of the framework. Finally, extending the framework to handle streaming data and
incorporate test-time adaptation techniques would make it even more relevant for real-
world financial applications, where models must continuously adapt to new information
without catastrophic forgetting 253254. By systematically addressing these limitations, the
proposed framework can evolve from a theoretical blueprint into a powerful and practical
tool for building robust predictive models in finance.

 Reference

 1. tsbootstrap: Enhancing Time Series Analysis with Advanced ... - arXiv https://
    arxiv.org/html/2404.15227v1
 2. (PDF) Bootstrap Methods for Time Series - ResearchGate https://
    www.researchgate.net/publication/29654667_Bootstrap_Methods_for_Time_Series
 3. [PDF] Assessing Budget Risk with Monte Carlo and Time Series Bootstrap https://
    repositorio-aberto.up.pt/bitstream/10216/134984/2/484384.pdf
 4. Bootstrap Methods for Strategy Robustness: Resampling When You … https://
    www.susanpotter.net/quant/bootstrap-methods-strategy-robustness/
 5. [PDF] Decoding Causal Structure: End-to-End Mediation Pathways Inference https://
    papers.nips.cc/paper_files/paper/2025/file/b54a93090407850f069ab52a072d5bc8-
    Paper-Conference.pdf
 6. [PDF] Wasserstein Generative Data Modeling for Robust Portfolio ... https://
    www.preprints.org/frontend/manuscript/b1aaf9ac4e0886e0e71c57fc5a72f375/
    download_pub
 7. [PDF] Invariant Risk Minimization Is A Total Variation Model - arXiv https://
    arxiv.org/pdf/2405.01389
 8. Invariant Risk Minimization: An Information Theoretic View https://
    www.inference.vc/invariant-risk-minimization/
 9. [PDF] Invariant Risk Minimization - Semantic Scholar https://
    www.semanticscholar.org/paper/Invariant-Risk-Minimization-Arjovsky-Bottou/
    753b7a701adc1b6072378bd048cfa8567885d9c7
10. [PDF] Invariant Risk Minimization - Leon Bottou https://leon.bottou.org/
    publications/pdf/tr-irm-2019.pdf
11. [PDF] Enhancing Distributional Stability among Sub-populations https://
    proceedings.mlr.press/v238/liu24c/liu24c.pdf
12. [PDF] Necessary and Sufficient Conditions for Causal Feature Selection in ... https://
    assets.amazon.science/d5/2d/27d307da40aea2fd9feee9655000/necessary-and-
    sufficient-conditions-for-causal-feature-selection-in-time-series-with-latent-common-
    causes.pdf
13. Causal feature selection framework for stable soft sensor modeling ... https://
    www.sciencedirect.com/science/article/abs/pii/S1474034626000297

14. Causality, Machine Learning, and Feature Selection: A Survey - MDPI https://
    www.mdpi.com/1424-8220/25/8/2373
15. Model-Based Causal Feature Selection for General Response Types https://
    www.tandfonline.com/doi/full/10.1080/01621459.2024.2395588
16. [PDF] 111 Causality-based Feature Selection: Methods and Evaluations http://
    4llab.net/publication/3409382.pdf
17. Frameworks and Results in Distributionally Robust Optimization https://ojmo.centre-
    mersenne.org/articles/10.5802/ojmo.15/
18. [PDF] Distributionally Robust Optimization under Decision-Dependent ... https://
    optimization-online.org/wp-content/uploads/2020/01/7591.pdf
19. Interpretable Distributionally Robust Optimization for Battery Energy ... https://
    ieeexplore.ieee.org/iel8/8685265/11174071/10988702.pdf
20. Distributionally Robust Optimization: A review on theory and ... https://
    www.aimsciences.org/article/doi/10.3934/naco.2021057?viewType=HTML
21. Distributionally robust optimization with decision-dependent ... https://
    link.springer.com/10.1007/s10107-026-02346-0
22. Distributionally Robust Optimization Under Distorted Expectations https://
    pubsonline.informs.org/doi/10.1287/opre.2020.0685
23. A reliable ensemble forecasting modeling approach for complex ... https://
    www.sciencedirect.com/science/article/abs/pii/S0305054824003034
24. Stability selection enables robust learning of differential equations ... https://
    royalsocietypublishing.org/rspa/article/478/2262/20210916/54488/Stability-
    selection-enables-robust-learning-of
25. [PDF] Nystr๖m Regularization for Time Series Forecasting https://www.jmlr.org/
    papers/volume23/21-1341/21-1341.pdf
26. Adaptive algorithms for change point detection in financial time series https://
    www.aimspress.com/article/doi/10.3934/math.20241674
27. Deep Learning for Financial Time Series: A Large-Scale Benchmark ... https://
    arxiv.org/html/2603.01820v1
28. Non-Stationarity in Time-Series Analysis: Modeling Stochastic and ... https://
    www.tandfonline.com/doi/full/10.1080/00273171.2024.2436413
29. [PDF] Mean–Variance Portfolio Selection by Continuous-Time ... https://
    www.columbia.edu/~xz2574/download/HJZ-MV.pdf
30. Machine learning advances for time series forecasting - Masini - 2023 https://
    onlinelibrary.wiley.com/doi/10.1111/joes.12429
31. Technology investigation on time series classification and prediction https://
    pmc.ncbi.nlm.nih.gov/articles/PMC9138170/

32. Inference for structural changes in nonstationary functional time ... https://
    academic.oup.com/jrsssb/advance-article/doi/10.1093/jrsssb/qkag072/8687472
33. Adaptive Ensemble Learning for Financial Time-Series Forecasting https://
    www.mdpi.com/2075-1680/14/8/597
34. GroupDRO: Robust Optimization & Fairness - Emergent Mind https://
    www.emergentmind.com/topics/group-distributionally-robust-optimization-groupdro
35. [PDF] Distributionally Robust Mean-Variance Portfolio Selection with ... http://
    www.columbia.edu/~xz2574/download/BCZ-final.pdf
36. Sampled-Data Wasserstein Distributionally Robust Control of ... - arXiv https://
    arxiv.org/html/2602.04219
37. Wasserstein Generative Data Modeling for Robust Portfolio ... https://dl.acm.org/doi/
    full/10.1145/3801228.3801314
38. Credible capacity evaluation of virtual power plants considering ... https://
    pmc.ncbi.nlm.nih.gov/articles/PMC12647671/
39. Integrated optimization of equipment degradation modeling and ... https://
    www.sciencedirect.com/science/article/abs/pii/S2213138825004576
40. [PDF] Portfolio rebalancing based on time series momentum and ... https://
    dr.lib.iastate.edu/bitstreams/ae765a46-7a68-4a49-bcbd-eb41d332c84e/download
41. Quantum-inspired robust optimization for coordinated scheduling of ... https://
    www.nature.com/articles/s41598-025-12280-4
42. Robust Hedging GANs: Towards Automated Robustification of ... https://
    www.tandfonline.com/doi/full/10.1080/1350486X.2024.2440661
43. Optimized Multi-Level Multi-Type Ensemble (OMME) Forecasting ... https://
    ieeexplore.ieee.org/iel7/6287639/10380310/10445459.pdf
44. [PDF] 1 Definition of trend analysis 2 Quantitative versus qualitative ... - IGAC
    https://igacproject.org/sites/default/files/2023-04/
    STAT_recommendations_TOAR_analyses_0.pdf
45. [PDF] Causal Inference Theory with Information Dependency Models - arXiv https://
    arxiv.org/pdf/2108.03099
46. NeurIPS Poster Distributionally Robust Performative Optimization https://neurips.cc/
    virtual/2025/poster/119893
47. [PDF] Frameworks and Results in Distributionally Robust Optimization https://
    ojmo.centre-mersenne.org/item/10.5802/ojmo.15.pdf
48. [PDF] Distributionally Robust Performative Optimization - arXiv https://arxiv.org/
    pdf/2407.01344
49. Distributionally robust Lyapunov–Barrier Networks for safe and ... https://
    www.sciencedirect.com/science/article/pii/S2666720725000426

50. Ariel NEUFELD | Nanyang Technological University, Singapore | ntu https://
www.researchgate.net/profile/Ariel-Neufeld
51. Beyond Risk: A Measure of Distribution Uncertainty - PubsOnLine https://
pubsonline.informs.org/doi/10.1287/isre.2022.0089
52. [PDF] program-book.pdf - 2026 INFORMS Optimization Society Conference https://
ios2026.isye.gatech.edu/sites/default/files/2026-03/program-book.pdf
53. uai2025 - Accepted Papers https://www.auai.org/uai2025/accepted_papers
54. 2 Theory | Forecasting: theory and practice https://forecasting-encyclopedia.com/
theory.html
55. [PDF] Synthetic Learner: Model-free inference on treatments over time https://
www.sciencedirect.com/science/article/am/pii/S030440762200152X
56. [PDF] Consistent Estimation, Variable Selection, and Forecasting in Factor ... https://
econweb.umd.edu/~chao/Research/research_files/ConsistentVariableSelection-
September%208%202025.pdf
57. [PDF] The 39th New England Statistics Symposium - From Data to Discovery https://
symposium.nestat.org/images/ness_book_may_27.pdf
58. [PDF] Long-term prediction intervals with many covariates - Sayar Karmakar https://
sayarkarmakar.github.io/publications/hdlongterm.pdf
59. Sensitivity analysis of Wasserstein distributionally robust ... - PMC https://
pmc.ncbi.nlm.nih.gov/articles/PMC8670962/
60. Stochastic Optimization with Decision-Dependent Distributions https://
pubsonline.informs.org/doi/10.1287/moor.2022.1287
61. Choosing the Right Intelligence — How Bayesian models, causal ... https://
medium.com/@adnanmasood/choosing-the-right-intelligence-how-bayesian-models-
causal-graphs-constraint-solvers-and-f34db730c59a
62. D.N. Politis Publications - UCSD Math https://math.ucsd.edu/~politis/
DPpublication.html
63. [PDF] Block bootstrap optimality and empirical block selection for sample ... https://
par.nsf.gov/servlets/purl/10400401
64. [PDF] Consistency and application of moving block bootstrap for non ... https://
arxiv.org/pdf/0711.4493
65. [PDF] Automatic Block-Length Selection for the Dependent Bootstrap https://
public.econ.duke.edu/~ap172/Politis_White_2004.pdf
66. [PDF] Bootstrap methods for time series - EconStor https://www.econstor.eu/
bitstream/10419/62726/1/725561971.pdf
67. Automatic Block-Length Selection for the Dependent Bootstrap https://
ideas.repec.org/a/taf/emetrv/v23y2004i1p53-70.html

68. [PDF] BOOTSTRAPPING FINANCIAL TIME SERIES - e-Archivo Repository :: https://e-
    archivo.uc3m.es/bitstreams/19afca69-fcf2-47da-b484-8ddc5ab5f048/download
69. [PDF] Optimal choice of bootstrap block length for periodically ... - HAL https://
    hal.science/hal-03472199/document
70. IPS 729 - Bootstrap-Based Statistical Inference for Dependent Data https://www.isi-
    next.org/conferences/session/667/details/
71. On the Equivalence and Performance of Distributionally Robust ... https://
    pubsonline.informs.org/doi/10.1287/msom.2023.0531
72. Distributionally robust optimization https://www.cambridge.org/core/services/aop-
    cambridge-core/content/view/5B4E65E3A5A2AEF24E218A6B34E6EAA2/
    S0962492924000084a.pdf/distributionally_robust_optimization.pdf
73. Tree-based vs. deep learning in time series - ScienceDirect.com https://
    www.sciencedirect.com/science/article/pii/S156849462600431X
74. [PDF] Observational process data analytics using causal inference - OSTI https://
    www.osti.gov/servlets/purl/2418510
75. [PDF] Elements of Causal Inference - OAPEN Library https://library.oapen.org/
    bitstream/id/056a11be-ce3a-44b9-8987-a6c68fce8d9b/11283.pdf
76. Causality from Bottom to Top: A Survey - arXiv https://arxiv.org/html/2403.11219v1
77. [PDF] Temporal representation learning for time series classification https://
    www.zzmylq.com/data/nca2021.pdf
78. Learning Reliable and Intuitive Temporal Logic Rules for ... https://dl.acm.org/doi/
    10.1145/3711896.3737022
79. Spatio-Temporal Consistency for Multivariate Time-Series ... https://
    ieeexplore.ieee.org/iel7/6287639/10380310/10445124.pdf
80. Temporal feature selection with SHAP values - Moneda https://lgmoneda.github.io/
    2020/12/07/temporal-feature-selection-with-shap-values.html
81. Time Series Analysis and Temporal Stability of Shallow Soil ... - MDPI https://
    www.mdpi.com/2073-4441/17/8/1140
82. Unsupervised Representation Learning for Time Series with ... https://
    openreview.net/forum?id=8qDwejCuCN
83. Normal Aging Affects the Short-Term Temporal Stability of Implicit ... https://
    www.eneuro.org/content/8/5/ENEURO.0527-20.2021
84. Awesome Time Series Forecasting/Prediction Papers - GitHub https://github.com/
    ddz16/TSFpaper
85. Learning Time-Series Forecasting with Temporal-Spatial-Sample ... https://arxiv.org/
    html/2606.07291v1

86. [PDF] temporal dependencies in feature importance https://www.cs.toronto.edu/
~mvolkovs/ICLR23_WinIT.pdf
87. Time Series Causal Inference - Rachel Leah Childers https://donskerclass.github.io/
CausalEconometrics/TimeSeries.html
88. Causal Inference Challenges with Interrupted Time Series Designs https://
muse.jhu.edu/pub/56/article/856400
89. [PDF] Matching Methods for Causal Inference with Time-Series Cross ... https://
imai.fas.harvard.edu/research/files/tscs.pdf
90. Causal Discovery with Multivariate Time Series Data - Medium https://medium.com/
causality-in-data-science/causal-discovery-with-multivariate-time-series-data-
a3f7ffc16747
91. Causal inference of multivariate time series in complex industrial ... https://
www.sciencedirect.com/science/article/abs/pii/S1474034623004482
92. 15 Causal Inference - Moving From Association to Causation https://peopleanalytics-
regression-book.org/causal_inference.html
93. Bayesian priors improve stability selection in high-dimensional ... https://
www.linkedin.com/posts/samuel-muller-17854393_bayesian-stability-selection-and-
inference-activity-7418042149126131712-Wp4e
94. Automated calibration for stability selection in penalised regression ... https://
pmc.ncbi.nlm.nih.gov/articles/PMC10746547/
95. Trimming stability selection increases variable selection robustness https://
link.springer.com/article/10.1007/s10994-023-06384-z
96. [PDF] Minimax Optimal Estimation of Stability Under Distribution Shift - arXiv
https://arxiv.org/pdf/2212.06338
97. [PDF] Data-driven distributionally robust optimization using the ... https://
repository.tudelft.nl/file/File_3ac9d19f-a219-45b6-88ec-9b78a0d73c56
98. [PDF] Bootstrap aggregation and confidence measures to improve time ... https://
proceedings.mlr.press/v236/debeire24a/debeire24a.pdf
99. Bootstrap-based causal structure learning - 玻尔 https://www.bohrium.com/paper-
details/bootstrap-based-causal-structure-learning/1133221493728083968-2000000
100. [PDF] Bootstraps for Time Series https://www.ssc.wisc.edu/~bhansen/718/
Buhlmann2002.pdf
101. [PDF] The Bootstrap Estimation In Time Series https://digitalcommons.mtu.edu/cgi/
viewcontent.cgi?article=1025&context=etdr
102. [PDF] Chapter 1 - Bootstrap Methods for Time Series - Kevin Sheppard https://
www.kevinsheppard.com/files/teaching/mfe/advanced-econometrics/
Kreiss_and_lahiri.pdf

103. Bootstrapping on Time Series Data — “Moving Block ... - Medium https://
medium.com/@daydreamersjp/bootstrapping-on-time-series-data-moving-block-
bootstrap-79aaf6648aec
104. Random forests for time-dependent processes https://www.esaim-ps.org/articles/ps/
pdf/2020/01/ps180111.pdf
105. [PDF] 1.Beyond-the-Status-Quo-A-Critical-Assessment-of-Lifecycle ... http://
www.icpmnetwork.com/wp-content/uploads/2025/09/1.Beyond-the-Status-Quo-A-
Critical-Assessment-of-Lifecycle-Investment-Advice.pdf
106. [PDF] Dynamic Factor Trees and Forests - A Theory-led Machine Learning ... https://
www.research-collection.ethz.ch/bitstreams/0b7614a0-379b-470f-8752-
e487e4e83350/download
107. [PDF] Statistical analysis and monitoring of time-series panels, with a ... https://
www.sidc.be/valusun/web/pdf/Thesis_Sophie_Mathieu.pdf
108. DistMatch: Adaptive Binning via Distribution Matching for Robust ... https://
arxiv.org/html/2606.00690
109. Working Papers - San Francisco Fed https://www.frbsf.org/research-and-insights/
publications/working-papers/
110. Publications - van der Schaar Lab https://www.vanderschaar-lab.com/publications/
111. [PDF] méthodes avec applications à la prévision des prix de l'électricité https://
theses.hal.science/tel-04720002v1/file/127897_ZAFFRAN_2024_archivage.pdf
112. Deep momentum networks with market trend dynamics - PMC https://
pmc.ncbi.nlm.nih.gov/articles/PMC12404547/
113. [PDF] Big Data Analytics and Information Science for Business and ... - MDPI https://
mdpi-res.com/bookfiles/book/4975/
Big_Data_Analytics_and_Information_Science_for_Business_and_Biomedical_Applicati
ons.pdf?v=1774919136
114. Research Papers - Sebastian Jaimungal https://sebastian.statistics.utoronto.ca/
research-papers/
115. Causal Discovery from Temporal Data: An Overview and New ... https://dl.acm.org/
doi/10.1145/3705297
116. Interpretability of Causal Discovery in Tracking Deterioration in a ... https://
pmc.ncbi.nlm.nih.gov/articles/PMC11207435/
117. Time-varying multivariate causal processes - ScienceDirect https://
www.sciencedirect.com/science/article/pii/S0304407624000174
118. Feature-based information-theoretic approach for detecting ... https://link.aps.org/
doi/10.1103/qnx2-yp4c

119. Causality in extremes of time series - Springer Nature https://link.springer.com/
     article/10.1007/s10687-023-00479-5
120. RegimeFolio: A Regime Aware ML System for Sectoral Portfolio ... https://arxiv.org/
     html/2510.14986v1
121. A Regime Aware ML System for Sectoral Portfolio Optimization in ... https://
     ieeexplore.ieee.org/iel8/6287639/10820123/11215751.pdf
122. Structured Robustness for Distribution Shifts - OpenReview https://openreview.net/
     forum?id=4tBjnFqmaQ
123. Publications - Stelios Bekiros https://www.steliosbekiros.com/publications/
124. [PDF] Learning time-dependent data with the signature transform https://
     afermanian.github.io/assets/docs/thesis.pdf
125. [PDF] Data-driven Distributionally Robust Optimization Using the ... https://
     optimization-online.org/wp-content/uploads/2015/05/4899.pdf
126. (PDF) Sieve Bootstrap for Time Series - ResearchGate https://www.researchgate.net/
     publication/38370987_Sieve_Bootstrap_for_Time_Series
127. Generative Robust Optimisation - arXiv https://arxiv.org/html/2606.22536v1
128. CDC 2025 Program | Wednesday December 10, 2025 - PaperPlaza https://
     css.paperplaza.net/conferences/conferences/CDC25/program/
     CDC25_ContentListWeb_1.html
129. [PDF] Learning Theory and Algorithms for Forecasting Non-stationary ... https://
     papers.nips.cc/paper/2015/file/41f1f19176d383480afa65d325c06ed0-Paper.pdf
130. [PDF] A First-Order Algorithmic Framework for Distributionally Robust ... http://
     papers.neurips.cc/paper/8649-a-first-order-algorithmic-framework-for-
     distributionally-robust-logistic-regression.pdf
131. [PDF] A First-Order Algorithmic Framework for Wasserstein Distributionally ...
     https://www1.se.cuhk.edu.hk/~manchoso/papers/fom_drlr-neurips19.pdf
132. [PDF] Residuals-based distributionally robust optimization with covariate ... https://
     optimization-online.org/wp-content/uploads/2020/11/8136-1.pdf
133. Efficient algorithms for distributionally robust optimization and its ... https://
     iro.uiowa.edu/esploro/outputs/doctoral/Efficient-algorithms-for-distributionally-
     robust-optimization/9984546943702771
134. From Data to Decisions: Distributionally Robust Optimization is ... https://av.tib.eu/
     media/59944
135. Online Conformal Model Selection for Nonstationary Time Series https://arxiv.org/
     html/2506.05544v2
136. Publications - Bart Van Parys https://www.vanparys.xyz/publications/

137. Frameworks and Results in Distributionally Robust Optimization https://ojmo.centre-
     mersenne.org/articles/OJMO_2022__3__A4_0/
138. Invariant Risk Minimization | Request PDF - ResearchGate https://
     www.researchgate.net/publication/334288906_Invariant_Risk_Minimization
139. zezhishao/DailyArXiv: Daily ArXiv Papers. - GitHub https://github.com/zezhishao/
     DailyArXiv
140. Long-Term Forecasting Trends in Machine Learning. - PhilArchive https://
     philarchive.org/rec/MAZLFT
141. Intelligence Entropy Principle and the ADE Stability Engineering ... https://arxiv.org/
     html/2606.18065v1
142. Available CRAN Packages by Date of Publication - Index of / https://
     archive.linux.duke.edu/cran/web/packages/available_packages_by_date.html
143. Publications - BayesWatch https://www.bayeswatch.com/publications/
144. Group Iterative Multiple Model Estimation Approaches in Clinical ... https://
     www.annualreviews.org/content/journals/10.1146/annurev-clinpsy-061724-080138
145. SARIMA: Complete Guide to Seasonal Time Series Forecasting with ... https://
     mbrenndoerfer.com/writing/sarima-seasonal-time-series-forecasting
146. [PDF] MM-iTransformer: A Multimodal Approach to Economic Time Series ... https://
     da.lib.kobe-u.ac.jp/da/kernel/0100493140/0100493140.pdf
147. Causal Inference on Time Series with Hidden Confounding - arXiv https://arxiv.org/
     html/2606.18969v1
148. Causal Inference Meets Deep Learning: A Comprehensive Survey https://
     pmc.ncbi.nlm.nih.gov/articles/PMC11384545/
149. [PDF] GST-UNet: A Neural Framework for Spatiotemporal Causal ... https://
     mirunaoprescu.com/assets/publications/2025_gstunet/GSTUNet.pdf
150. Full article: Objective causal predictions from observational data https://
     www.tandfonline.com/doi/full/10.1080/10408444.2024.2399856
151. Causality from bottom to top: a survey | Machine Learning https://link.springer.com/
     article/10.1007/s10994-025-06855-5
152. Universal Time-Series Representation Learning: A Survey - arXiv https://arxiv.org/
     html/2401.03717v3
153. Time Series Foundation Models for Multivariate Financial ... - arXiv https://arxiv.org/
     html/2507.07296v1
154. [PDF] The Long-Run Effects of Monetary Policy https://www.frbsf.org/wp-content/
     uploads/wp2020-01.pdf

155. Multiplier subsample bootstrap for statistics of time series https://
www.sciencedirect.com/science/article/abs/pii/S0378375824000405
156. Bootstrapping Not Independent and Not Identically Distributed Data https://
www.mdpi.com/2227-7390/10/24/4671
157. [PDF] Testing covariance separability for continuous functional data https://d-
nb.info/1370589131/34
158. [PDF] A conditional tail expectation type risk measure for time series - HAL https://
hal.science/hal-04222405/document
159. [PDF] EXTREMES OF STATIONARY TIME SERIES https://empslocal.ex.ac.uk/people/
staff/ferro/Publications/chapter10.pdf
160. The EAS approach for graphical selection consistency in vector ... https://
onlinelibrary.wiley.com/doi/full/10.1002%2Fcjs.11726
161. [PDF] Lecture 13 Time Series: Stationarity, AR(p) & MA(q) https://
www.bauer.uh.edu/rsusmel/phd/ec2-3.pdf
162. Distributionally Robust Optimization - an overview - ScienceDirect.com https://
www.sciencedirect.com/topics/computer-science/distributionally-robust-optimization
163. Distributionally Robust Optimization https://optimization-online.org/2024/11/
distributionally-robust-optimization/
164. [PDF] Large-Scale Methods for Distributionally Robust Optimization - NIPS https://
proceedings.neurips.cc/paper_files/paper/2020/file/
64986d86a17424eeac96b08a6d519059-Paper.pdf
165. [PDF] Distributionally Robust Predictive Runtime Verification under Spatio https://
www.research-collection.ethz.ch/bitstreams/a7a8b1c0-dfa8-41b3-9bb1-
d44917ceb839/download
166. Decision-Dependent Distributionally Robust Optimization with ... https://arxiv.org/
html/2508.06965v1
167. [PDF] Decision-Dependent Distributionally Robust Optimization with ... https://
crqu.github.io/assets/pdf/decision-dependent-dro.pdf
168. [PDF] Decision-dependent distributionally robust standard quadratic ... - HAL https://
hal.science/hal-05542827v1/file/2026%20Decision-
dependent%20distributionally%20robust%20standard%20quadratic%20optimization
%20with%20Wasserstein%20ambiguity.pdf
169. Distributionally Robust Optimization with Decision-Dependent ... https://
papers.ssrn.com/sol3/papers.cfm?abstract_id=6249652
170. [PDF] Distributionally robust optimization with decision dependent ... https://d-
nb.info/121257494X/34

171. Distributionally robust optimization: a novel approach with decision ... https://
repositorio.uniandes.edu.co/entities/publication/953a7282-7bd0-43bc-
acf5-6ac79fca3df8
172. Online Randomized Distributionally Robust Forecast Combination ... https://
onlinelibrary.wiley.com/doi/10.1111/jtsa.70056
173. Decision-Focused Ambiguity Sets - Emergent Mind https://www.emergentmind.com/
topics/decision-focused-ambiguity-sets
174. Universal Time-Series Representation Learning: A Survey - arXiv https://arxiv.org/
html/2401.03717v2
175. CAUSALITY FROM A DISTRIBUTIONAL ROBUSTNESS POINT OF ... https://
www.researchgate.net/publication/
327132899_CAUSALITY_FROM_A_DISTRIBUTIONAL_ROBUSTNESS_POINT_OF_VIE
W
176. [PDF] Causal Regularization for Distributional Robustness and Replicability https://
baselbiometrics.github.io/home/docs/talks/20191101/4_Buehlmann.pdf
177. Stability selection - Meinshausen - 2010 - Wiley https://rss.onlinelibrary.wiley.com/
doi/10.1111/j.1467-9868.2010.00740.x
178. Wasserstein Distributionally Robust Optimization and Its Tractable ... https://
ideas.repec.org/a/spr/joptap/v208y2026i2d10.1007_s10957-025-02896-x.html
179. [PDF] The influence of unconventional monetary policy tools: An euro area ... https://
www.econstor.eu/bitstream/10419/334269/1/1929077084.pdf
180. Symmetry-Aware Causal-Inference-Driven Web Performance ... - MDPI https://
www.mdpi.com/2073-8994/17/12/2058
181. Stochastic Dual Dynamic Programming and Its Variants: A Review https://
epubs.siam.org/doi/full/10.1137/23M1575093
182. [PDF] arXiv:2407.16800v2 [cs.LG] 18 Jan 2025 https://arxiv.org/pdf/2407.16800?
183. [PDF] Data-driven control, optimization, and decision-making in active ... https://
intra.ece.ucr.edu/~nyu/papers/2025-Data_Driven_Control_ADN-WG.pdf
184. Track: San Diego Poster Session 5 - NeurIPS 2026 https://nips.cc/virtual/2025/loc/
san-diego/session/128335
185. [PDF] Robust Inference on Infinite and Growing Dimensional Time-Series ... https://
www.econometricsociety.org/publications/econometrica/2023/07/01/Robust-
Inference-on-Infinite-and-Growing-Dimensional-Time-Series-Regression/file/
ecta200583.pdf
186. [PDF] Selecting the Relevant Variables for Factor Estimation in FAVAR ... http://
econweb.umd.edu/~chao/Research/research_files/
factor_variable_selection_in_favars-oct-23-2023.pdf

187. [PDF] Online Bootstrap Inference For Policy Evaluation In Reinforcement ... https://
par.nsf.gov/servlets/purl/10418397
188. [PDF] A conditional tail expectation type risk measure for time series | HAL https://
hal.science/hal-04222405v4/file/Real-Valued-TimesSeries-REV.pdf
189. Rademacher complexity for Markov chains: Applications to kernel ... https://
projecteuclid.org/journals/bernoulli/volume-25/issue-4B/Rademacher-complexity-for-
Markov-chains--Applications-to-kernel-smoothing/10.3150/19-BEJ1115.pdf
190. [PDF] data-driven decision making in heterogeneous environments - Will Ma https://
willma353.github.io/papers/beyond_iid.pdf
191. [PDF] data-driven decision making in heterogeneous environments - arXiv https://
arxiv.org/pdf/2206.09642
192. [PDF] the annals - APPLIED STATISTICS https://www.imstat.org/publications/aoas/
aoas_18_1/aoas_18_1.pdf
193. [PDF] Financial Mathematics and Engineering - SIAM https://www.siam.org/media/
sh3nyngs/fm25_abstracts.pdf
194. Off-the-shelf Algorithmic Stability - YouTube https://www.youtube.com/watch?
v=oVOPrd3dSI4
195. Sharp Generalization Bounds under Finite _ Moments - arXiv https://arxiv.org/
html/2606.06855v1
196. [PDF] Collective Stability in Structured Prediction: Generalization from One ... http://
proceedings.mlr.press/v28/london13.pdf
197. [PDF] Hypothesis Set Stability and Generalization - NIPS http://papers.neurips.cc/
paper/8898-hypothesis-set-stability-and-generalization.pdf
198. [PDF] Stability and Generalization in Structured Prediction - People https://
people.cs.vt.edu/~bhuang/papers/london-jmlr16.pdf
199. [PDF] Summary and discussion of: “Stability Selection” https://www.stat.cmu.edu/
~ryantibs/journalclub/stability.pdf
200. [PDF] Transformers as Algorithms: Generalization and Stability in In ... https://
intra.ece.ucr.edu/~oymak/transformers_as_algorithms.pdf
201. [PDF] Stability and Generalization - Journal of Machine Learning Research https://
www.jmlr.org/papers/volume2/bousquet02a/bousquet02a.pdf
202. Understanding the Theoretical Foundations of Deep Neural ... - arXiv https://
arxiv.org/html/2603.18331v1
203. Domain Generalization in Time Series Forecasting https://dl.acm.org/doi/full/
10.1145/3643035
204. Signed Networks: theory, methods, and applications - arXiv https://arxiv.org/html/
2511.17247v2

205. Methods for Knowledge Graph Construction from Text Collections https://arxiv.org/
     html/2603.25862v1
206. [PDF] InfoGram and Admissible Machine Learning - arXiv https://arxiv.org/pdf/
     2108.07380
207. AI Infrastructure Sovereignty - arXiv https://arxiv.org/html/2602.10900v4
208. Modeling Regime Structure and Informational Drivers of Stock ... https://arxiv.org/
     html/2504.18958v1
209. Phase Transitions in Attention: A Bayesian Theory of Copy Head ... https://arxiv.org/
     html/2606.12058v1
210. [PDF] arXiv:2504.18958v1 [q-fin.ST] 26 Apr 2025 https://arxiv.org/pdf/2504.18958?
211. [PDF] Intelligent Computing Social Modeling and Methodological ... - arXiv https://
     arxiv.org/pdf/2410.16301
212. [PDF] Wasserstein Distributionally Robust Estimation in High Dimensions https://
     arxiv.org/pdf/2206.13269
213. [PDF] Statistics of Robust Optimization: A Generalized Empirical ... https://
     par.nsf.gov/servlets/purl/10382316
214. Statistical analysis of multivariate discrete-valued time series https://
     www.sciencedirect.com/science/article/pii/S0047259X2100083X
215. Robust optimization approaches in inventory management https://
     www.tandfonline.com/doi/pdf/10.1080/24725854.2024.2381713
216. Generalization Bounds with Minimal Dependency on Hypothesis ... https://
     openreview.net/forum?id=2bE4He5a9eQ
217. [PDF] On Generalization and Regularization via Wasserstein ... https://optimization-
     online.org/wp-content/uploads/2022/12/WDRO-20221212.pdf
218. [PDF] Lasso guarantees for beta-mixing heavy-tailed time series https://
     www.ambujtewari.com/research/wong20lasso.pdf
219. [PDF] Stability Bounds for Stationary ϕ-mixing and β-mixing Processes https://
     research.google.com/pubs/archive/36944.pdf
220. Lasso Guarantees for β-Mixing Heavy Tailed Time Series - arXiv https://arxiv.org/
     abs/1708.01505
221. The blockwise bootstrap in time series and empirical processes https://
     www.semanticscholar.org/paper/The-blockwise-bootstrap-in-time-series-and-
     B%C3%BChlmann/d542c63b3688b87f5371ae395167e7e04492497d
222. (PDF) Data-Driven Distributionally Robust Optimization Using the ... https://
     www.researchgate.net/publication/277023281_Data-
     Driven_Distributionally_Robust_Optimization_Using_the_Wasserstein_Metric_Perform
     ance_Guarantees_and_Tractable_Reformulations

223. [PDF] Wasserstein Distributionally Robust Optimization: Theory and ... https://
optimization-online.org/wp-content/uploads/2019/08/7347.pdf
224. [PDF] © 2025 Zhuangzhuang Jia - IDEALS https://www.ideals.illinois.edu/items/
139562/bitstreams/450654/data.pdf
225. 2019 TutORial: Wasserstein Distributionally Robust Optimization https://
www.youtube.com/watch?v=vozmvt_glQs
226. keynote talks - CMStatistics https://www.cmstatistics.org/EcoSta2026/
fullprogramme.php
227. [PDF] A non-stationary paradigm for the dynamics of multivariate financial ... https://
www.math.cmu.edu/~reha/Pss/HST.pdf
228. [PDF] Stochastic Control and Optimization with Nonstationary Data https://
www.epoc.org.nz/papers/
Stochastic%20Control%20and%20Optimization%20with%20Nonstationary%20Data.p
df
229. Distributionally Robust Optimization via Generative Ambiguity ... - arXiv https://
arxiv.org/html/2602.08976v1
230. [PDF] Data-driven chance constrained optimization under wasserstein ... https://
pure.rug.nl/ws/files/107591666/08814677_1_.pdf
231. Wasserstein Distributionally Robust Optimization for Chance ... - MDPI https://
www.mdpi.com/2227-7390/13/13/2144
232. [PDF] Wasserstein Distributionally Robust Optimization https://www.dcsc.tudelft.nl/
~mohajerin/Publications/journal/2019/DRO_tutorial.pdf
233. Shift-Aware Gaussian-Supremum Validation for Wasserstein-DRO ... https://
neurips.cc/virtual/2025/132574
234. [PDF] arXiv:2502.02710v1 [stat.ML] 4 Feb 2025 https://arxiv.org/pdf/2502.02710?
235. 同步arXiv全量数据，AI总结、翻译，覆盖人工智能、机器人 - arXivDaily https://
arxivdaily.com/?major=CS&subcat=cs.LG&search_in=all
236. Top Papers This Week - Machine Learning Papers https://
machinelearningpapers.com/2026-06-07.html
237. 同步arXiv全量数据，AI总结、翻译，覆盖人工智能、机器人 https://arxivdaily.com/?
major=CS&subcat=cs.AI&search_in=all
238. Invariance & Causal Representation Learning: Prospects and ... - arXiv https://
arxiv.org/html/2312.03580v1
239. Track: Poster Session 2 - aistats 2026 https://virtual.aistats.org/virtual/2025/session/
8799
240. [PDF] Outlier-Robust Wasserstein DRO https://papers.neurips.cc/paper_files/paper/
2023/file/c67b138497305835e76fdedd48dd4e59-Paper-Conference.pdf

241. Refined Wasserstein Distributionally Robust Optimization for ... https://
pubsonline.informs.org/doi/10.1287/ijoc.2024.0547
242. Automatic Block-Length Selection for the Dependent Bootstrap https://
www.researchgate.net/publication/227357033_Automatic_Block-
Length_Selection_for_the_Dependent_Bootstrap
243. [PDF] Automatic Block-Length Selection for the Dependent Bootstrap ∗ https://
www.math.ucsd.edu/~politis/SBblock-revER.pdf
244. [PDF] The mathematical machinery of causal inference - PhilArchive https://
philarchive.org/archive/ELITMM
245. [PDF] Lecture 3: Causality and Interventions https://people.math.ethz.ch/
~buhlmann/teaching/lecture3.pdf
246. Stability Bounds for Non-i.i.d. Processes - NIPS https://papers.nips.cc/paper/3239-
stability-bounds-for-non-iid-processes
247. [PDF] Exact Generalization Guarantees for Wasserstein Distributionally ... https://
wazizian.fr/assets/pdf/poster_wdro.pdf
248. Necessary and sufficient conditions for causal feature selection in ... https://
www.amazon.science/publications/necessary-and-sufficent-conditions-for-causal-
feature-selection-in-time-series-with-latent-common-causes
249. Stable Causal Feature Selection based on Direct Causal Effect ... https://
www.researchgate.net/publication/
369589602_Stable_Causal_Feature_Selection_based_on_Direct_Causal_Effect_Estimat
ion
250. A Language Model Perspective on Time Series Foundation Models https://arxiv.org/
html/2507.00078v1
251. [PDF] Lipschitz Continuity in Model-based Reinforcement Learning http://
proceedings.mlr.press/v80/asadi18a/asadi18a.pdf
252. [PDF] STEM-LTS: Integrating Semantic-Temporal Dynamics in LLM-driven ... http://
home.ustc.edu.cn/~pengkun/files/Publications/AAAI2025_2.pdf
253. From Synthetic Regime Shifts to Financial Markets - ResearchGate https://
www.researchgate.net/publication/400369214_Test-Time_Adaptation_for_Non-
stationary_Time_Series_From_Synthetic_Regime_Shifts_to_Financial_Markets
254. Test-Time Adaptation for Non-stationary Time Series - IDEAS/RePEc https://
ideas.repec.org/p/arx/papers/2602.00073.html
255. [PDF] Discrepancy-Based Theory and Algorithms for Forecasting Non ... https://
cs.nyu.edu/~mohri/pub/tsj.pdf
256. Applied Probability Seminar Series - Department of Statistics https://
stat.columbia.edu/applied-probability-seminar-series/

257. Publications - Jalal Kazempour https://www.jalalkazempour.com/publications
258. Exact Generalization Guarantees for (Regularized) Wasserstein ... https://neurips.cc/
     virtual/2023/poster/70777
259. Finite-Sample Guarantees for Wasserstein Distributionally Robust ... https://
     www.researchgate.net/publication/344180627_Finite-
     Sample_Guarantees_for_Wasserstein_Distributionally_Robust_Optimization_Breaking_
     the_Curse_of_Dimensionality
260. Data-driven distributionally robust optimization using the ... https://
     research.tudelft.nl/en/publications/data-driven-distributionally-robust-optimization-
     using-the-wasser/
261. Derandomised knockoffs: leveraging e-values for false discovery ... https://
     academic.oup.com/jrsssb/article/86/1/122/7262479
262. [PDF] False Discovery Proportion control for aggregated Knockoffs - HAL https://
     hal.science/hal-04250621v1/document
263. [PDF] model-free methods for multiple testing and predictive inference a ... https://
     stacks.stanford.edu/file/druid:kf427yp0284/ren_thesis-augmented.pdf
264. [PDF] Lipschitz Continuity in Deep Learning: A Systematic Review of ... https://
     openreview.net/pdf?id=pRZ0RKl11f
265. [PDF] Generalization Analysis for Contrastive Representation Learning https://
     arxiv.org/pdf/2302.12383
266. [PDF] SOME FUNDAMENTAL ASPECTS ABOUT LIPSCHITZ ... https://
     proceedings.iclr.cc/paper_files/paper/2024/file/
     123d3e814e257e0781e5d328232ead9b-Paper-Conference.pdf
267. [PDF] Enhancing Generalization in Data-Efficient GANs via lipsCHitz https://
     openaccess.thecvf.com/content/CVPR2024/papers/
     Ni_CHAIN_Enhancing_Generalization_in_Data-
     Efficient_GANs_via_lipsCHitz_continuity_constrAIned_CVPR_2024_paper.pdf
268. Approximation Theory for Lipschitz Continuous Transformers https://
     www.researchgate.net/publication/
     400894670_Approximation_Theory_for_Lipschitz_Continuous_Transformers
269. [PDF] On the Stability of Neural Networks in Deep Learning https://
     theses.hal.science/tel-05398597v1/file/2025UPSLD022.pdf
270. [PDF] Lipschitz Lifelong Reinforcement Learning https://cdn.aaai.org/ojs/
     17006/17006-13-20500-1-2-20210518.pdf
271. Research - Furong Huang https://furong-huang.com/research/
272. [PDF] Invariance, Causality and Robustness - SfS – Seminar for Statistics https://
     stat.ethz.ch/Manuscripts/buhlmann/STS721.pdf

273. P-K-GCN: Physics-augmented Koopman-enhanced Graph ... - arXiv https://arxiv.org/
html/2606.19303v1
274. Track: Poster Session 2 - NeurIPS 2026 https://neurips.cc/virtual/2023/session/
74070
275. [PDF] Tight Bounds and Fundamental Impossibility for ... - OpenReview https://
openreview.net/pdf/f0d50062faa1d634b043fc525f6f628a20876c48.pdf
276. Technical Program for Monday August 24, 2026 - IFAC Papercept https://
ifac.papercept.net/conferences/conferences/IFAC26/program/
IFAC26_ContentListWeb_1.html
277. [PDF] MARS: MEMORY-ADAPTIVE ROUTING FOR ... - OpenReview https://
openreview.net/pdf?id=GGrLeik2qo
278. [PDF] Signature Methods in Machine Learning https://ora.ox.ac.uk/objects/
uuid:282745c3-9835-4a96-ad7b-fb3631c33678/files/sww72bd65r
279. [PDF] Log Signatures in Machine Learning - UCL Discovery https://
discovery.ucl.ac.uk/10156498/2/Shujian_Liao_PhD_Thesis.pdf
280. Track: Poster Session 1 - ICML 2026 https://icml.cc/virtual/2024/session/35591
281. AHGT-DFD: Adaptive Hierarchical Graph Transformer for Dynamic ... https://
www.computer.org/csdl/journal/tq/2026/02/11217214/2b4URQKzSDK
282. Graph Convolutional Networks: A Critical Review - ResearchGate https://
www.researchgate.net/publication/
400693118_Graph_Convolutional_Networks_A_Critical_Review
283. CityGuard: Graph-Aware Private Descriptors for Bias-Resilient ... https://arxiv.org/
html/2602.18047v1
284. Statistics - Academus scientific article reader https://academ.us/list/stat/
285. Notes for Weekly/Monthly Good News - Computer Sciences https://www.cs.wisc.edu/
notes-for-weekly-monthly-good-news/
286. SMGI: A Structural Theory of General Artificial Intelligence Preprint https://arxiv.org/
html/2603.07896v1
287. [PDF] SMGI: A Structural Theory of General Artificial Intelligence - arXiv https://
arxiv.org/pdf/2603.07896
288. [PDF] Sample Weight Averaging for Stable Prediction - arXiv https://arxiv.org/pdf/
2502.07414