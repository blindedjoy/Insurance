#!/usr/bin/env python3
"""Demo: Compare health insurance plans using Spitznagel's geometric mean approach.

Wealth ratios (Spitznagel / Tao of Capital):
- 1.0 = kept all disposable income (no health spending)
- 0.9 = kept 90% (spent 10% on health)
- 0.0 = total loss (all gone to health costs)

The geometric mean is dominated by the MINIMUM outcome.
Any near-zero outcome (catastrophe) drives GM toward zero.
"""

from src.insurance import (
    MedicalPlan, DentalPlan, VisionPlan,
    compare_plans, format_comparison_table,
)
from src.insurance.geometric_mean import compute_wealth_ratio, compute_geometric_mean_ratio

# =============================================================================
# PLAN DEFINITIONS (from Covered California research)
# =============================================================================

gold_ppo = MedicalPlan(
    name="Blue Shield Gold 80 PPO",
    annual_premium=24_000,  # ~$2000/month couple
    in_network_oop_max=17_400,
    deductible=0,
    expected_minor_oop=400,
)

platinum_ppo = MedicalPlan(
    name="Blue Shield Platinum 90 PPO",
    annual_premium=30_000,  # Higher premium
    in_network_oop_max=8_700,  # Lower OOP max (the "put protection")
    deductible=0,
    expected_minor_oop=300,
)

kaiser_gold = MedicalPlan(
    name="Kaiser Gold HMO",
    annual_premium=18_000,
    in_network_oop_max=8_700,
    deductible=0,
    expected_minor_oop=350,
)

blue_shield_trio = MedicalPlan(
    name="Blue Shield Gold Trio HMO",
    annual_premium=21_000,
    in_network_oop_max=8_700,
    deductible=0,
    expected_minor_oop=400,
)

# Add-ons
dental = DentalPlan(name="Delta Dental", annual_premium=800, expected_oop=200)
vision = VisionPlan(name="VSP Vision", annual_premium=300, expected_oop=50)

# =============================================================================
# FINANCIAL PARAMETERS
# =============================================================================

GROSS_INCOME = 240_000  # SF couple
TAX_RATE = 0.30  # ~30% effective (fed + CA state)
AFTER_TAX_INCOME = GROSS_INCOME * (1 - TAX_RATE)  # $168,000
BASELINE_SPEND = 80_000  # Rent, food, etc.
DISPOSABLE = AFTER_TAX_INCOME - BASELINE_SPEND  # $88,000

# =============================================================================
# DEMO: WEALTH RATIO CALCULATION
# =============================================================================

print("\n" + "="*70)
print("SPITZNAGEL WEALTH RATIO DEMO")
print("="*70)

print(f"\nFinancial Setup:")
print(f"  Gross Income:     ${GROSS_INCOME:,}")
print(f"  Tax Rate:         {TAX_RATE:.0%}")
print(f"  After-Tax Income: ${AFTER_TAX_INCOME:,}")
print(f"  Baseline Spend:   ${BASELINE_SPEND:,}")
print(f"  Disposable:       ${DISPOSABLE:,}  ← This is '1.0' on the ratio scale")

print(f"\n--- Kaiser Gold HMO Wealth Ratios by Scenario ---")
print(f"  (Premium: ${kaiser_gold.annual_premium + dental.annual_premium + vision.annual_premium:,})")

scenarios = [
    ("No Use", 0),
    ("Minor Use", kaiser_gold.expected_minor_oop + dental.expected_oop + vision.expected_oop),
    ("Catastrophe (in-network)", kaiser_gold.in_network_oop_max + dental.expected_oop + vision.expected_oop),
    ("Catastrophe (OON emergency)", kaiser_gold.in_network_oop_max + 30_000 + dental.expected_oop + vision.expected_oop),
]

total_premium = kaiser_gold.annual_premium + dental.annual_premium + vision.annual_premium
ratios = []

for name, oop in scenarios:
    ratio = compute_wealth_ratio(
        disposable_income=DISPOSABLE,
        total_premium=total_premium,
        scenario_oop=oop,
    )
    ratios.append(ratio)
    remaining = ratio * DISPOSABLE
    print(f"  {name:30s}: {ratio:.2%} (${remaining:,.0f})")

gm = compute_geometric_mean_ratio(ratios)
print(f"\n  Geometric Mean Ratio: {gm:.2%}")
print(f"  GM Wealth:            ${gm * DISPOSABLE:,.0f}")

print(f"\n  ⚠️  Note: The OON catastrophe ({ratios[-1]:.1%}) pulls down the GM significantly!")
print(f"      This is Spitznagel's key insight: tail risk dominates.")

# =============================================================================
# DEMO: PLAN COMPARISON
# =============================================================================

print("\n" + "="*70)
print("PLAN COMPARISON (Geometric Mean Ranking)")
print("="*70)

results = compare_plans(
    plans=[gold_ppo, platinum_ppo, kaiser_gold, blue_shield_trio],
    annual_income=AFTER_TAX_INCOME,  # Using after-tax
    annual_baseline_spend=BASELINE_SPEND,
    dental=dental,
    vision=vision,
)

print(f"\n{format_comparison_table(results)}")

print(f"\n🏆 Winner: {results[0].plan_name}")

print(f"\n--- Winner's Scenario Ratios ---")
for name, ratio in results[0].scenario_ratios.items():
    print(f"  {name:25s}: {ratio:.1%}")

print(f"\n--- Key Insight (Spitznagel / Tao of Capital) ---")
print("The geometric mean naturally penalizes high-variance downside.")
print("Plans with lower OOP max (better 'put protection') win because they")
print("prevent the catastrophic scenario from dominating the GM calculation.")
print("\nThe insurance 'put' is the OOP maximum - it caps your downside loss.")
