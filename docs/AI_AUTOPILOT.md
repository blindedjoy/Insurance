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

### 🔄 P2: Config Refactor + Network Modeling — IN PROGRESS

#### P2a: Config Objects (Uncle Bob)

**Problem**: Functions have too many arguments (>3).

**Solution**: Create config dataclasses.

```python
# src/insurance/config.py
@dataclass
class FinancialConfig:
    """Household financial parameters."""
    gross_income: float
    tax_rate: float
    baseline_spend: float
    
    @property
    def after_tax_income(self) -> float:
        return self.gross_income * (1 - self.tax_rate)
    
    @property
    def disposable_income(self) -> float:
        return self.after_tax_income - self.baseline_spend


@dataclass
class PlanBundle:
    """Medical + optional dental/vision."""
    medical: MedicalPlan
    dental: Optional[DentalPlan] = None
    vision: Optional[VisionPlan] = None
    
    @property
    def total_premium(self) -> float:
        return sum(p.annual_premium for p in [self.medical, self.dental, self.vision] if p)


# Refactored function signature:
def compute_expected_log_wealth(
    config: FinancialConfig,
    bundle: PlanBundle,
    scenarios: List[Scenario],
) -> float:
    """Now has only 3 arguments (Uncle Bob approved)."""
```

| Sub-task | Description | Tests |
|----------|-------------|-------|
| P2a.1 | Create `FinancialConfig` | `test_config.py` |
| P2a.2 | Create `PlanBundle` | `test_config.py` |
| P2a.3 | Refactor `compute_expected_log_wealth` | Update existing |
| P2a.4 | Refactor `compare_plans` | Update existing |

---

#### P2b: Network Type Modeling

**Problem**: Current model ignores HMO/PPO/EPO differences.

**Solution**: Add network type to `MedicalPlan` with OON coverage rules.

```python
# src/insurance/plans.py
from enum import Enum

class NetworkType(Enum):
    HMO = "hmo"      # Referrals required, OON emergency only
    PPO = "ppo"      # No referrals, some OON coverage
    EPO = "epo"      # No referrals, NO OON coverage (except emergency)


@dataclass
class OONCoverageRules:
    """Out-of-network coverage rules by situation."""
    emergency_covered: bool = True  # Always True per No Surprises Act
    emergency_cost_share: float = 1.0  # 1.0 = in-network rates, <1.0 = partial
    post_stabilization_covered: bool = False
    post_stabilization_cost_share: float = 0.0  # 0.0 = you pay 100%
    elective_oon_covered: bool = False


# Default rules by network type
DEFAULT_OON_RULES = {
    NetworkType.HMO: OONCoverageRules(
        emergency_covered=True,
        emergency_cost_share=1.0,
        post_stabilization_covered=False,
        post_stabilization_cost_share=0.0,
        elective_oon_covered=False,
    ),
    NetworkType.PPO: OONCoverageRules(
        emergency_covered=True,
        emergency_cost_share=1.0,
        post_stabilization_covered=True,  # Usually some coverage
        post_stabilization_cost_share=0.5,  # 50% covered (estimate)
        elective_oon_covered=False,  # Not on exchange plans
    ),
    NetworkType.EPO: OONCoverageRules(
        emergency_covered=True,
        emergency_cost_share=1.0,
        post_stabilization_covered=False,
        post_stabilization_cost_share=0.0,
        elective_oon_covered=False,
    ),
}
```

| Sub-task | Description | Tests |
|----------|-------------|-------|
| P2b.1 | Add `NetworkType` enum | `test_plans.py` |
| P2b.2 | Add `OONCoverageRules` | `test_plans.py` |
| P2b.3 | Update `MedicalPlan` with network_type | `test_plans.py` |
| P2b.4 | Update scenario builder for network rules | `test_scenarios.py` |

---

#### P2c: OON Probability Model (Requires Research)

**Problem**: What's the probability of needing OON care?

**Current assumption**: Fixed $30k post-stabilization exposure.

**Better model** (after research):

```python
@dataclass
class OONScenarioConfig:
    """Configuration for out-of-network scenarios."""
    # Probability of needing OON care at all
    p_oon_event: float = 0.02  # 2% annual chance
    
    # Given OON event, probability of each situation
    p_emergency_only: float = 0.70  # Just ER, no follow-up
    p_needs_post_stabilization: float = 0.25  # PT, rehab, etc.
    p_needs_extended_oon: float = 0.05  # Surgery, long-term
    
    # Cost distributions (mean, std for log-normal?)
    emergency_cost_mean: float = 15_000
    post_stab_cost_mean: float = 30_000
    extended_cost_mean: float = 100_000
```

**Research questions for ChatGPT 5.2**:
1. What's the actual probability of OON emergency for SF residents?
2. What does "post-stabilization" mean exactly?
3. What's typical cost for OON follow-up care?

---

## 📁 Module Map

| Module | Purpose | Uncle Bob Status |
|--------|---------|------------------|
| `src/insurance/plans.py` | Plan data models | ✅ Good |
| `src/insurance/scenarios.py` | Scenario definitions | ⚠️ Needs network type |
| `src/insurance/geometric_mean.py` | GM calculation | ⚠️ Too many args |
| `src/insurance/compare.py` | Plan comparison | ⚠️ Too many args |
| `src/insurance/config.py` | **NEW** Config objects | 📋 P2a |

---

## 🔬 Research Tasks (for ChatGPT 5.2)

Use ChatGPT 5.2 for current/factual questions. Bring findings back here.

**Full prompts**: See `docs/research/RESEARCH_PROMPTS.md`

### Priority Research (Medical Tail Risk)

| Task | Topic | Critical For |
|------|-------|--------------|
| **R1** | Network type coverage rules (HMO/PPO/EPO) | P2b |
| **R2** | Kaiser network + travel risk | Kaiser vs PPO decision |
| **R3** | Gold vs Platinum comparison | Premium vs OOP trade-off |
| **R4** | Post-stabilization cost estimates | $30k assumption validation |

### Optional Research (Lower Priority)

| Task | Topic | Why Optional |
|------|-------|--------------|
| R5 | Dental plan details | No catastrophic tail risk |
| R6 | Vision plan details | No catastrophic tail risk |

**Rationale**: Dental/vision have capped annual maximums. No "Colorado catastrophe" equivalent. Can research later if needed for completeness.

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

### OON Scenario (to be refined)

```
Current (simplistic):
  oon_oop = in_network_oop_max + post_stabilization_exposure

Better (after P2b/P2c):
  oon_oop = emergency_oop × (1 - emergency_cost_share)
          + post_stab_cost × (1 - post_stab_cost_share)
          
  Where cost_share depends on NetworkType
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

## 🚀 Priority Order

| Priority | Task | Blocker? |
|----------|------|----------|
| 1 | **P2a**: Config refactor | No |
| 2 | **R1-R4**: Research tasks | No (parallel) |
| 3 | **P2b**: Network type modeling | Needs R1 |
| 4 | **P2c**: OON probability model | Needs R3, R4 |
| 5 | **P3**: Real plan data | Needs P2a |
| 6 | **P4**: Visualization | Needs P3 |
