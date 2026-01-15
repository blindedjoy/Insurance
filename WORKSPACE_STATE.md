# 🏥 Insurance Analysis Workspace State

> **Last Updated**: 2026-01-15
> **Current Branch**: `research-prompts`
> **Next Task**: P2b — Network type modeling (research complete!)

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
| **Research: OON rules + costs** | ✅ **COMPLETE** | `docs/research/prompt a responses/` |
| **Network type modeling** | ⏳ P2b | — |
| **Tests** | ✅ **82 passing** | `tests/` |

---

## ✅ Research Findings (Prompt A Complete)

### Q1: OON Coverage Rules by Plan Type — ANSWERED

| Situation | HMO | PPO | EPO | Source |
|-----------|-----|-----|-----|--------|
| **Emergency OON** | ✅ In-network rates | ✅ In-network rates | ✅ In-network rates | No Surprises Act |
| **Air ambulance** | ✅ Protected ($250 copay) | ✅ Protected | ✅ Protected | No Surprises Act |
| **Ground ambulance** | ⚠️ **NOT protected** | ⚠️ **NOT protected** | ⚠️ **NOT protected** | Federal gap |
| **Post-stabilization (no waiver)** | ✅ Covered | ✅ Covered | ✅ Covered | Until safe to transfer |
| **Post-stabilization (waiver signed)** | ❌ $0 coverage | ⚠️ 50% after $5.5k ded | ❌ $0 coverage | Patient choice |
| **Elective OON** | ❌ Never | ⚠️ Limited | ❌ Never | Plan rules |
| **OON OOP max** | N/A | **$25k ind / $50k couple** | N/A | PPO only |

**Key insight**: The **consent waiver** is the critical decision point. CMS estimates **50% of patients sign waivers**, exposing themselves to full OON charges.

### Q2: Network Adequacy — PARTIALLY ANSWERED

| Plan | Network | Key Hospitals | Travel Risk |
|------|---------|---------------|-------------|
| Kaiser Gold HMO | Kaiser only | Kaiser SF | **High** (Kaiser-only nationwide) |
| Blue Shield Trio HMO | UCSF + Dignity | UCSF, St. Mary's | Medium |
| Blue Shield PPO | Broad | Most SF hospitals | Lower (OON coverage exists) |
| Anthem EPO | Broad | TBD | Medium |

**Prompt B** will provide more detail on Kaiser travel risk.

### Q3: Post-Stabilization Exposure — ANSWERED

**$30k assumption is reasonable but should be tiered for geometric mean analysis.**

| Scenario | Probability | Exposure | Model Parameter |
|----------|-------------|----------|-----------------|
| Best case (simple fracture, quick discharge) | 30% | $1k-$5k | **$3,000** |
| Expected case (surgery, transfer arranged) | 50% | $8k-$20k | **$15,000** |
| Moderate worst (surgery, stays at OON hospital) | 18% | $25k-$50k | **$35,000** |
| Catastrophic (complications, extended stay) | 2% | $50k-$150k | **$75,000** |

**Additional exposure**: Ground ambulance ($500-$2,000) — not protected by federal law.

---

## 📊 Key Concepts (from Spitznagel)

### Geometric Mean Dominance

The geometric mean of wealth outcomes is:
- **GM = (W₁ × W₂ × ... × Wₙ)^(1/n)**
- Equivalently: **log(GM) = (1/n) × Σ log(Wᵢ)**

**Critical insight**: A single catastrophic outcome (Wᵢ → 0) drives GM → 0.
This is why **tail risk protection** matters more than premium optimization.

### Wealth Ratio Scale (P1.1)

```
1.0 = 100% = kept all disposable income
0.9 =  90% = spent 10% on health
0.0 =   0% = total loss (catastrophe)
```

### Health Insurance as a "Put Option"

The OOP maximum acts like a put option strike price:
- **Lower OOP max** = better downside protection = higher "put value"
- **Network type** affects the "conditions" under which the put pays off
- **PPO OON OOP max ($25k)** = partial protection for waiver-signers

---

## 📋 Task Backlog

### ✅ Complete

| Task | Description |
|------|-------------|
| P1a | Plan data models (MedicalPlan, DentalPlan, VisionPlan) |
| P1b | Scenario definitions |
| P1c | Geometric mean calculation |
| P1d | Plan comparison function |
| P1.1 | Wealth ratio refactor (Spitznagel 0-1 scale) |
| **R1-R4** | **Research complete** (Prompt A via ChatGPT + Opus) |

### 🔄 In Progress / Next

| Task | Description | Depends On |
|------|-------------|------------|
| **P2b** | Network type modeling (HMO/PPO/EPO) | ✅ Research done |
| **P2c** | Tiered OON scenario model | ✅ Research done |
| **Prompt B** | Kaiser travel + Gold vs Platinum research | In progress |
| **P3** | Load real Covered California plan data | P2b |
| **P4** | Visualization (scenario waterfall) | P3 |

---

## 📍 Navigation

| Resource | Path |
|----------|------|
| **This file** | `WORKSPACE_STATE.md` |
| Autopilot | `docs/AI_AUTOPILOT.md` |
| Research prompts | `docs/research/prompts/` |
| **Research findings** | `docs/research/prompt a responses/` |

---

## ⚠️ Technical Debt

| Issue | Location | Priority | Status |
|-------|----------|----------|--------|
| Binary OON model (too simplistic) | `scenarios.py` | **High** | 🔄 Fixing now |
| Hardcoded $30k post-stabilization | `plans.py` | **High** | 🔄 Fixing now |
| No network type field | `MedicalPlan` | **High** | 🔄 Fixing now |
| No ground ambulance exposure | `plans.py` | Medium | 🔄 Adding |
| Functions with >3 args | `geometric_mean.py` | Medium | Later |
