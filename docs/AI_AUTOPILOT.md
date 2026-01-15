# Insurance Plan Analysis Autopilot

> **Goal**: Compare Covered California health insurance plans (Gold vs Platinum + dental/vision) using Spitznagel's geometric mean framework.
> **Constraint**: TDD for all implementations. Tests first, then code.

---

## 📋 Entropy Backlog (ROI-ordered)

ROI = Entropy × Ease. Higher ROI = do first.

### ✅ P1: Core Plan Analysis Engine — COMPLETE

| Task | Description | Status | Tests |
|------|-------------|--------|-------|
| P1a | Plan data models (MedicalPlan, DentalPlan, VisionPlan) | ✅ | `test_plans.py` (18) |
| P1b | Scenario definitions | ✅ | `test_scenarios.py` (16) |
| P1c | Geometric mean / log-wealth calculation | ✅ | `test_geometric_mean.py` (15) |
| P1d | Plan comparison (Gold vs Platinum) | ✅ | `test_compare.py` (12) |
| **Total** | **61 tests passing** | ✅ | — |

#### Design: Data Models

```python
# src/insurance/plans.py
@dataclass
class MedicalPlan:
    """Medical insurance plan with cost-sharing details.
    
    Attributes:
        name: Plan name (e.g., "Blue Shield Gold 80 PPO")
        annual_premium: Total annual premium (after subsidies if any)
        in_network_oop_max: Maximum out-of-pocket for in-network care
        deductible: Annual deductible before insurance pays
        expected_minor_oop: Estimated OOP for "normal year" usage
        oon_emergency_treated_as_in_network: Emergency OON uses in-network cost-sharing
        post_stabilization_oon_covered: Coverage for post-emergency OON care
        post_stabilization_exposure: Extra OOP risk if not covered
    """
    name: str
    annual_premium: float
    in_network_oop_max: float
    deductible: float = 0.0
    expected_minor_oop: float = 400.0
    oon_emergency_treated_as_in_network: bool = True  # No Surprises Act
    post_stabilization_oon_covered: bool = False  # Conservative for exchange plans
    post_stabilization_exposure: float = 30_000.0  # Tail risk estimate

@dataclass
class DentalPlan:
    """Dental insurance add-on."""
    name: str
    annual_premium: float
    expected_oop: float = 200.0  # Average annual dental OOP

@dataclass
class VisionPlan:
    """Vision insurance add-on."""
    name: str
    annual_premium: float
    expected_oop: float = 50.0  # Average annual vision OOP
```

#### Design: Scenarios

```python
# src/insurance/scenarios.py
@dataclass
class Scenario:
    """A possible healthcare outcome scenario.
    
    Uses EQUAL WEIGHTING by default (Spitznagel approach).
    Probability is for reference/documentation only.
    """
    name: str
    probability: float  # Reference only
    medical_oop: float  # Out-of-pocket medical costs
    extra_oon: float = 0.0  # Additional OON costs (post-stabilization)

# Default scenarios (equally weighted for geometric mean)
DEFAULT_SCENARIOS = [
    Scenario("no_use", 0.70, 0.0),
    Scenario("minor_use", 0.25, None),  # Filled from plan.expected_minor_oop
    Scenario("cat_in_network", 0.03, None),  # Filled from plan.in_network_oop_max
    Scenario("cat_oon_emergency", 0.02, None, extra_oon=None),  # OON + post-stabilization
]
```

#### Design: Geometric Mean Calculation

```python
# src/insurance/geometric_mean.py
def compute_expected_log_wealth(
    annual_income: float,
    annual_baseline_spend: float,
    plan: MedicalPlan,
    scenarios: List[Scenario],
    dental: Optional[DentalPlan] = None,
    vision: Optional[VisionPlan] = None,
) -> float:
    """Compute expected log-wealth (geometric mean objective).
    
    The geometric mean is dominated by the MINIMUM outcome.
    Spitznagel's key insight: tail protection matters more than expected value.
    
    Args:
        annual_income: Gross annual income
        annual_baseline_spend: Fixed non-health spending (rent, food, etc.)
        plan: Medical plan to evaluate
        scenarios: List of possible outcomes
        dental: Optional dental add-on
        vision: Optional vision add-on
        
    Returns:
        Expected log of relative wealth: E[log(W/W₀)]
        where W₀ = income - baseline_spend (disposable income)
    """
```

---

## 📁 Module Map

| Module | Purpose |
|--------|---------|
| `src/insurance/plans.py` | Plan data models |
| `src/insurance/scenarios.py` | Scenario definitions |
| `src/insurance/geometric_mean.py` | GM calculation (Spitznagel) |
| `src/insurance/compare.py` | Plan comparison utilities |
| `tests/insurance/` | TDD tests |

---

## 🔑 Key Insight: Why Geometric Mean?

From Spitznagel's "The Tao of Capital":

> "The arithmetic mean can mislead. A strategy with high average returns but occasional catastrophic losses will underperform a more modest but consistent strategy over time."

**For health insurance**:
- Arithmetic mean favors Gold (lower premiums, same "average" outcome)
- Geometric mean may favor Platinum (lower catastrophic loss ceiling)

The geometric mean naturally penalizes strategies with high variance in the downside.

---

## 📐 Mathematical Framework

### Log-Wealth Objective

```
E[log(W)] = (1/n) × Σᵢ log(Wᵢ)
```

where:
- `Wᵢ = Income - Baseline - Premium - OOPᵢ`
- `n` = number of scenarios (EQUAL weighting)

### Why Equal Weighting?

Probability estimates are uncertain. Equal weighting:
1. Avoids false precision in probability estimates
2. Ensures all scenarios matter (no scenario is "negligible")
3. Makes the analysis robust to probability errors

---

## ✅ Execution Checklist

Before implementing any feature:

1. [ ] Write failing test first (TDD)
2. [ ] Keep functions <50 lines
3. [ ] Use dataclasses for structured data
4. [ ] Docstrings with Args/Returns
5. [ ] Run `pytest -v` after each change

---

## 🚀 Next Steps

After P1 is complete:

| Task | Description | Entropy | Ease | ROI |
|------|-------------|---------|------|-----|
| P2 | Load real Covered California 2026 plan data | 6 | 5 | 30 |
| P3 | Sensitivity analysis (vary probabilities) | 4 | 7 | 28 |
| P4 | Visualization (scenario waterfall chart) | 3 | 8 | 24 |
| P5 | CLI for plan comparison | 3 | 6 | 18 |
