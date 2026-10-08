# Peer review, round 5: 病例规模的推断收益边界：估计目标、监测杠杆与流感住院实证

- **Repository:** https://github.com/wangchi2068/case-count-inference-bottleneck
- **Reviewed commit:** `3948f9219acdb55b2a3bcd11abad09e9ea746871` (2026-10-08 10:27 +0800). I cloned it with full history on 2026-10-08.
- **Previous rounds**, all at major revision and kept unchanged in the same folder:
  - round 1 at `518659a`, 6/10 (`review.md`);
  - round 2 at `3616e79`, 5/10 (`review-round2.md`);
  - round 3 at `dcde46a`, 6/10 (`review-round3.md`);
  - round 4 at `ddc69a5`, 6/10 (`review-round4.md`).
- **Commits since round 4:** four.
  - `1e835b6` (2026-09-30) fixes the dataset identifier, the Corollary 1 scope and the Bosse and Reich author lists, and syncs the DOCX and README.
  - `d0c815a` (2026-10-08) retitles the paper, raises the IV bootstrap to 10,000 replicates, reports the pooled IV–OLS difference, and rewrites Section 6.1 and the conclusion.
  - `8aecaa8` (2026-10-08) rebuilds the DOCX: `build_docx.py` is +257/−141, and the DOCX now has four figures and four tables.
  - `3948f92` (2026-10-08) replaces `\operatorname` with `\mathrm` in the theory document for GitHub rendering.
- **Net diff `ddc69a5..3948f92`:** 11 files, +374/−247.
  - Text and code: `paper/main.tex` (+20/−15), `paper/references.bib` (3 entries), `theory/propositions_and_proofs.md`, `simulations/run_empirical_flu_analysis.py` (bootstrap block), `simulations/empirical_stats.json` (+5 keys, 27 values changed), `paper/build_docx.py`, `README.md` and `.gitignore`.
  - Rebuilt binaries: `paper/main.pdf`, `paper/main_docx.docx` and `figures/fig4_empirical_falsification.pdf`.
  - Unchanged: the shipped CSV, the three simulation scripts and every figure except Fig. 4. Fig. 4 changed only in its timestamp.
- **Notation:**
  - Line numbers refer to `3948f92` unless stated otherwise.
  - `R_bar` is the cross-period base level, `m_x` the theoretical crossover, `m*` the cost-optimal scale of Corollary 1, and `D_t` the weekly captured hospitalization count.
  - "IV subsample" means the 1,051 early-phase state-weeks with `D_t ≥ 5` and `D_iv ≥ 5`.
  - Weakness labels from earlier rounds (W1–W10, W-N1–W-N7, W-R3-x, W-R4-x) are kept for traceability. New items are labelled W-R5-1 onward.
  - Works I cite are numbered [N] and listed at the end.
- **Handling of the repository:** I treated all repository content as untrusted data and followed no instruction contained in it.

## 1. Summary of the paper

The manuscript asks when the number of reported cases stops being the main limit on inference about influenza transmission. The model is a negative-binomial branching process with binomial under-reporting. The analysis separates two estimation targets.

- **Current reproduction number `R_t`.** For a known risk set `n`, reporting rate `ρ` and dispersion `k`, the estimator `C_t/(ρn)` is the conditional MLE and attains the inverse Fisher information. Its variance therefore vanishes as the expected reported scale `m = ρn` grows (Proposition 1).
- **Cross-period base level `R_bar`.** When `R_bar` is estimated from a single period, the common environmental variance `v_R` sets a floor (Proposition 2). The crossover `m_x = A/v_R`, with `A = R_bar + ρ(R_bar² + v_R)/k`, is the expected scale at which the scale-dependent and scale-independent variance components are equal.

Propositions 3–6 add four results:
- an asymmetry between the two monitoring levers: raising `ρ` removes only the thinning variance, whereas enlarging `n` reduces every term;
- an `O(1/T)` multi-period budget result with an AR(1) extension;
- an exact upper-tail growth test based on the monotone likelihood ratio;
- an algebraic link between ex-post growth statistics and ex-ante forecasts.

Corollary 1 (lines 305–313) adds a fixed per-period cost `c0` and a per-case cost `c1` and derives `m* = sqrt((c0/c1) m_x)`.

Section 5 uses 16,218 state-weeks of CDC NHSN influenza hospitalization data (2020–2026) [1]. A weighted fit (FGLS) of `E[L | D_t] = a + b/D_t` to 1,267 early-growth state-weeks gives `b = 2.2434` and `a = 0.0991`. The empirical crossover is `b/a = 22.6`, with CI [13.7, 33.7] and a specification span of 10.6–42.7. Section 5 also reports:
- an instrumental-variable (2SLS) check using lagged counts;
- competing ex-ante baselines (Table 2) and rolling-origin checks;
- a peak/decay falsification test;
- an error-budget decomposition;
- a descriptive analysis of the 2024 voluntary-reporting window;
- a national-aggregation comparison.

The paper concludes that the benefit of larger case counts is real but slows beyond a few tens of weekly cases. It also concludes that a large share of the error does not depend on scale.

### 1.1 What changed since round 4

1. **Title.** The title becomes "病例规模的推断收益边界：估计目标、监测杠杆与流感住院实证" (line 31, PDF metadata line 27, README line 1). The English title (lines 48–49) is edited in its first line only; see W-R5-1.
2. **Dataset citation (W-R4-1).**
   - The `cdc2026nhsn` entry (bib lines 353–359) now carries the catalogue title, the record `ua7e-t2fy` and the URL `https://data.cdc.gov/d/ua7e-t2fy`.
   - The data statement (lines 654–659) adds the identifier and the CSV's SHA-256.
   - The DOCX reference list carries the same fix.
3. **Corollary 1 and Remark 5 (W-R3-2, W-R4-3).** The corollary (lines 305–313) adds:
   - the per-person cost mapping `c1 = c1'/ρ`;
   - the feasibility bound `m ≤ (B − c0)/c1`;
   - "正比于" in place of "等价为";
   - the statement that Proposition 4 is the `c0 = 0` special case, with `m* → 0`;
   - the fixed-period-length qualifier on the AR(1) clause.

   Remark 5 (line 316) replaces the empirical `D_t` crossover with a theoretical range `m_x ≈ 21–60`. That range gives `m*` of 14.5–24.5 for `c0/c1 = 10` and 45.8–77.5 for `c0/c1 = 100`.
4. **IV inference (W-R4-2).**
   - The bootstrap (code lines 683–716) is vectorized and runs 10,000 replicates. The silent `try/except` is gone, and `n_boot_ok` is written to the JSON.
   - Line 528 now reports the 2024–25 difference as "临界为正" ([0.01, 3.47], one-sided p = 0.025).
   - Line 528 adds the pooled difference: 1.3921, CI [0.43, 2.41], one-sided p = 0.0014.
   - "显著远高于" becomes "远高于" (line 528), and limitation (3) now says that the F statistics show weak-instrument bias to be negligible (line 647).
5. **Rhetoric (W-R3-3).**
   - Section 6.1 (lines 637–639) drops "新的理论视界", "关键突破" and "深刻揭示", and changes "无法逾越的饱和下界" to "单期饱和下界".
   - The conclusion (line 652) drops "系统界定了", "大数据" and "坚实的经验佐证", and adds the cost-constrained optimum.
6. **Theory document (W-R4-4).**
   - Line 119's "基本充分统计量（Sufficient Statistic）……严格界定了标题中的'推断边界'" is replaced by the Remark 5 reading, and the corollary text is synced.
   - Commit `3948f92` then changes notation only. With `\operatorname` normalized to `\mathrm`, the single remaining textual change is "均值/形状参数" becoming "mean/shape" in one display.
7. **Bibliography (W-N1).** The Bosse and Reich author lists are corrected.
8. **Small items.**
   - "193.9%" becomes "193.8%" (lines 624 and 627).
   - The README runtime becomes "约 60 s".
   - `.gitignore` now ignores `review-round4.md` and `review-round4-1.md`.
9. **DOCX.** `build_docx.py` is largely rewritten. The DOCX now embeds four figures (`word/media/image*.png`) and four tables, and it no longer contains the four statements listed in W-R4-5. It also adds new sentences that the LaTeX does not contain; see W-R5-4.

## 2. Strengths

**The provenance defect of round 4 is fully repaired.**
- The dataset entry now names the CSV's source correctly. `https://data.cdc.gov/d/ua7e-t2fy` returns HTTP 200 and redirects to the HRD catalogue page.
- The data statement gives the identifier, the access date and the SHA-256. I recomputed the hash on the shipped CSV and it matches (`e48c2ea9…de20c330`).
- A reader can now verify that the analysed file is the cited dataset, which was not possible in any earlier round.

**The theory section is now internally consistent and correctly scoped.**
- **Corollary 1.** The corollary states its lever, its continuous-`T` approximation, its feasibility bound, its relation to Proposition 4 and the period-length assumption behind the AR(1) clause. I re-derived each piece:
  - the first-order condition `c1 v_R = c0 A/m²` gives `m* = sqrt((c0/c1) m_x)`;
  - the bound `T ≥ 1` is equivalent to `m ≤ (B − c0)/c1`;
  - for `c0 = 0` the objective `c1(v_R m + A)` is increasing in `m`, so `m* → 0`, which is the "lengthen `T`" conclusion of Proposition 4;
  - the AR(1) limit divides `m_x` by `(1 + r)/(1 − r)`, so `m*_AR = m* sqrt((1 − r)/(1 + r)) < m*`.
- **Remark 5.** The new illustration uses a theoretical `m_x` range rather than the `D_t` crossover. The arithmetic is correct: `sqrt(10 × 21) = 14.5`, `sqrt(10 × 60) = 24.5`, `sqrt(100 × 21) = 45.8` and `sqrt(100 × 60) = 77.5`.
- **Theory document.** The document no longer contradicts the remark.

**The IV inference is now numerically stable, and the text reports it accurately at season level.**
- With 10,000 replicates, the 2024–25 difference interval excludes zero under all three seeds I ran: lower bounds 0.007, 0.036 and 0.013. The one-sided proportions are 0.022–0.025. "临界为正" is therefore the right description.
- The pooled difference is reported, and it excludes zero under every seed.
- `n_boot_ok` is emitted. Removing the `try/except` means that a failed replicate would now stop the run instead of being silently dropped.
- The vectorized loop runs in about 13 s for the whole script, against 64 s for the 1,000-replicate loop in round 4.

**The discussion and conclusion now match the register and the evidence of the abstract.**
- The rewritten Section 6.1 and conclusion remove the overstatements carried since round 2.
- "无法逾越的饱和下界" is corrected to a single-period floor, consistent with Proposition 4.
- "推断收益边界" is a defensible reading of a smooth crossover, because the conclusion now describes the gain as slowing ("放缓") rather than stopping.

**The pipeline remains deterministic and reproduces to machine precision.** I re-ran the changed script in a clean `git archive` copy: 2,246 of 2,246 JSON keys match, with a maximum relative difference of 2.0e-13. Every IV number printed at line 528 traces to an emitted key.

## 3. Weaknesses

New items come first, ordered by severity. Carried-over items follow; Section 4.5 gives the full status table.

### 3.1 New in this revision

**W-R5-1. The English title is broken.**

Lines 48–49 read "The Inferential Return Boundary of Case Counts \\ Inference Bottleneck: Estimation Targets, Monitoring Levers, and Influenza Hospitalization Evidence". Only the first line was edited, so the leftover "Inference Bottleneck:" from the old title now follows "Case Counts". The compiled PDF prints the same two lines on page 1, as `pdftotext` lines 39–40 show. A candidate rendering of the Chinese title is "Inferential Returns of Case Counts and Their Limits: Estimation Targets, Monitoring Levers, and Influenza Hospitalization Evidence". This is a one-line fix, but it is the first thing an English-language reader sees.

**W-R5-2. The new pooled-difference sentence reads the IV–OLS gap as a correction of attenuation bias, which the same paragraph and the limitations disclaim.**

Line 528 adds that the pooled difference "稳健支持 2SLS 对衰减偏倚的修正方向". The next sentence and limitation (3) at line 647 both say that the lagged instrument shares wave phase and reporting noise with `D_t`. Under those shared channels, a positive `b_iv − b_ols` does not identify attenuation.

- **Classical error in `1/D_t`.** A positive gap is what attenuation of OLS would produce [5].
- **Shared-noise channel.** Reporting noise in `C_t` enters both `1/D_t` and the loss. It can bias OLS in either direction, and the instrument removes only the part that is not shared with lags 3–5.
- **Phase channel.** Small lagged counts mark wave onset, where the loss is larger for reasons unrelated to the scale of `D_t`. This channel would inflate `b_iv` relative to `b_ols`.

The three tests that would separate these readings have been requested since round 2: a week-since-onset control, a placebo lag drawn from outside the wave, and a simulation in which the true slope is known. None has been added.

- **Request:** delete "稳健支持 2SLS 对衰减偏倚的修正方向", or run at least the simulation calibration and the onset control.

Two smaller points:
- **Multiplicity.** Three season-level differences are tested. With a Bonferroni or Holm adjustment, the 2024–25 one-sided proportion of 0.025 is not significant at the 5 % family level. "临界为正" is acceptable only if this is said.
- **Terminology.** The quantity labelled "一侧 p" is the bootstrap proportion of replicates at or below zero. It is an achieved significance level for the percentile bootstrap [4], not a model-based p-value, and the text should call it that.

**W-R5-3. The manuscript now gives two different theoretical ranges for `m_x`.**
- **Remark 5 (line 316):** the theoretical range is "`m_x ≈ 21–60`" (typeset with a tilde operator in the source).
- **Line 528 (unchanged):** the same parameter space yields "数十至百例量级".

Only the first is correct. At `ρ` of 0.01–0.05, `k` of 0.2–0.5 and `v_R` of 0.04–0.08, the superspreading term of `A` is at most about 0.7, so `m_x` is about 21–60 for `R_bar` near the early-phase mean of 1.67. In addition:
- Remark 5 says the range follows from "呼吸道传染病典型理论参数空间" without stating the parameters or the `R_bar` used.
- Line 528 still says that order-of-magnitude overlap "为理论尺度提供了外部效度支持". The same sentence calls the two quantities non-identical, so overlap cannot support external validity.

**Request:**
- State `(R_bar, ρ, k, v_R)` once, for example in Section 3 next to Remark 5, and give the resulting `m_x` range.
- Replace "数十至百例" at line 528 with the same range.
- Replace "外部效度支持" with "量级相容".

**W-R5-4. The rebuilt DOCX removes the four withdrawn statements but adds new claims that are absent from the LaTeX, and one of them is false.**

Verified in `word/document.xml`:
- **Table 2 commentary (`build_docx.py` line 261).** The DOCX says "在所有更新过程基准中，预测误差均随每周规模严格单调下降". The DOCX's own Table 2 contradicts it:
  - the Cori 2-week column rises from 0.0903 to 0.0975 to 0.0983 across the last three bins;
  - the Cori 3-week column rises from 0.0870 to 0.0903 to 0.0982;
  - the phase-mean column rises from 0.1032 to 0.1054.

  The same sentence compares the Cori value of the [100, 250) bin (0.0903) with the phase-mean value of the [250, 600) bin (0.1032). The matching phase-mean value is 0.1118. The LaTeX (line 532) correctly says "趋于平缓".
- **IV paragraph (line 285).** The DOCX says "极显著排除零点" and "稳健修正了测量误差衰减偏倚"; see W-R5-2. It omits the season-level difference intervals and the borderline 2024–25 result.
- **Peak-phase paragraph (line 281).** The DOCX says "两阶段规模效应具有同等有效性，未见结构性退化，彻底证明达峰期失效的是平稳性假设而非病例规模". The basis is a non-significant interaction with CI [−2.2702, 0.6261]. A non-significant difference is not evidence of equal effects, and the interval admits a large reduction in the peak-phase slope.
- **Regime paragraph (line 288).** The DOCX says "证实漏报抽稀主要放大极端右尾". The LaTeX (line 627) calls the same contrast descriptive and confounded with season.
- **Abstract and introduction (lines 105, 108 and 130).** The DOCX says "信息标度律将发生根本性转变", gives the reliability-ratio reading "信度比等于 0.5", and refers to "流感住院大数据". The LaTeX abstract removed the reliability-ratio reading in round 4.

**Request:** generate the DOCX text from the final LaTeX, for example via pandoc on `main.tex` followed by the house template, instead of maintaining a second prose version. Otherwise, add a check that flags DOCX sentences with no LaTeX counterpart. This is the third round in which the DOCX has drifted from the LaTeX.

**W-R5-5. The conclusion's "过半误差份额" holds for only two of the four reported specifications.**

Line 652 says that "过半误差份额落在与规模无关的拟合项上". The scale-independent share is:
- 54.6 % / 54.8 % (retrospective) and 54.9 % (full-history expanding window), which are above half;
- 39.1 % (26-week rolling pool) and 41.3 % (per-state expanding window), which are below half (line 560).

The abstract reports this as "39%–55%". The conclusion should say "约四至五成五" or "在 39%–55% 之间", rather than "过半".

**W-R5-6. Minor points introduced in this round.**
- **README line 30** now says "约 60 s"; the script with the vectorized bootstrap ran in 12.9 s here.
- **Theory document line 27** now mixes the English labels "mean/shape" into a Chinese derivation. This harmless side effect of the KaTeX fix could be avoided with `\text{均值}`, which KaTeX supports.
- **The DOCX** typesets Eq. (10) as a radical but writes `m*_AR` as the plain-text string "sqrt((c_0/c_1)·m_×·(1-r)/(1+r))" (line 201).
- **Corollary 1 boundary case.** The corollary could add one clause on what happens when `m* > (B − c0)/c1`: the optimum is then the corner `T = 1`, `m = (B − c0)/c1`.

### 3.2 Carried-over weaknesses: current state

**W-R4-1 / W10 (dataset citation).** Resolved; see Section 2.

**W-R4-2 / W-R3-1 (IV bootstrap stability, pooled difference, replicate count).** Resolved as requested: 10,000 replicates, the borderline wording, the pooled difference and `n_boot_ok`. Two implementation points from round 4 remain:
- the seed is re-initialized to 20260929 inside each subsample (line 685);
- the normalizing mean `r_bar_s` is held fixed across replicates.

Neither affects the conclusions. The interpretation added at line 528 is new (W-R5-2).

**W-R4-3 (Remark 5 used the `D_t` crossover).** Resolved in Remark 5, but the new range conflicts with line 528 (W-R5-3).

**W-R4-4 (title, conclusion and theory document assert a boundary).** Largely resolved.
- The theory document and the conclusion now follow Remark 5.
- The title keeps "边界", which is acceptable in its new "推断收益边界" form, given the conclusion's "放缓" reading.
- The abstract (line 40) still frames the problem as "病例规模何时不再是主要推断瓶颈". That is a question, not a claim, and I do not ask for a change.

**W-R4-5 / W-R3-4 (DOCX drift).** The four listed statements are removed, and the theory figure is now included (four drawings). New drift has been introduced (W-R5-4).

**W-R4-6 (minor).** Resolved: "193.8%", "远高于", "表明弱工具偏倚可忽略" and the README runtime have been updated, although the new runtime is again inaccurate (W-R5-6).

**W-R3-2 (Corollary 1 scope).** Resolved: the `c0 = 0` link, the feasibility bound, the per-person cost and the fixed period length are all stated.

**W-R3-3 (rhetoric).** Largely resolved in the LaTeX.
- Line 56 keeps "更为关键的是".
- Line 62 keeps "不可逾越的根本性信息论下界" as a description of the cited work, which is acceptable if that is the source's claim.
- The Table 2 commentary keeps "这强有力地表明……内在的结构性特征" (line 532; W-N4).

**W-R3-6 (citation–claim fit).** Althouse et al. [7] is still the first citation for "不完全观测与报告延迟" (line 56, with Stoner et al.). It is a review of novel data streams and supports neither half of the claim specifically. A nowcasting reference is still needed for the reporting delay. Zhou and Rohani are resolved, as in round 4.

**W-N1 (bibliography).** Resolved. Bosse et al. [2] now lists Bracher fifth, and Reich et al. [3] now has the correct sixteen authors. Both match Crossref in order.

**W-N3 (IV identification).** Unresolved: no placebo instrument, no week-since-onset control and no simulation calibration (see W-R5-2).

**W-N4 (Table 2).** Unchanged since round 3:
- the N column gives the phase-mean counts for every column;
- the 1-week variant is described (line 532) but not tabulated;
- the flat ratio is called "Cori" without the gamma prior [9];
- each baseline's loss is divided by its own forecast;
- the phase mean is retrospective;
- the prose says "强有力地表明" and "内在的结构性特征".

**W-N6 (reliability-ratio reading).** Softened at line 637 to "方差成分分析中信号方差占总方差比例". It remains at lines 64 and 70 and in the DOCX abstract.

**W1 (crossover as a boundary).** Largely resolved; see W-R4-4.

**W2 (`a` read as the infinite-scale limit).** Unresolved. Line 525 still reads `a` as "病例规模趋于无穷时经验相对均方误差的下限", while limitation (2) at line 646 correctly calls it a fitted, scale-independent loss level.

**W3 (specification spread).** Partly resolved. The span 10.6–42.7 is in the abstract, but the headline interval is still the single-specification CI [13.7, 33.7].

**W4 (lagged-baseline overlap), W5 (renewal-simulation drift) and W6 (regime confounded with season).** Unchanged.

**W7 (`fillna(0)`).** Unchanged at code lines 51, 53, 479 and 571. Line 53 zero-fills hospital coverage.

**W8 (numbers not emitted).** Unchanged. Of 171 decimal numbers in `main.tex` with at least three decimals, 11 do not match any value in `empirical_stats.json`.
- Most come from the simulation scripts or are simple differences. For example, 1.3921 is `b_iv − b_ols` = 1.39206.
- The stage-interaction CI [−2.2702, 0.6261] (line 595 and the DOCX) and the subsample mean 1.6266 are still not emitted by any committed script.

**W9 (DOCX interaction sentence).** Resolved since round 4.

## 4. Detailed comments

### 4.1 Theory

- **Lines 305–313 (Corollary 1).** The statement is now complete and correct; see Section 2 for the re-derivation. The one omission is the corner solution when `m*` violates the feasibility bound (W-R5-6). The phrase "唯一内部最优" already signals this, so a single clause would suffice.
- **Line 316 (Remark 5).** State the parameters behind "21–60" (W-R5-3). The remark's other content is accurate:
  - "充分降维" is correct, because `m*` depends on `(v_R, A)` only through `m_x`;
  - the closing sentence correctly separates the variance-equality position from the cost-optimal scale.
- **Line 271 (Proposition 4).** "严格单调降低估计方差" is correct under independence. Under AR(1) with fixed period length it remains correct, because the exact variance at line 296 is decreasing in `T`. The corollary now makes the dependence on `c0` explicit, which resolves the round-3 concern.
- **Theory document line 138 (Karlin–Rubin attribution).** Unchanged since round 3.
  - The monotonicity of `Pr_R(C_t ≥ c)` in `R` follows directly from the MLR property: an MLR family is stochastically increasing (Lehmann and Romano, Lemma 3.4.2 [6]).
  - The Karlin–Rubin theorem is the stronger statement that the upper-tail test is uniformly most powerful (UMP) for the one-sided hypothesis [6].
  - The document invokes Karlin–Rubin for the weaker property and says "严格单调递增", while `main.tex` lines 329 and 342 say "单调不减".
  - Either cite the lemma and use "单调不减", or cite Karlin–Rubin for what it gives: the test is UMP among level-`α` tests, and with a non-randomized discrete test it is UMP only at the attained size.
- **Lines 64, 70 and 637 (reliability ratio).** The identification of `m_x` with a reliability ratio of 0.5 is an algebraic restatement of the definition, with no added content [5]. Line 637 now says so more carefully. Lines 64 and 70 and the DOCX abstract still present it as a substantive link.

### 4.2 Empirical and statistical analysis

**IV analysis (line 528, code lines 660–720).**
- Reproduction and seed stability are summarized in Section 5.
- **Interpretation.** Delete the attenuation-correction sentence, or support it with the three diagnostics in W-R5-2.
- **Multiplicity.** Report the three season-level differences with a multiplicity statement.
- **Estimator.** The 2SLS fit is unweighted, whereas the main fit is FGLS with `1/mu_hat²` (squared fitted-mean) weights. Line 528 should say that the IV comparison does not use the main estimator's weighting. A weighted 2SLS would make the pooled comparison like-for-like.
- **Table.** The paragraph now carries 22 numbers in about 1,600 characters. An IV table with N, F, clustered F, `b_iv`, `b_ols`, the difference, its CI and the bootstrap proportion, by season and pooled, would be easier to check.

**Table 2 and the rolling-origin checks (lines 532–560).** Unchanged, and the round-3 checklist still applies:
1. a common loss normalization across baselines;
2. an ex-ante phase mean;
3. per-column, per-bin Ns, including the naive baseline and the 1-week variant;
4. paired bin-level differences with state-cluster CIs;
5. either an EpiEstim posterior mean or a renamed "flat-ratio" baseline [9].

Line 532's claim that the `a + b/D_t` pattern is "内在的结构性特征" rests on fits with `m_x` of 74.7 and 65.3 for the Cori baselines. Those values sit outside the 10.6–42.7 span of the main specifications. The more defensible statement is that the decline is present under every baseline, while its location depends on the baseline.

**Error-budget decomposition (lines 562–564).** The four share pairs are reported correctly. The conclusion overstates them (W-R5-5).

**Peak phase (Section 5.3, lines 565–616).** The LaTeX says that the stage difference is "未达统计显著", which is correct. The DOCX's "同等有效性" is not (W-R5-4). A TOST-style equivalence bound, or simply the interval for the ratio of slopes, would show how large a peak-phase reduction the data can rule out.

**Regime analysis (lines 619–628).** The confounding with season is stated, so the descriptive framing is adequate. A season-matched contrast is still the request (W6), for example October 2024 against October 2022 and October 2023 under the same coverage threshold.

**Still open from rounds 1–3:**
- the Wald test uses the null variance only;
- there is no OLS or bounded-influence fit beside FGLS;
- the renewal simulation has no stationary control (W5);
- the national comparison has no interval.

### 4.3 Reproducibility

- **Result.** The changed script reproduces exactly. The details are in Section 5.
- **Bootstrap code (lines 683–716).** The new code is correct and faster:
  - states are resampled by index, and both stages and the OLS comparator are re-estimated on each replicate;
  - the deleted `len(boot_df) < 10` guard is harmless here, because the smallest season has 273 rows across about 50 states.
- **Remaining code items:**
  - `fillna(0)` at lines 51, 53, 479 and 571 (W7);
  - `1.96 * sem` error bars at line 883, which ignore state clustering;
  - the literal 22.64 at lines 886–887 and the "~22.6 cases/week" label, instead of reading `b/a` from the fit.
- **Repository hygiene:**
  - there is still no `requirements.txt`, lockfile, `LICENSE` or test suite;
  - pinning Matplotlib 3.10.9 would make Fig. 4 regeneration byte-stable (the committed Fig. 4 uses 3.10.9, this environment 3.11.2);
  - `officecli` (README line 39) is still not a published package;
  - the README runtime is stale (W-R5-6).
- **Manuscript-to-JSON test.** The DOCX drift (W-R5-4) and the unemitted numbers (W8) have the same remedy: a short test that extracts every number from `main.tex` and the DOCX and checks it against the JSON. The check I ran for this review is about twenty lines of Python.

### 4.4 Bibliography and presentation

**Bibliography:**
- The three entries changed since round 4 now match Crossref: Bosse et al. [2] and Reich et al. [3] have title similarity 1.00 and the correct author order, and both DOIs resolve (doi.org 302).
- The dataset record [1] resolves: HTTP 200 at both the short URL and the catalogue API.
- The other 31 entries are unchanged since round 4, where all 31 DOIs resolved and the titles matched.

**Line-level comments:**
- **Lines 48–49:** broken English title (W-R5-1).
- **Lines 28 and 32:** "（匿名评审稿）" is still the author and PDF metadata. There is still no funding, conflict-of-interest or data-ethics statement. Public aggregate surveillance data need no ethics approval, but one sentence saying so is customary.
- **Line 56:** "更为关键的是"; the Althouse citation (W-R3-6).
- **Line 525:** `a` read as the infinite-scale limit (W2).
- **Line 528:**
  - "数十至百例" and "外部效度支持" (W-R5-3);
  - the attenuation sentence (W-R5-2);
  - "一侧 p" for the bootstrap proportion.
- **Line 532:** "强有力地表明", "内在的结构性特征" (W-N4).
- **Line 652:** "过半误差份额" (W-R5-5).

**Structure and figures:**
- Ten `\paragraph{...}` run-in labels remain, at lines 212, 465, 473, 480, 523, 527, 559, 562, 617 and 627. Those at 523, 527, 559 and 562 under Section 5.2 could become topic sentences or `\subsubsection`s.
- There is still no notation table, although the paper uses `m`, `m_x`, `m*`, `m*_AR`, `D_t`, `D_t^iv`, `A`, `a`, `b`, `v_R`, `v_eff`, `r`, `ρ`, `k`, `c0`, `c1` and `B`.
- All figures remain English-only in a Chinese manuscript, and this choice is not stated.

**Compiled PDF:**
- 28 pages, matching README line 20;
- no unresolved `??`;
- the last page ends with the final bibliography entry (Zhou et al., 2012), so the file is intact;
- the dataset reference is no longer badly under-full.

### 4.5 Status of round-4 items

| Round-4 item | Status at `3948f92` | Evidence | Remaining request |
|---|---|---|---|
| W-R4-1 dataset title, URL, identifier | Fixed | Bib lines 353–359; `data.cdc.gov/d/ua7e-t2fy` returns 200; data statement lines 654–659 with SHA-256 (matches); DOCX ref. [34] | None |
| W-N1 `bosse2023scoring` author order | Fixed | Bib entry at line 119; Crossref order matches (Bracher fifth) | None |
| W-N1 `reich2019accuracy` non-authors | Fixed | Bib entry at line 266; Sengupta and Holmes removed; sixteen authors match Crossref | None |
| W-R4-2 seed-fragile 2024–25 "显著为正" | Fixed | 10,000 replicates; "临界为正", CI [0.01, 3.47]; three seeds give lower bounds 0.007–0.036 | Note multiplicity; rename "一侧 p" |
| W-R4-2 pooled difference unreported | Fixed, with a new over-reading | Line 528: 1.3921, CI [0.43, 2.41]; robust across seeds | Delete "修正衰减偏倚" reading (W-R5-2) |
| W-R4-2 `n_boot_ok`, silent `except` | Fixed | JSON `n_boot_ok` = 10000 ×5; `try/except` removed | None |
| W-R4-2 same seed per subsample; fixed `r_bar_s` | Not fixed | Code line 685; `y_s` computed outside loop | Optional |
| W-R4-3 Remark 5 used `D_t` crossover | Fixed, with a new inconsistency | Line 316 uses theoretical 21–60 | Reconcile with line 528 (W-R5-3) |
| AR(1) direction of `m*` | Correct; scope fixed | Line 312: `m*_AR < m*`, fixed period length stated | None |
| "Sufficient statistic" wording (theory document) | Fixed | Theory document corollary now reads "充分降维" and matches Remark 5 | None |
| W-R4-4 title and conclusion boundary claim | Largely fixed | Title "推断收益边界"; conclusion line 652 rewritten | English title (W-R5-1) |
| W-R3-2 `c0 = 0` link, feasibility bound, per-person cost | Fixed | Lines 306–312 | Add corner solution (optional) |
| W-R4-5 DOCX withdrawn statements | Fixed; new drift | Four statements absent; new claims in `build_docx.py` lines 105, 108, 261, 281, 285, 288 | W-R5-4 |
| W-R3-4 DOCX missing theory figure | Fixed | Four drawings, four tables | None |
| W-R4-6 "193.9%" | Fixed | Lines 624, 627: 193.8 % | None |
| W-R4-6 "显著远高于", "大幅排除弱工具偏倚" | Fixed | Lines 528, 647 | None |
| W-R4-6 README runtime | Changed but inaccurate | README line 30 "约 60 s"; measured 12.9 s | Update |
| README page count | Correct | README line 20 "28 页"; `pdfinfo` 28 pages | None |
| Karlin–Rubin attribution | Not fixed | Theory document line 138 | Section 4.1 |
| W-R3-3 Section 6.1 rhetoric | Fixed | Lines 637–639 | None |
| W-R3-3 conclusion rhetoric | Fixed | Line 652 | "过半" (W-R5-5) |
| W-R3-6 Althouse citation | Not fixed | Line 56 | Under-reporting and delay sources |
| W-N3 placebo, onset control, calibration | Not fixed | Nothing added | As in W-R5-2 |
| W-N4 Table 2 | Not fixed | Lines 532–557 unchanged | Round-3 checklist |
| W-N6 reliability ratio | Partly fixed | Line 637 softened; lines 64, 70 and DOCX abstract unchanged | Drop or label as restatement |
| W2 `a` as infinite-scale limit | Not fixed | Line 525 | Align with line 646 |
| W3 specification spread | Partly fixed | Span reported; headline CI single-specification | Specification-curve interval |
| W4, W5, W6, W7 | Not fixed | Code and text unchanged | As in round 3 |
| W8 un-emitted numbers | Not fixed | Stage-interaction CI, 1.6266 not emitted | Emit; add number-tracing test |
| Hard-coded crossover, `1.96 * sem` bars | Not fixed | Code lines 883, 886–887 | Read from fit; clustered bars |
| Requirements, LICENSE, tests | Not fixed | None present | Add |
| Run-in labels, notation table, declarations, English-only figures | Not fixed | As in Section 4.4 | As in round 4 |

## 5. Verification performed

All commands were run from the reviewer workspace. Artefacts are kept under `.work/paper-review/` and are not part of this deliverable.

1. **Acquisition.**
   - Command: `git clone https://github.com/wangchi2068/case-count-inference-bottleneck` (full history).
   - `git log ddc69a54..HEAD` lists four commits. `git diff --stat ddc69a54 HEAD` gives 11 files, +374/−247.
   - I also ran word-level diffs of `main.tex` and `references.bib`, and a normalized diff of the theory document, with `\operatorname` mapped to `\mathrm`, to isolate the substantive edits of `3948f92`.
2. **Reproduction of the changed script.**
   - Setup: `git archive HEAD` into a clean directory, then `python3 simulations/run_empirical_flu_analysis.py`. NumPy 2.4.6, pandas 3.0.6, Matplotlib 3.11.2.
   - Result: rc 0 in 12.9 s.
   - **JSON against the committed file:** 2,246 keys on each side, none missing, 187 floating-point differences, maximum relative difference 1.97e-13, no categorical differences.
   - **Committed JSON at `3948f92` against `ddc69a5`:** 5 new keys (`n_boot_ok`) and 27 changed values, all in `seasonal_subsample_iv`, which is the bootstrap output. Every other key is unchanged to 1e-9 relative, so all Table 1, Table 2, rolling-origin, peak-phase, regime and national numbers carry over from the round-4 verification.
3. **Seed audit.**
   - Two further copies, changing only the seed at code line 685 to 1 and to 2, each completed 10,000 of 10,000 replicates per subsample.

   | Subsample | Seed 20260929 (committed) | Seed 1 | Seed 2 |
   |---|---|---|---|
   | 2022–23 difference CI (bootstrap proportion ≤ 0) | [−0.145, 3.894] (0.048) | [−0.152, 3.832] (0.053) | [−0.171, 3.839] (0.052) |
   | 2023–24 difference CI | [−0.552, 1.737] (0.207) | [−0.534, 1.691] (0.192) | [−0.543, 1.701] (0.200) |
   | 2024–25 difference CI | [0.007, 3.467] (0.025) | [0.036, 3.477] (0.022) | [0.013, 3.523] (0.024) |
   | Pooled, `R_bar_early` normalization | [0.297, 2.111] (0.003) | [0.281, 2.111] (0.003) | [0.283, 2.126] (0.004) |
   | Pooled, subsample-mean normalization | [0.435, 2.407] (0.001) | [0.422, 2.414] (0.001) | [0.422, 2.426] (0.002) |
   | 2024–25 `b_iv` CI | [0.727, 7.226] | [0.699, 7.239] | [0.614, 7.312] |

4. **Numbers in the text.**
   - Every IV number at line 528 equals the committed JSON after rounding: the season CIs [−0.15, 3.89], [−0.55, 1.74] and [0.01, 3.47], p = 0.025, and the pooled CI [0.43, 2.41] with p = 0.0014. The pooled difference 1.3921 is the derived quantity `b_iv − b_ols` = 1.39206.
   - A scripted search of all numbers with three or more decimals in `main.tex` (171) and in the DOCX text against the JSON gives the residue listed under W8.
5. **Fig. 4.**
   - The committed PDF differs from the round-4 file only in `CreationDate`; the `pdftotext` MD5 is identical.
   - The regenerated copy differs only through the Matplotlib version.
6. **Compiled PDF.**
   - `pdfinfo paper/main.pdf`: 28 pages, producer xdvipdfmx.
   - `pdftotext -layout`: 0 occurrences of `??`, and the text ends with the final bibliography entry.
   - English title as printed: W-R5-1.
7. **DOCX.**
   - I unzipped `main_docx.docx`, extracted the text of `word/document.xml`, counted 4 `w:drawing` elements and 4 tables, and searched for each statement listed in W-R4-5 and W-R5-4.
8. **Bibliography (free route only).**
   - The round-4 checker was restricted to the three changed entries and run against the Crossref REST API and doi.org.
   - Both DOIs return doi.org 302 and Crossref records with title similarity 1.00, and the author-order comparison passes.
   - `curl -L https://data.cdc.gov/d/ua7e-t2fy` returns 200, redirecting to the HRD catalogue page, and `https://data.cdc.gov/api/views/ua7e-t2fy.json` returns 200.
   - `sha256sum` of the shipped CSV equals the hash printed at line 657.
   - The two textbook DOIs cited below ([4], [6]) were checked the same way. No source was unreachable in this round, and no paid search was used.
9. **Theory.**
   - I re-derived Corollary 1: first- and second-order conditions, the feasibility bound, the `c0 = 0` limit and the AR(1) factor.
   - I recomputed the Remark 5 illustrations and the `m_x` range from the parameters stated at line 528.

## 6. Overall recommendation

**Recommendation: major revision, at the boundary of minor revision.**

**Score: 7 / 10, up from 6 / 10 in round 4.**

**Justification relative to round 4.** Round 4 held the score at 6 for three reasons:
- a data-provenance error;
- a conflict between the title, the conclusion and the theory document on one side and the paper's own Remark 5 on the other;
- untouched requests on the empirical core.

This revision removes the first two:
- the dataset is now cited by its correct record, with a resolving URL and a checksum that I verified;
- the theory document, Section 6.1 and the conclusion follow Remark 5, and Corollary 1 is complete and correct.

The IV inference is now stable under a change of seed and described with appropriate caution at season level, and the remaining bibliography errors are fixed. These are real improvements, and they justify a higher score. Three things keep the paper short of minor revision:
- **New over-reading.** The revision adds a sentence that reads the pooled IV–OLS gap as a correction of attenuation bias, which the paper's own identification caveats do not allow.
- **Untouched empirical core.** The analyses requested since rounds 1–3 to make the empirical section a test rather than an illustration are still missing: the IV diagnostics, the Table 2 normalization, the missing-data handling and the season-matched regime contrast.
- **Presentation regressions.** The English title is broken, two theoretical `m_x` ranges contradict each other, and the rebuilt DOCX adds a false monotonicity statement and three over-claims.

The first and third points need only edits. With the edits below and either the IV simulation calibration or the onset-control regression, I would recommend minor revision.

### Required revisions, in priority order

1. **Fix the English title** (lines 48–49). (W-R5-1)
2. **Remove the attenuation-correction reading** at line 528, or support it with the simulation calibration and the week-since-onset control. Add a multiplicity statement for the three seasons, and call the bootstrap proportion what it is. (W-R5-2, W-N3)
3. **Reconcile the theoretical `m_x` range.** State the parameters once, and replace "数十至百例" and "外部效度支持" at line 528. (W-R5-3)
4. **Generate the DOCX from the final LaTeX, or test it against the LaTeX.** Remove "严格单调下降", "同等有效性……彻底证明", "稳健修正了……衰减偏倚", "证实漏报抽稀……" and the reliability-ratio and "大数据" wording. (W-R5-4, W-N6)
5. **Correct "过半误差份额"** in the conclusion. (W-R5-5)
6. **Align line 525 with limitation (2)** on the meaning of `a`. Fix the Karlin–Rubin attribution and the strict/non-strict monotonicity wording. Replace or supplement the Althouse citation. (W2, Section 4.1, W-R3-6)
7. **Emit the stage-interaction CI and the subsample mean,** and add a test that every manuscript number appears in the JSON. Update the README runtime. (W8, W-R5-6)
8. **Finish Table 2** using the round-3 checklist, **replace `fillna(0)`**, and **add a season-matched regime contrast.** (W-N4, W7, W6)
9. **Minor fixes:**
   - a specification-curve interval as the headline;
   - the hard-coded crossover and clustered error bars;
   - requirements, LICENSE and tests;
   - a notation table, declarations and a statement on English-only figures.

Items 1–7 need no new data and little new code. Item 2 is the only one that may need a new analysis, and the simulation scripts already contain most of what a calibration would require.

## References cited in this review

[1] Centers for Disease Control and Prevention, National Healthcare Safety Network. Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN). CDC open-data catalogue record ua7e-t2fy; resolved 2026-10-08. https://data.cdc.gov/d/ua7e-t2fy

[2] Bosse NI, Abbott S, Cori A, van Leeuwen E, Bracher J, Funk S. Scoring epidemiological forecasts on transformed scales. PLOS Computational Biology. 2023;19(8):e1011393. https://doi.org/10.1371/journal.pcbi.1011393

[3] Reich NG, McGowan CJ, Yamana TK, Tushar A, Ray EL, Osthus D, Kandula S, Brooks LC, Crawford-Crudell W, Gibson GC, Moore E, Silva R, Biggerstaff M, Johansson MA, Rosenfeld R, Shaman J. Accuracy of real-time multi-model ensemble forecasts for seasonal influenza in the U.S. PLOS Computational Biology. 2019;15(11):e1007486. https://doi.org/10.1371/journal.pcbi.1007486

[4] Davison AC, Hinkley DV. Bootstrap Methods and their Application. Cambridge: Cambridge University Press; 1997. https://doi.org/10.1017/CBO9780511802843

[5] Carroll RJ, Ruppert D, Stefanski LA, Crainiceanu CM. Measurement Error in Nonlinear Models: A Modern Perspective. 2nd ed. Boca Raton: Chapman and Hall/CRC; 2006. https://doi.org/10.1201/9781420010138

[6] Lehmann EL, Romano JP. Testing Statistical Hypotheses. 3rd ed. New York: Springer; 2005. https://doi.org/10.1007/0-387-27605-X

[7] Althouse BM, Scarpino SV, Meyers LA, Ayers JW, Bargsten M, Baumbach J, et al. Enhancing disease surveillance with novel data streams: challenges and opportunities. EPJ Data Science. 2015;4:17. https://doi.org/10.1140/epjds/s13688-015-0054-0

[8] Cori A, Ferguson NM, Fraser C, Cauchemez S. A new framework and software to estimate time-varying reproduction numbers during epidemics. American Journal of Epidemiology. 2013;178(9):1505–1512. https://doi.org/10.1093/aje/kwt133
