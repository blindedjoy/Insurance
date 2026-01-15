"""Shared fixtures for insurance tests.

These fixtures provide reusable test data following DRY principles.
All values are from Covered California 2026 research (Jan 2026).
"""

import pytest
from src.insurance.plans import MedicalPlan, DentalPlan, VisionPlan, NetworkType
from src.insurance.scenarios import Scenario


# =============================================================================
# Plan Fixtures - Real 2026 Covered California Numbers
# Source: docs/research/prompt b responses/
# All premiums for SF couple, age 35, no subsidies
# =============================================================================

@pytest.fixture
def kaiser_gold_hmo() -> MedicalPlan:
    """Kaiser Permanente Gold HMO - lowest premium, integrated network.
    
    2026 Research findings:
    - Has 1,100+ physicians in Colorado (better travel coverage than expected)
    - Visiting Member Program for out-of-area care
    - 24/7 authorization line: 1-800-225-8883
    """
    return MedicalPlan(
        name="Kaiser Gold HMO",
        annual_premium=18_456.0,  # $1,538/month × 2
        in_network_oop_max=18_400.0,  # $9,200 × 2 (couple)
        network_type=NetworkType.HMO,
        deductible=0.0,
        expected_minor_oop=400.0,  # $40 PCP + some visits
        oon_emergency_treated_as_in_network=True,
        post_stabilization_oon_covered=False,
        post_stabilization_exposure=15_000.0,  # Expected case from research
        # HMO: no meaningful OON coverage
        oon_deductible=0.0,
        oon_oop_max=0.0,
        oon_coinsurance=1.0,
        ground_ambulance_exposure=1_500.0,
    )


@pytest.fixture
def kaiser_platinum_hmo() -> MedicalPlan:
    """Kaiser Permanente Platinum HMO - lower OOP max, higher premium."""
    return MedicalPlan(
        name="Kaiser Platinum HMO",
        annual_premium=19_824.0,  # $1,652/month × 2
        in_network_oop_max=10_000.0,  # $5,000 × 2 (couple)
        network_type=NetworkType.HMO,
        deductible=0.0,
        expected_minor_oop=200.0,  # $15 PCP copay (lower)
        oon_emergency_treated_as_in_network=True,
        post_stabilization_oon_covered=False,
        post_stabilization_exposure=15_000.0,
        oon_deductible=0.0,
        oon_oop_max=0.0,
        oon_coinsurance=1.0,
        ground_ambulance_exposure=1_500.0,
    )


@pytest.fixture
def blue_shield_trio_gold_hmo() -> MedicalPlan:
    """Blue Shield Trio Gold HMO - narrow network (UCSF, Dignity).
    
    2026 Research findings:
    - Has BlueCard national network for emergencies
    - Away From Home Care program
    - Slightly better OON flexibility than Kaiser
    """
    return MedicalPlan(
        name="Blue Shield Trio Gold HMO",
        annual_premium=18_600.0,  # $1,550/month × 2
        in_network_oop_max=18_400.0,  # $9,200 × 2
        network_type=NetworkType.HMO,
        deductible=0.0,
        expected_minor_oop=400.0,
        oon_emergency_treated_as_in_network=True,
        post_stabilization_oon_covered=False,  # Still HMO rules
        post_stabilization_exposure=15_000.0,
        oon_deductible=0.0,
        oon_oop_max=0.0,
        oon_coinsurance=1.0,
        ground_ambulance_exposure=1_500.0,
    )


@pytest.fixture
def blue_shield_trio_platinum_hmo() -> MedicalPlan:
    """Blue Shield Trio Platinum HMO - ChatGPT's recommended plan."""
    return MedicalPlan(
        name="Blue Shield Trio Platinum HMO",
        annual_premium=21_672.0,  # $1,806/month × 2
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


@pytest.fixture
def gold_ppo_plan() -> MedicalPlan:
    """Blue Shield Gold 80 PPO - broad network, OON coverage exists.
    
    2026 Research findings:
    - $8,712/year premium penalty vs Kaiser Gold
    - OON coverage has gaps (50% coinsurance, $5.5k deductible)
    - Both sources say hard to justify premium
    """
    return MedicalPlan(
        name="Blue Shield Gold 80 PPO",
        annual_premium=27_168.0,  # $2,264/month × 2
        in_network_oop_max=18_400.0,  # $9,200 × 2
        network_type=NetworkType.PPO,
        deductible=0.0,
        expected_minor_oop=400.0,  # $40 PCP copay
        oon_emergency_treated_as_in_network=True,
        post_stabilization_oon_covered=True,  # PPO has some OON coverage
        post_stabilization_exposure=15_000.0,  # Still exposed after OON deductible
        # PPO OON fields (from research)
        oon_deductible=5_500.0,
        oon_oop_max=50_000.0,  # $25,000 × 2 couple
        oon_coinsurance=0.50,  # You pay 50%
        ground_ambulance_exposure=1_500.0,
    )


@pytest.fixture
def platinum_ppo_plan() -> MedicalPlan:
    """Blue Shield Platinum 90 PPO - richest benefits, highest premium."""
    return MedicalPlan(
        name="Blue Shield Platinum 90 PPO",
        annual_premium=36_936.0,  # $3,078/month × 2
        in_network_oop_max=10_000.0,  # $5,000 × 2
        network_type=NetworkType.PPO,
        deductible=0.0,
        expected_minor_oop=200.0,  # $15 PCP copay
        oon_emergency_treated_as_in_network=True,
        post_stabilization_oon_covered=True,
        post_stabilization_exposure=10_000.0,  # Lower due to OON coverage
        oon_deductible=5_500.0,
        oon_oop_max=50_000.0,
        oon_coinsurance=0.50,
        ground_ambulance_exposure=1_500.0,
    )


@pytest.fixture
def anthem_gold_epo() -> MedicalPlan:
    """Anthem Blue Cross Gold EPO - broad network, no OON coverage."""
    return MedicalPlan(
        name="Anthem Blue Cross Gold EPO",
        annual_premium=22_000.0,  # Estimated
        in_network_oop_max=18_400.0,
        network_type=NetworkType.EPO,
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


@pytest.fixture
def basic_dental() -> DentalPlan:
    """Delta Dental PPO from Covered California."""
    return DentalPlan(
        name="Delta Dental PPO",
        annual_premium=800.0,
        expected_oop=200.0,
    )


@pytest.fixture
def basic_vision() -> VisionPlan:
    """VSP Vision from Covered California."""
    return VisionPlan(
        name="VSP Vision",
        annual_premium=300.0,
        expected_oop=50.0,
    )


# =============================================================================
# Scenario Fixtures - Updated with Research Findings
# =============================================================================

@pytest.fixture
def no_use_scenario() -> Scenario:
    """Healthy year - no healthcare usage (70% probability)."""
    return Scenario(
        name="no_use",
        probability=0.70,
        medical_oop=0.0,
    )


@pytest.fixture
def minor_use_scenario() -> Scenario:
    """Typical year - some doctor visits, prescriptions (25% probability)."""
    return Scenario(
        name="minor_use",
        probability=0.25,
        medical_oop=400.0,
    )


@pytest.fixture
def high_use_scenario() -> Scenario:
    """High cost year - one person hits significant costs (8% probability)."""
    return Scenario(
        name="high_use",
        probability=0.08,
        medical_oop=5_000.0,  # One person with moderate costs
    )


@pytest.fixture
def cat_in_network_scenario() -> Scenario:
    """Catastrophic event in-network - both hit OOP max (3% probability)."""
    return Scenario(
        name="cat_in_network",
        probability=0.03,
        medical_oop=18_400.0,  # Gold couple OOP max
    )


@pytest.fixture
def cat_oon_scenario() -> Scenario:
    """Catastrophic event out-of-network (Colorado skiing accident).
    
    Research tiered exposure:
    - Best case: $3,000 (30%)
    - Expected: $15,000 (50%)
    - Moderate worst: $35,000 (18%)
    - Catastrophic: $75,000 (2%)
    
    Using expected case ($15k) + ground ambulance ($1.5k) for model.
    """
    return Scenario(
        name="cat_oon_emergency",
        probability=0.02,
        medical_oop=18_400.0,  # Emergency at in-network rates
        extra_oon=16_500.0,  # $15k post-stab + $1.5k ground ambulance
    )


@pytest.fixture
def default_scenarios(
    no_use_scenario,
    minor_use_scenario,
    cat_in_network_scenario,
    cat_oon_scenario,
) -> list[Scenario]:
    """Default scenario set for plan comparison."""
    return [
        no_use_scenario,
        minor_use_scenario,
        cat_in_network_scenario,
        cat_oon_scenario,
    ]


# =============================================================================
# Financial Fixtures
# =============================================================================

@pytest.fixture
def typical_couple_income() -> float:
    """Typical SF couple household income (no subsidies at this level)."""
    return 240_000.0


@pytest.fixture
def typical_baseline_spend() -> float:
    """Typical annual baseline spending (rent, food, etc.)."""
    return 120_000.0


@pytest.fixture
def typical_tax_rate() -> float:
    """Effective tax rate for SF couple at $240k income."""
    return 0.35  # ~35% federal + state + FICA
