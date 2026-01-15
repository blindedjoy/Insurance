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
# PLAN DEFINITIONS (from 2026 Covered California research - Jan 2026)
# Source: docs/research/prompt b responses/
# All premiums for SF couple, age 35, no subsidies
# =============================================================================

# --- HMOs (recommended by both AI models) ---

kaiser_gold = MedicalPlan(
    name="Kaiser Gold HMO",
    annual_premium=18_456,  # $1,538/month (LOWEST)
    in_network_oop_max=18_400,  # $9,200 × 2 (couple)
    deductible=0,
    expected_minor_oop=400,  # $40 PCP copay
)

kaiser_platinum = MedicalPlan(
    name="Kaiser Platinum HMO",
    annual_premium=19_824,  # $1,652/month
    in_network_oop_max=10_000,  # $5,000 × 2 (better put protection!)
    deductible=0,
    expected_minor_oop=200,  # $15 PCP copay
)

blue_shield_trio_gold = MedicalPlan(
    name="Blue Shield Trio Gold HMO",
    annual_premium=18_600,  # $1,550/month
    in_network_oop_max=18_400,  # Same as Kaiser Gold
    deductible=0,
    expected_minor_oop=400,
)

blue_shield_trio_platinum = MedicalPlan(
    name="Blue Shield Trio Platinum HMO",
    annual_premium=21_672,  # $1,806/month (ChatGPT's pick)
    in_network_oop_max=10_000,  # $5,000 × 2
    deductible=0,
    expected_minor_oop=200,
)

# --- PPOs (hard to justify per research) ---

gold_ppo = MedicalPlan(
    name="Blue Shield Gold 80 PPO",
    annual_premium=27_168,  # $2,264/month (+$8,712/yr vs Kaiser Gold!)
    in_network_oop_max=18_400,
    deductible=0,
    expected_minor_oop=400,
)

platinum_ppo = MedicalPlan(
    name="Blue Shield Platinum 90 PPO",
    annual_premium=36_936,  # $3,078/month (HIGHEST)
    in_network_oop_max=10_000,
    deductible=0,
    expected_minor_oop=200,
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

# Post-stabilization exposure from research (expected case)
POST_STAB_EXPOSURE = 15_000  # Expected case from tiered model
GROUND_AMBULANCE = 1_500  # Not protected by No Surprises Act

def demo_plan_scenarios(plan: MedicalPlan, label: str) -> tuple[list[float], float]:
    """Show wealth ratios for a plan across scenarios."""
    print(f"\n--- {label} ---")
    print(f"  Premium: ${plan.annual_premium + dental.annual_premium + vision.annual_premium:,.0f}/year")
    print(f"  OOP Max: ${plan.in_network_oop_max:,.0f} (couple)")
    
    scenarios = [
        ("No Use (70%)", 0, 0.70),
        ("Minor Use (25%)", plan.expected_minor_oop + dental.expected_oop + vision.expected_oop, 0.25),
        ("Catastrophe in-network (3%)", plan.in_network_oop_max + dental.expected_oop + vision.expected_oop, 0.03),
        ("Catastrophe OON Colorado (2%)", plan.in_network_oop_max + POST_STAB_EXPOSURE + GROUND_AMBULANCE + dental.expected_oop + vision.expected_oop, 0.02),
    ]
    
    total_premium = plan.annual_premium + dental.annual_premium + vision.annual_premium
    ratios = []
    
    for name, oop, prob in scenarios:
        ratio = compute_wealth_ratio(
            disposable_income=DISPOSABLE,
            total_premium=total_premium,
            scenario_oop=oop,
        )
        ratios.append(ratio)
        remaining = ratio * DISPOSABLE
        print(f"  {name:35s}: {ratio:.2%} (${remaining:,.0f})")
    
    gm = compute_geometric_mean_ratio(ratios)
    print(f"\n  Geometric Mean Ratio: {gm:.2%}")
    print(f"  GM Wealth:            ${gm * DISPOSABLE:,.0f}")
    return ratios, gm

# Compare Gold vs Platinum (the key question!)
print("\n" + "="*70)
print("GOLD vs PLATINUM COMPARISON")
print("="*70)

kaiser_gold_ratios, kaiser_gold_gm = demo_plan_scenarios(kaiser_gold, "Kaiser GOLD HMO ($18,456/yr)")
kaiser_plat_ratios, kaiser_plat_gm = demo_plan_scenarios(kaiser_platinum, "Kaiser PLATINUM HMO ($19,824/yr)")

print("\n" + "-"*70)
print("KEY INSIGHT: Kaiser Platinum IS worth it")
print("-"*70)
print(f"  Premium difference: ${kaiser_platinum.annual_premium - kaiser_gold.annual_premium:,.0f}/year")
print(f"  OOP max savings:    ${kaiser_gold.in_network_oop_max - kaiser_platinum.in_network_oop_max:,.0f} in catastrophe")
print(f"  Net benefit:        ${(kaiser_gold.in_network_oop_max - kaiser_platinum.in_network_oop_max) - (kaiser_platinum.annual_premium - kaiser_gold.annual_premium):,.0f} in worst case")
print(f"\n  Gold GM:     {kaiser_gold_gm:.2%}")
print(f"  Platinum GM: {kaiser_plat_gm:.2%}")
if kaiser_plat_gm > kaiser_gold_gm:
    print(f"  ✅ Platinum wins by {(kaiser_plat_gm - kaiser_gold_gm)*100:.2f} percentage points")
else:
    print(f"  ⚠️  Gold wins - catastrophe not likely enough to justify premium")

# =============================================================================
# FULL PLAN COMPARISON (All 6 Plans)
# =============================================================================

print("\n" + "="*70)
print("FULL PLAN COMPARISON (Geometric Mean Ranking)")
print("="*70)

all_plans = [
    kaiser_gold,
    kaiser_platinum,
    blue_shield_trio_gold,
    blue_shield_trio_platinum,
    gold_ppo,
    platinum_ppo,
]

results = compare_plans(
    plans=all_plans,
    annual_income=AFTER_TAX_INCOME,
    annual_baseline_spend=BASELINE_SPEND,
    dental=dental,
    vision=vision,
)

print(f"\n{format_comparison_table(results)}")

print(f"\n🏆 Winner: {results[0].plan_name}")

print(f"\n--- Winner's Scenario Ratios ---")
for name, ratio in results[0].scenario_ratios.items():
    print(f"  {name:25s}: {ratio:.1%}")

print(f"\n" + "="*70)
print("KEY INSIGHTS (Spitznagel / Tao of Capital)")
print("="*70)
print("""
1. GEOMETRIC MEAN IS DOMINATED BY THE MINIMUM
   Any near-zero outcome (catastrophe) drives GM toward zero.
   This is why downside protection matters more than expected value.

2. PLATINUM WINS FOR KAISER (but NOT for PPO)
   - Kaiser: +$1,368 premium → -$8,400 OOP max = +$7,032 net benefit
   - PPO:    +$9,768 premium → -$8,400 OOP max = -$1,368 net LOSS

3. AVOID PPO (both research sources agree)
   - $8,712/year premium penalty vs Kaiser Gold
   - OON coverage has gaps (50% coinsurance, $5.5k deductible)
   - Not worth it for occasional travel risk

4. HMO TRAVEL RISK IS OVERBLOWN
   - Emergency: Protected by No Surprises Act
   - Kaiser has 1,100+ doctors in Colorado
   - Blue Shield has BlueCard national network
   - Post-stabilization exposure: ~$15k expected (manageable)

5. THE INSURANCE "PUT"
   OOP maximum = your strike price (caps downside loss)
   Lower OOP max = better put protection = higher geometric mean
""")
