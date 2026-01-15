"""Shared plan data - Single Source of Truth.

All plan definitions in one place to avoid DRY violations.
Data from 2026 Covered California research (Jan 2026).
Source: docs/research/prompt b responses/

All premiums for SF couple, age 35, no subsidies.
"""

from src.insurance.plans import MedicalPlan, DentalPlan, VisionPlan, NetworkType


# =============================================================================
# FINANCIAL DEFAULTS (SF couple, $240k gross)
# 
# NOTE: BLS says SF average household spends ~$110-130k/year.
# BUT at $130k baseline + $55k max health cost = RUIN at $240k income!
# Using $80k baseline to allow meaningful analysis.
# User should customize to their actual spending.
# =============================================================================

DEFAULT_GROSS_INCOME = 240_000
DEFAULT_TAX_RATE = 0.30  # Fed + CA state for $240k couple (conservative)
DEFAULT_BASELINE_SPEND = 80_000  # Allows survival in catastrophe

# Calculated
DEFAULT_AFTER_TAX = DEFAULT_GROSS_INCOME * (1 - DEFAULT_TAX_RATE)  # $168,000
DEFAULT_DISPOSABLE = DEFAULT_AFTER_TAX - DEFAULT_BASELINE_SPEND  # $88,000


# =============================================================================
# MEDICAL PLANS - HMOs (recommended by research)
# =============================================================================

KAISER_GOLD_HMO = MedicalPlan(
    name="Kaiser Gold HMO",
    annual_premium=18_456.0,  # $1,538/month (LOWEST)
    in_network_oop_max=18_400.0,  # $9,200 × 2 (couple)
    network_type=NetworkType.HMO,
    deductible=0.0,
    expected_minor_oop=400.0,  # $40 PCP copay
    oon_emergency_treated_as_in_network=True,
    post_stabilization_oon_covered=False,
    post_stabilization_exposure=15_000.0,  # Expected case from research
    oon_deductible=0.0,
    oon_oop_max=0.0,
    oon_coinsurance=1.0,
    ground_ambulance_exposure=1_500.0,
)

KAISER_PLATINUM_HMO = MedicalPlan(
    name="Kaiser Platinum HMO",
    annual_premium=19_824.0,  # $1,652/month
    in_network_oop_max=10_000.0,  # $5,000 × 2 (better put protection!)
    network_type=NetworkType.HMO,
    deductible=0.0,
    expected_minor_oop=200.0,  # $15 PCP copay
    oon_emergency_treated_as_in_network=True,
    post_stabilization_oon_covered=False,
    post_stabilization_exposure=15_000.0,
    oon_deductible=0.0,
    oon_oop_max=0.0,
    oon_coinsurance=1.0,
    ground_ambulance_exposure=1_500.0,
)

BLUE_SHIELD_TRIO_GOLD_HMO = MedicalPlan(
    name="Blue Shield Trio Gold HMO",
    annual_premium=18_600.0,  # $1,550/month
    in_network_oop_max=18_400.0,
    network_type=NetworkType.HMO,
    deductible=0.0,
    expected_minor_oop=400.0,
    oon_emergency_treated_as_in_network=True,
    post_stabilization_oon_covered=False,
    post_stabilization_exposure=15_000.0,
    oon_deductible=0.0,
    oon_oop_max=0.0,
    oon_coinsurance=1.0,
    ground_ambulance_exposure=1_500.0,
)

BLUE_SHIELD_TRIO_PLATINUM_HMO = MedicalPlan(
    name="Blue Shield Trio Platinum HMO",
    annual_premium=21_672.0,  # $1,806/month (ChatGPT's pick)
    in_network_oop_max=10_000.0,  # $5,000 × 2
    network_type=NetworkType.HMO,
    deductible=0.0,
    expected_minor_oop=200.0,
    oon_emergency_treated_as_in_network=True,
    post_stabilization_oon_covered=False,
    post_stabilization_exposure=15_000.0,
    oon_deductible=0.0,
    oon_oop_max=0.0,
    oon_coinsurance=1.0,
    ground_ambulance_exposure=1_500.0,
)


# =============================================================================
# MEDICAL PLANS - PPOs (hard to justify per research)
# =============================================================================

BLUE_SHIELD_GOLD_PPO = MedicalPlan(
    name="Blue Shield Gold 80 PPO",
    annual_premium=27_168.0,  # $2,264/month (+$8,712/yr vs Kaiser Gold!)
    in_network_oop_max=18_400.0,
    network_type=NetworkType.PPO,
    deductible=0.0,
    expected_minor_oop=400.0,
    oon_emergency_treated_as_in_network=True,
    post_stabilization_oon_covered=True,  # PPO has some OON coverage
    post_stabilization_exposure=15_000.0,  # Still exposed after OON deductible
    oon_deductible=5_500.0,
    oon_oop_max=50_000.0,  # $25,000 × 2 couple
    oon_coinsurance=0.50,  # You pay 50%
    ground_ambulance_exposure=1_500.0,
)

BLUE_SHIELD_PLATINUM_PPO = MedicalPlan(
    name="Blue Shield Platinum 90 PPO",
    annual_premium=36_936.0,  # $3,078/month (HIGHEST)
    in_network_oop_max=10_000.0,
    network_type=NetworkType.PPO,
    deductible=0.0,
    expected_minor_oop=200.0,
    oon_emergency_treated_as_in_network=True,
    post_stabilization_oon_covered=True,
    post_stabilization_exposure=10_000.0,  # Lower due to OON coverage
    oon_deductible=5_500.0,
    oon_oop_max=50_000.0,
    oon_coinsurance=0.50,
    ground_ambulance_exposure=1_500.0,
)


# =============================================================================
# ADD-ONS (Dental & Vision)
# =============================================================================

DELTA_DENTAL = DentalPlan(
    name="Delta Dental PPO",
    annual_premium=800.0,
    expected_oop=200.0,
)

VSP_VISION = VisionPlan(
    name="VSP Vision",
    annual_premium=300.0,
    expected_oop=50.0,
)


# =============================================================================
# CONVENIENCE LISTS
# =============================================================================

ALL_PLANS = [
    KAISER_GOLD_HMO,
    KAISER_PLATINUM_HMO,
    BLUE_SHIELD_TRIO_GOLD_HMO,
    BLUE_SHIELD_TRIO_PLATINUM_HMO,
    BLUE_SHIELD_GOLD_PPO,
    BLUE_SHIELD_PLATINUM_PPO,
]

HMO_PLANS = [
    KAISER_GOLD_HMO,
    KAISER_PLATINUM_HMO,
    BLUE_SHIELD_TRIO_GOLD_HMO,
    BLUE_SHIELD_TRIO_PLATINUM_HMO,
]

PPO_PLANS = [
    BLUE_SHIELD_GOLD_PPO,
    BLUE_SHIELD_PLATINUM_PPO,
]
