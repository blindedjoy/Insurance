# 🏥 Insurance Analysis Workspace State

> **Last Updated**: 2026-01-15
> **Current Branch**: `integrate-research-findings` (ready to merge)
> **Status**: ✅ **ANALYSIS COMPLETE** - Kaiser Platinum HMO wins!
> **Test Coverage**: 91% (94 tests passing)

---

## 🎯 Current Goal: Health Insurance Plan Comparison

Analyze Covered California Gold vs Platinum plans using Spitznagel's geometric mean framework from "The Tao of Capital". The key insight: **geometric mean is dominated by the minimum outcome**, so downside protection matters more than expected value.

| Component | Status | Location |
|-----------|--------|----------|
| Plan data models | ✅ Complete | `src/insurance/plans.py` |
| Geometric mean calc | ✅ Complete | `src/insurance/geometric_mean.py` |
| Scenario engine | ✅ Complete | `src/insurance/scenarios.py` |
| NetworkType enum | ✅ Complete | `src/insurance/plans.py` |
| **Research: Prompt A** | ✅ Complete | `docs/research/prompt a responses/` |
| **Research: Prompt B** | ✅ Complete | `docs/research/prompt b responses/` |
| **Demo (real data)** | ✅ **Complete** | `demo.py` |
| **Tests** | ✅ **94 passing** | `tests/` |

---

## ✅ Research Complete: Final Model Parameters

### 2026 Premium Numbers (SF couple, age 35, no subsidies)

| Plan | Annual Premium | Monthly |
|------|----------------|---------|
| **Kaiser Gold HMO** | **$18,456** | $1,538 |
| Kaiser Platinum HMO | $19,824 | $1,652 |
| Blue Shield Trio Gold | $18,600 | $1,550 |
| Blue Shield Trio Platinum | $21,672 | $1,806 |
| Blue Shield Gold PPO | $27,168 | $2,264 |
| Blue Shield Platinum PPO | $36,936 | $3,078 |

### Standardized Cost-Sharing (ALL carriers identical per CA law)

| Metric | Gold | Platinum | Delta |
|--------|------|----------|-------|
| **Individual OOP max** | $9,200 | $5,000 | $4,200 |
| **Couple OOP max** | $18,400 | $10,000 | **$8,400** |
| Medical deductible | $0 | $0 | — |
| Primary care copay | $40 | $15 | $25 |
| Specialist copay | $70 | $30 | $40 |
| ER facility fee | $350 | $175 | $175 |
| Hospital admission | $375/day × 5 | $225/day × 5 | $750 max |

### OON Coverage (PPO only)

| Metric | Value |
|--------|-------|
| OON Deductible | $5,500 individual |
| OON Coinsurance | 50% after deductible |
| OON OOP Max | $25,000 individual / $50,000 couple |

---

## 🔬 Key Research Findings

### Kaiser Travel Risk: MIXED CONCLUSIONS

| Source | Finding |
|--------|---------|
| **Opus** | Kaiser has **1,100+ physicians in Colorado** + Visiting Member Program. Kaiser is **BETTER** than Blue Shield HMOs for ski travel risk. |
| **ChatGPT** | Kaiser has authorization hassles, documented lawsuits (Providence, MemorialCare), horror stories. Blue Shield Trio has **BlueCard** national network advantage. |

**Consensus**: All HMOs equal for emergency (No Surprises Act). Difference is post-stabilization.

### Post-Stabilization Exposure (Colorado Ski Scenario)

| Scenario | Probability | Exposure |
|----------|-------------|----------|
| Best case (simple fracture) | 30% | **$3,000** |
| Expected case (surgery, transfer) | 50% | **$15,000** |
| Moderate worst (stays at OON) | 18% | **$35,000** |
| Catastrophic (complications) | 2% | **$75,000** |

**Additional**: Ground ambulance $500-$2,000 (not protected by federal law)

### Break-Even Analysis

| Scenario | Gold Total | Platinum Total | Winner |
|----------|------------|----------------|--------|
| Healthy year (~$400 spend) | $18,856 | $20,024 | **Gold (+$1,168)** |
| Moderate year (~$5k spend) | $22,000 | $22,500 | **Gold** |
| Catastrophic (both hit OOP) | $36,856 | $29,824 | **Platinum (+$7,032)** |

**Break-even point**: ~$3,400-$4,000 in healthcare spending

### Final Recommendations

| Source | Recommendation | Rationale |
|--------|----------------|-----------|
| **Opus** | **Kaiser Gold + travel insurance** | Best geometric mean. Premium savings fund 3-4 years of travel insurance. |
| **ChatGPT** | **Blue Shield Trio Platinum** | Best tail-risk protection. BlueCard network + low OOP max. |
| **Both** | **Avoid PPO** | $8,712/year premium penalty hard to justify. OON coverage has gaps. |

---

## 📊 Key Concepts (from Spitznagel)

### Geometric Mean Dominance

```
GM = (W₁ × W₂ × ... × Wₙ)^(1/n)

Key property: ANY Wᵢ → 0 makes GM → 0
This is why tail risk protection matters more than expected value.
```

### Our Implementation: Equal Weighting (Conservative)

| Approach | Formula | 2% Event Weight |
|----------|---------|-----------------|
| Probability-weighted | E[log(W)] = Σ pᵢ log(Wᵢ) | 2% |
| **Our approach (equal)** | E[log(W)] = (1/n) Σ log(Wᵢ) | **25%** |

**Why equal weighting?** Spitznagel argues we systematically underestimate tail risks.
Equal weighting is MORE conservative - treats catastrophe as more likely than data suggests.

### Math Verification

```python
# Wealth ratio formula
ratio = (disposable - premium - oop) / disposable

# Example: $117,350 disposable, $20,924 premium, $10,000 OOP
ratio = (117350 - 20924 - 10000) / 117350 = 0.7364 (73.64%)

# Geometric mean (equal weighting)
GM([r1, r2, r3, r4]) = (r1 × r2 × r3 × r4)^(1/4)

# Example: [0.82, 0.82, 0.73, 0.59]
GM = (0.82 × 0.82 × 0.73 × 0.59)^0.25 = 0.7353 (73.53%)
```

### Wealth Ratio Scale

```
1.0 = 100% = kept all disposable income
0.9 =  90% = spent 10% on health
0.0 =   0% = total loss (catastrophe)
```

### Health Insurance as a "Put Option"

- **Lower OOP max** = better downside protection = higher "put value"
- **Platinum vs Gold**: $8,400 lower OOP max for $1,368 premium (Kaiser)
- **Put cost-effectiveness**: $1,368 / $8,400 = 16.3% "premium" for tail protection

---

## 📊 GEOMETRIC MEAN RESULTS (Your Real Numbers)

**Your Financial Situation**:
- Gross Income: $275,000 (wife $130k + your $145k)
- Tax Rate: 32.6%
- Baseline Spend: $68,000 (child support $24k + other - NO RENT)
- **Disposable: $117,350**

**Winner: Kaiser Platinum HMO** 🏆

| Rank | Plan | Premium | OOP Max | GM Wealth | GM Ratio |
|------|------|---------|---------|-----------|----------|
| 🥇 1 | **Kaiser Platinum HMO** | $20,924 | $10,000 | **$86,283** | **73.53%** |
| 🥈 2 | Blue Shield Trio Platinum HMO | $22,772 | $10,000 | $84,418 | 71.94% |
| 🥉 3 | Kaiser Gold HMO | $19,556 | $18,400 | $82,790 | 70.55% |
| 4 | Blue Shield Trio Gold HMO | $19,700 | $18,400 | $82,644 | 70.42% |
| 5 | Blue Shield Gold 80 PPO | $28,268 | $18,400 | $78,586 | 66.97% |
| 6 | Blue Shield Platinum 90 PPO | $38,036 | $10,000 | $73,444 | 62.59% |

### Gold vs Platinum Analysis (Kaiser)

| Metric | Kaiser Gold | Kaiser Platinum | Delta |
|--------|-------------|-----------------|-------|
| Premium (w/ dental+vision) | $19,556 | $20,924 | +$1,368 |
| OOP Max | $18,400 | $10,000 | **-$8,400** |
| GM Ratio | 70.55% | 73.53% | **+2.98pp** |
| GM Wealth | $82,790 | $86,283 | **+$3,493** |
| Worst case (OON Colorado) | $62,644 left | **$69,676 left** | +$7,032 |

**Key Insight**: Platinum wins. Even in worst case (OON ski accident), you keep **$69,676** (59% of disposable).

---

## 📋 Task Backlog

### ✅ Complete

| Task | Description |
|------|-------------|
| P1a-d | Core plan analysis engine (plans, scenarios, geometric mean, compare) |
| P1.1 | Wealth ratio refactor (Spitznagel 0-1 scale) |
| P2b | NetworkType enum (HMO/PPO/EPO) + OON fields |
| **R1-R4** | Research Prompt A (OON rules, costs) |
| **R5-R8** | Research Prompt B (Kaiser travel, Gold vs Platinum) |
| **P3** | ✅ Update demo with real 2026 numbers |
| **P4** | ✅ Run comparison with real data |

### 🔄 Next Steps

| Task | Description | Priority |
|------|-------------|----------|
| **T1** | Test refactor: Math verification tests (hand-calculated golden values) | **High** |
| **T2** | Test refactor: Increase coverage to 95%+ | **High** |
| **T3** | Test refactor: Clean up fixtures with pytest patterns | Medium |
| **T4** | Test refactor: Add edge case tests (ruin scenario, etc.) | Medium |
| **P5** | Add supplemental travel insurance to model? | Low |
| **P6** | Visualization (scenario waterfall) | Low |
| **P7** | Sensitivity analysis (vary probabilities) | Low |

---

## 📍 Navigation

| Resource | Path |
|----------|------|
| **This file** | `WORKSPACE_STATE.md` |
| Autopilot | `docs/AI_AUTOPILOT.md` |
| Research Prompt A | `docs/research/prompt a responses/` |
| Research Prompt B | `docs/research/prompt b responses/` |

---

## ⚠️ Technical Debt

| Issue | Location | Priority | Status |
|-------|----------|----------|--------|
| ~~No network type field~~ | `plans.py` | ~~High~~ | ✅ Done |
| ~~Hardcoded test fixtures~~ | `conftest.py` | ~~High~~ | ✅ Done (uses data.py) |
| ~~DRY violations~~ | Multiple | ~~High~~ | ✅ Done (centralized in data.py) |
| Test coverage 91% | `tests/` | Medium | 🔄 Target 95% |
| Functions with >3 args | `geometric_mean.py` | Low | Later |
| No math verification tests | `tests/` | **High** | 🔄 Next branch |

## 📋 Test Refactor Plan (Next Branch)

After merge, create `test-refactor` branch:

1. **Math Verification Tests** (hand-calculated golden values)
   ```python
   def test_gm_math_by_hand():
       # GM([0.9, 0.8, 0.5]) = (0.9 × 0.8 × 0.5)^(1/3) = 0.7208...
       assert abs(compute_geometric_mean_ratio([0.9, 0.8, 0.5]) - 0.7208) < 0.001
   ```

2. **Increase Coverage** (85% → 95%)
   - Cover `format_scenario_breakdown()` in compare.py
   - Cover edge cases in geometric_mean.py
   - Cover `oon_emergency_treated_as_in_network=False` branch

3. **Edge Case Tests**
   - Disposable = 0 (what happens?)
   - OOP > disposable (ruin scenario)
   - All scenarios identical (GM = AM)

4. **Optional: Property-Based Tests** (with hypothesis)
   - GM ≤ AM (always)
   - 0 ≤ ratio ≤ 1 (always)
   - Higher premium → lower ratio (monotonicity)
