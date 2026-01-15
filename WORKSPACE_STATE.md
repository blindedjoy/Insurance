# 🏥 Insurance Analysis Workspace State

> **Last Updated**: 2026-01-15
> **Current Branch**: `main`
> **Next Task**: P1 — Plan data models + geometric mean calculation

---

## 🎯 Current Goal: Health Insurance Plan Comparison

Analyze Covered California Gold vs Platinum plans using Spitznagel's geometric mean framework from "The Tao of Capital". The key insight: **geometric mean is dominated by the minimum outcome**, so downside protection matters more than expected value.

| Component | Status | Location |
|-----------|--------|----------|
| Plan data models | ✅ Complete | `src/insurance/plans.py` |
| Geometric mean calc | ✅ Complete | `src/insurance/geometric_mean.py` |
| Scenario engine | ✅ Complete | `src/insurance/scenarios.py` |
| Gold vs Platinum comparison | ✅ Complete | `src/insurance/compare.py` |
| Dental/Vision add-ons | ✅ Included | `src/insurance/plans.py` |
| **Tests** | ✅ **61 passing** | `tests/` |

---

## 📊 Key Concepts (from Spitznagel)

### Geometric Mean Dominance

The geometric mean of wealth outcomes is:
- **GM = (W₁ × W₂ × ... × Wₙ)^(1/n)**
- Equivalently: **log(GM) = (1/n) × Σ log(Wᵢ)**

**Critical insight**: A single catastrophic outcome (Wᵢ → 0) drives GM → 0.
This is why **tail risk protection** matters more than premium optimization.

### Health Insurance Application

| Scenario | Probability | Financial Impact |
|----------|-------------|------------------|
| No use | ~70% | -Premium only |
| Minor use | ~25% | -Premium - Copays/Deductible |
| Catastrophic in-network | ~3% | -Premium - OOP Max |
| Catastrophic out-of-network | ~2% | -Premium - OOP Max - Post-stabilization |

**Gold vs Platinum trade-off**:
- Platinum: Higher premium, lower OOP max → better catastrophe protection
- Gold: Lower premium, higher OOP max → better "no use" scenario

---

## 🔑 Key Findings (to be computed)

| Protection Level | Winner | Why |
|------------------|--------|-----|
| TBD | TBD | Geometric mean calculation pending |

---

## 📋 Task Backlog

| Task | Description | Status |
|------|-------------|--------|
| P1a | Plan data models (MedicalPlan, DentalPlan, VisionPlan) | ✅ |
| P1b | Scenario definitions | ✅ |
| P1c | Geometric mean calculation | ✅ |
| P1d | Plan comparison function | ✅ |
| P2 | Load real Covered California plan data | ⏳ |
| P3 | Visualization (scenario outcomes) | ⏳ |

---

## 📍 Navigation

| Resource | Path |
|----------|------|
| **This file** | `WORKSPACE_STATE.md` |
| Autopilot | `docs/AI_AUTOPILOT.md` |
| ChatGPT research | `docs/research/chatgpt_ca_2026_research.md` |

---

## ⚠️ Technical Notes

### Out-of-Network Coverage (Covered California)

From research, even PPO plans on Covered California have limited OON coverage:
- **Emergency services**: Protected by No Surprises Act (in-network-like cost-sharing)
- **Post-stabilization**: Often NOT covered or punitive — model as high tail risk
- **Non-emergency OON**: Effectively not covered on exchange plans

### Modeling Assumptions

1. Emergency OON treated as in-network (per federal law)
2. Post-stabilization OON modeled as additional exposure (configurable)
3. Equal scenario weighting (not probability-weighted) for robustness
