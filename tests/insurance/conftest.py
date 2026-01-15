"""Shared fixtures for insurance tests.

These fixtures provide reusable test data following DRY principles.
"""

import pytest
from src.insurance.plans import MedicalPlan, DentalPlan, VisionPlan
from src.insurance.scenarios import Scenario


# =============================================================================
# Plan Fixtures
# =============================================================================

@pytest.fixture
def gold_ppo_plan() -> MedicalPlan:
    """Blue Shield Gold 80 PPO - typical Gold tier plan."""
    return MedicalPlan(
        name="Blue Shield Gold 80 PPO",
        annual_premium=24_000.0,  # $2000/month for couple
        in_network_oop_max=17_400.0,  # Couple OOP max
        deductible=0.0,  # Gold plans often $0 deductible
        expected_minor_oop=400.0,
        oon_emergency_treated_as_in_network=True,
        post_stabilization_oon_covered=False,
        post_stabilization_exposure=30_000.0,
    )


@pytest.fixture
def platinum_ppo_plan() -> MedicalPlan:
    """Blue Shield Platinum 90 PPO - typical Platinum tier plan."""
    return MedicalPlan(
        name="Blue Shield Platinum 90 PPO",
        annual_premium=30_000.0,  # Higher premium than Gold
        in_network_oop_max=8_700.0,  # Lower OOP max (key benefit)
        deductible=0.0,
        expected_minor_oop=300.0,  # Lower copays
        oon_emergency_treated_as_in_network=True,
        post_stabilization_oon_covered=False,
        post_stabilization_exposure=30_000.0,
    )


@pytest.fixture
def kaiser_gold_hmo() -> MedicalPlan:
    """Kaiser Permanente Gold HMO - low cost, closed network."""
    return MedicalPlan(
        name="Kaiser Gold HMO",
        annual_premium=18_000.0,  # Lower premium
        in_network_oop_max=8_700.0,  # Couple OOP max
        deductible=0.0,
        expected_minor_oop=350.0,
        oon_emergency_treated_as_in_network=True,
        post_stabilization_oon_covered=False,
        post_stabilization_exposure=30_000.0,
    )


@pytest.fixture
def basic_dental() -> DentalPlan:
    """Basic dental plan from Covered California."""
    return DentalPlan(
        name="Delta Dental PPO",
        annual_premium=800.0,
        expected_oop=200.0,
    )


@pytest.fixture
def basic_vision() -> VisionPlan:
    """Basic vision plan (VSP or EyeMed)."""
    return VisionPlan(
        name="VSP Vision",
        annual_premium=300.0,
        expected_oop=50.0,
    )


# =============================================================================
# Scenario Fixtures
# =============================================================================

@pytest.fixture
def no_use_scenario() -> Scenario:
    """Healthy year - no healthcare usage."""
    return Scenario(
        name="no_use",
        probability=0.70,
        medical_oop=0.0,
    )


@pytest.fixture
def minor_use_scenario() -> Scenario:
    """Typical year - some doctor visits, prescriptions."""
    return Scenario(
        name="minor_use",
        probability=0.25,
        medical_oop=400.0,  # Will be overridden by plan.expected_minor_oop
    )


@pytest.fixture
def cat_in_network_scenario() -> Scenario:
    """Catastrophic event in-network (surgery, hospitalization)."""
    return Scenario(
        name="cat_in_network",
        probability=0.03,
        medical_oop=17_400.0,  # Will be overridden by plan.in_network_oop_max
    )


@pytest.fixture
def cat_oon_scenario() -> Scenario:
    """Catastrophic event out-of-network (Colorado skiing accident)."""
    return Scenario(
        name="cat_oon_emergency",
        probability=0.02,
        medical_oop=17_400.0,  # Emergency part (in-network-like)
        extra_oon=30_000.0,  # Post-stabilization exposure
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
    """Typical SF couple household income."""
    return 240_000.0


@pytest.fixture
def typical_baseline_spend() -> float:
    """Typical annual baseline spending (rent, food, etc.)."""
    return 120_000.0
