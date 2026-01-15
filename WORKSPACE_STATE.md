# 🏥 Insurance Analysis Workspace State

> **Last Updated**: 2026-01-15
> **Current Branch**: `planning`
> **Next Task**: P2 — Config refactor + Network type modeling

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
| **Config refactor (Uncle Bob)** | ⏳ P2a | — |
| **Network type modeling (HMO/PPO/EPO)** | ⏳ P2b | — |
| **Tests** | ✅ **82 passing** | `tests/` |

---

## 🔴 Open Questions (Need Research)

### Q1: How to model OON risk by network type?

| Plan Type | Emergency OON | Post-Stabilization | Non-Emergency OON |
|-----------|---------------|-------------------|-------------------|
| **HMO** | ✅ Covered (No Surprises Act) | ❌ Rarely covered | ❌ Never covered |
| **PPO** | ✅ Covered | ⚠️ Partial/varies | ⚠️ Limited on exchange |
| **EPO** | ✅ Covered | ❌ Not covered | ❌ Never covered |

**Research needed**: What's the actual probability of needing OON care, and what's the expected cost exposure for each plan type?

### Q2: Network adequacy for SF plans

| Plan | Network | Key Hospitals | Risk if traveling? |
|------|---------|---------------|-------------------|
| Kaiser Gold HMO | Kaiser only | Kaiser SF | High (Kaiser only nationwide) |
| Blue Shield Trio HMO | UCSF + Dignity | UCSF, St. Mary's | Medium |
| Blue Shield PPO | Broad | Most SF hospitals | Lower |
| Anthem EPO | Broad (no UCSF?) | ? | Medium |

**Research needed**: Which hospitals/providers are in each network? What happens with Kaiser if injured in Colorado?

### Q3: Post-stabilization exposure

Current model assumes $30k exposure. Is this realistic?
- What does "post-stabilization" actually mean legally?
- When does emergency coverage end?
- What's typical for extended OON care (rehab, follow-up surgery)?

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

### 🔄 In Progress / Next

| Task | Description | Depends On |
|------|-------------|------------|
| **P2a** | Config refactor (Uncle Bob ≤3 args) | — |
| **P2b** | Network type modeling (HMO/PPO/EPO) | Research |
| **P2c** | OON probability model | Research |
| **P3** | Load real Covered California plan data | P2a |
| **P4** | Visualization (scenario waterfall) | P3 |

### 📚 Research Tasks (for ChatGPT 5.2)

| Task | Question |
|------|----------|
| R1 | What are the actual OON coverage rules for each Covered California plan type (HMO/PPO/EPO)? |
| R2 | What's the network for Kaiser Gold HMO outside California? |
| R3 | What does "post-stabilization" mean under the No Surprises Act? |
| R4 | What's typical cost for extended OON care (PT, rehab, follow-up surgery)? |

---

## 📍 Navigation

| Resource | Path |
|----------|------|
| **This file** | `WORKSPACE_STATE.md` |
| Autopilot | `docs/AI_AUTOPILOT.md` |
| ChatGPT research | `docs/research/chatgpt_ca_2026_research.md` |

---

## ⚠️ Technical Debt

| Issue | Location | Priority |
|-------|----------|----------|
| Functions with >3 args | `geometric_mean.py`, `compare.py` | **High** (P2a) |
| Binary OON model (too simplistic) | `plans.py`, `scenarios.py` | **High** (P2b) |
| Hardcoded $30k post-stabilization | `plans.py` | Medium |
| No network type field | `MedicalPlan` | **High** (P2b) |
