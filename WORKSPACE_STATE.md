# 🏥 Insurance Analysis Workspace State

> **Last Updated**: 2026-01-15
> **Current Branch**: `integrate-research-findings`
> **Status**: ✅ **ANALYSIS COMPLETE** - Kaiser Platinum HMO wins!

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

## 📊 GEOMETRIC MEAN RESULTS (Real 2026 Data)

**Winner: Kaiser Platinum HMO** 🏆

| Rank | Plan | Premium | OOP Max | GM Wealth | GM Ratio |
|------|------|---------|---------|-----------|----------|
| 🥇 1 | **Kaiser Platinum HMO** | $20,924 | $10,000 | **$51,041** | 64.3% |
| 🥈 2 | Blue Shield Trio Platinum HMO | $22,772 | $10,000 | $49,033 | 58.5% |
| 🥉 3 | Kaiser Gold HMO | $19,556 | $18,400 | $46,202 | 59.9% |
| 4 | Blue Shield Trio Gold HMO | $19,700 | $18,400 | $46,036 | 59.6% |
| 5 | Blue Shield Gold 80 PPO | $28,268 | $18,400 | $35,565 | 52.3% |
| 6 | Blue Shield Platinum 90 PPO | $38,036 | $10,000 | $31,217 | 46.8% |

### Gold vs Platinum Analysis

| Metric | Kaiser Gold | Kaiser Platinum | Delta |
|--------|-------------|-----------------|-------|
| Premium (w/ dental+vision) | $19,556 | $20,924 | +$1,368 |
| OOP Max | $18,400 | $10,000 | **-$8,400** |
| GM Ratio | 59.85% | 64.28% | **+4.44pp** |
| GM Wealth | $52,664 | $56,570 | **+$3,906** |

**Key Insight**: Platinum wins by +4.44 percentage points on GM ratio.

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
| **P5** | Add supplemental travel insurance to model? | Medium |
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

## ⚠️ Technical Debt (Reduced)

| Issue | Location | Priority | Status |
|-------|----------|----------|--------|
| ~~No network type field~~ | `plans.py` | ~~High~~ | ✅ Done |
| Hardcoded test fixtures | `conftest.py` | **High** | 🔄 Updating |
| Functions with >3 args | `geometric_mean.py` | Medium | Later |
