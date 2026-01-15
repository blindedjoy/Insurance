# Insurance Plan Analysis Autopilot

> **Goal**: Compare Covered California health insurance plans (Gold vs Platinum + dental/vision) using Spitznagel's geometric mean framework.
> **Constraint**: TDD for all implementations. Tests first, then code.
> **Style**: Uncle Bob — max 3 function arguments, use config objects.

---

## 📋 Entropy Backlog (ROI-ordered)

ROI = Entropy × Ease. Higher ROI = do first.

### ✅ P1: Core Plan Analysis Engine — COMPLETE

| Task | Description | Status | Tests |
|------|-------------|--------|-------|
| P1a | Plan data models | ✅ | `test_plans.py` (18) |
| P1b | Scenario definitions | ✅ | `test_scenarios.py` (16) |
| P1c | Geometric mean / log-wealth | ✅ | `test_geometric_mean.py` (15) |
| P1d | Plan comparison | ✅ | `test_compare.py` (12) |
| P1.1 | Wealth ratio refactor | ✅ | `test_wealth_ratio.py` (21) |
| **Total** | **82 tests passing** | ✅ | — |

---

### ✅ Research Phase — PROMPT A COMPLETE

| Task | Topic | Status | Findings |
|------|-------|--------|----------|
| **R1** | Network type coverage rules | ✅ | All plans equal for emergency |
| **R2** | Kaiser travel risk | ⏳ Prompt B | — |
| **R3** | Gold vs Platinum comparison | ⏳ Prompt B | — |
| **R4** | Post-stabilization costs | ✅ | Tiered model validated |

**Key Research Findings** (from ChatGPT 5.2 + Opus):

1. **Emergency OON**: Protected equally across all plan types (No Surprises Act)
2. **Air ambulance**: Protected by federal law
3. **Ground ambulance**: **NOT protected** — budget $500-$2,000
4. **Consent waiver**: 50% of patients sign, exposing to full OON charges
5. **PPO advantage**: $25k OON OOP max caps tail risk for waiver-signers
6. **$30k assumption**: Reasonable for expected case, but use tiered model

---

## 🔬 Validated Model Parameters (from Research)

### Tiered Post-Stabilization Exposure (Colorado Ski Scenario)

**Old model**: Fixed $30,000 exposure

**New model** (Opus recommendation):

```python
# Tiered OON exposure for geometric mean analysis
OON_SCENARIOS = {
    "best_case": {
        "exposure": 3_000,      # Simple fracture, quick discharge
        "probability": 0.30,
    },
    "expected_case": {
        "exposure": 15_000,     # Surgery, transfer arranged
        "probability": 0.50,
    },
    "moderate_worst": {
        "exposure": 35_000,     # Surgery, stays at OON hospital
        "probability": 0.18,
    },
    "catastrophic": {
        "exposure": 75_000,     # Complications, extended stay
        "probability": 0.02,
    },
}

# Additional fixed costs
GROUND_AMBULANCE_EXPOSURE = 1_500  # $500-$2,000 range, use midpoint
```

### Coverage Rules by Plan Type

```python
from enum import Enum

class NetworkType(Enum):
    HMO = "hmo"
    PPO = "ppo"
    EPO = "epo"

# Validated coverage rules (from research)
COVERAGE_RULES = {
    NetworkType.HMO: {
        "emergency_oon": "in_network_rates",      # No Surprises Act
        "post_stab_no_waiver": "covered",         # Until safe to transfer
        "post_stab_with_waiver": "not_covered",   # You pay 100%
        "oon_oop_max": None,                      # No cap
    },
    NetworkType.PPO: {
        "emergency_oon": "in_network_rates",
        "post_stab_no_waiver": "covered",
        "post_stab_with_waiver": "50%_after_5.5k_ded",  # Blue Shield PPO
        "oon_oop_max": 25_000,                    # Individual cap
    },
    NetworkType.EPO: {
        "emergency_oon": "in_network_rates",
        "post_stab_no_waiver": "covered",
        "post_stab_with_waiver": "not_covered",
        "oon_oop_max": None,
    },
}
```

---

### 🔄 P2: Network Modeling — NOW UNBLOCKED

#### P2b: Network Type + Tiered OON Model

**Status**: Research complete, ready to implement!

```python
# src/insurance/plans.py additions

class NetworkType(Enum):
    """Health plan network type."""
    HMO = "hmo"
    PPO = "ppo"  
    EPO = "epo"


@dataclass
class PostStabilizationConfig:
    """Tiered post-stabilization exposure (from research)."""
    # Probability of signing consent waiver (CMS: ~50%)
    p_waiver_signed: float = 0.50
    
    # Tiered exposure if waiver signed (HMO/EPO)
    best_case: float = 3_000
    best_case_p: float = 0.30
    expected_case: float = 15_000
    expected_case_p: float = 0.50
    moderate_worst: float = 35_000
    moderate_worst_p: float = 0.18
    catastrophic: float = 75_000
    catastrophic_p: float = 0.02
    
    # Ground ambulance (not protected by federal law)
    ground_ambulance: float = 1_500


@dataclass
class MedicalPlan:
    """Updated with network type."""
    name: str
    annual_premium: float
    in_network_oop_max: float
    network_type: NetworkType  # NEW
    deductible: float = 0.0
    expected_minor_oop: float = 400.0
    
    # OON fields (PPO only)
    oon_deductible: float = 5_500  # PPO OON deductible
    oon_oop_max: float = 25_000    # PPO OON cap
    oon_coinsurance: float = 0.50  # You pay 50% after deductible
```

| Sub-task | Description | Tests |
|----------|-------------|-------|
| P2b.1 | Add `NetworkType` enum | `test_plans.py` |
| P2b.2 | Add `PostStabilizationConfig` | `test_plans.py` |
| P2b.3 | Update `MedicalPlan` with network_type | `test_plans.py` |
| P2b.4 | Update scenario builder for tiered OON | `test_scenarios.py` |

---

## 📁 Module Map

| Module | Purpose | Status |
|--------|---------|--------|
| `src/insurance/plans.py` | Plan data models | 🔄 Updating |
| `src/insurance/scenarios.py` | Scenario definitions | 🔄 Updating |
| `src/insurance/geometric_mean.py` | GM calculation | ✅ Good |
| `src/insurance/compare.py` | Plan comparison | ✅ Good |

---

## 📐 Mathematical Framework

### Wealth Ratio (Spitznagel)

```
ratio = (disposable - premium - oop) / disposable

Where:
  disposable = after_tax_income - baseline_spend
  premium = medical + dental + vision
  oop = scenario-specific out-of-pocket
```

### Geometric Mean

```
GM = (r₁ × r₂ × ... × rₙ)^(1/n)

Key property: ANY rᵢ → 0 makes GM → 0
This is why tail risk dominates.
```

### Tiered OON Model (NEW)

For HMO/EPO (no waiver):
```
oon_oop = in_network_oop_max + ground_ambulance
```

For HMO/EPO (waiver signed, weighted by tier probability):
```
oon_oop = in_network_oop_max 
        + ground_ambulance
        + weighted_post_stab_exposure

weighted_post_stab_exposure = 
    0.30 × $3,000 
  + 0.50 × $15,000 
  + 0.18 × $35,000 
  + 0.02 × $75,000
  = $15,600 (expected)
  
But for GM analysis, model each tier separately!
```

For PPO (waiver signed):
```
oon_oop = min(oon_oop_max, 
              oon_deductible + post_stab_cost × oon_coinsurance)
        + ground_ambulance
```

---

## ✅ Execution Checklist

Before implementing any feature:

1. [ ] Write failing test first (TDD)
2. [ ] Keep functions ≤3 arguments (use config objects)
3. [ ] Keep functions <50 lines
4. [ ] Use dataclasses for structured data
5. [ ] Docstrings with Args/Returns
6. [ ] Run `pytest -v` after each change

---

## 🚀 Priority Order (Updated)

| Priority | Task | Status |
|----------|------|--------|
| 1 | ~~Research Prompt A~~ | ✅ Complete |
| 2 | **P2b**: Network type + tiered OON | 🔄 Ready to implement |
| 3 | **Prompt B**: Kaiser travel + Gold vs Platinum | ⏳ In progress |
| 4 | **P3**: Real plan data | After P2b |
| 5 | **P4**: Visualization | After P3 |
