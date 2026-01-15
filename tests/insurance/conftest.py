"""Shared fixtures for insurance tests.

Fixtures use the shared data module (src/insurance/data.py) to avoid DRY violations.
All values are from Covered California 2026 research (Jan 2026).
"""

import pytest
from src.insurance.plans import MedicalPlan, DentalPlan, VisionPlan, NetworkType
from src.insurance.scenarios import Scenario
from src.insurance.data import (
    KAISER_GOLD_HMO,
    KAISER_PLATINUM_HMO,
    BLUE_SHIELD_TRIO_GOLD_HMO,
    BLUE_SHIELD_TRIO_PLATINUM_HMO,
    BLUE_SHIELD_GOLD_PPO,
    BLUE_SHIELD_PLATINUM_PPO,
    DELTA_DENTAL,
    VSP_VISION,
    DEFAULT_GROSS_INCOME,
    DEFAULT_TAX_RATE,
    DEFAULT_BASELINE_SPEND,
)


# =============================================================================
# Plan Fixtures - Using shared data module (Single Source of Truth)
# =============================================================================

@pytest.fixture
def kaiser_gold_hmo() -> MedicalPlan:
    """Kaiser Permanente Gold HMO - lowest premium, integrated network."""
    return KAISER_GOLD_HMO


@pytest.fixture
def kaiser_platinum_hmo() -> MedicalPlan:
    """Kaiser Permanente Platinum HMO - lower OOP max, higher premium."""
    return KAISER_PLATINUM_HMO


@pytest.fixture
def blue_shield_trio_gold_hmo() -> MedicalPlan:
    """Blue Shield Trio Gold HMO - narrow network (UCSF, Dignity)."""
    return BLUE_SHIELD_TRIO_GOLD_HMO


@pytest.fixture
def blue_shield_trio_platinum_hmo() -> MedicalPlan:
    """Blue Shield Trio Platinum HMO - ChatGPT's recommended plan."""
    return BLUE_SHIELD_TRIO_PLATINUM_HMO


@pytest.fixture
def gold_ppo_plan() -> MedicalPlan:
    """Blue Shield Gold 80 PPO - broad network, OON coverage exists."""
    return BLUE_SHIELD_GOLD_PPO


@pytest.fixture
def platinum_ppo_plan() -> MedicalPlan:
    """Blue Shield Platinum 90 PPO - richest benefits, highest premium."""
    return BLUE_SHIELD_PLATINUM_PPO


@pytest.fixture
def anthem_gold_epo() -> MedicalPlan:
    """Anthem Blue Cross Gold EPO - broad network, no OON coverage."""
    # EPO not in shared data yet - keep inline for now
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
    return DELTA_DENTAL


@pytest.fixture
def basic_vision() -> VisionPlan:
    """VSP Vision from Covered California."""
    return VSP_VISION


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
