"""TDD tests for plan data models.

Tests written BEFORE implementation following TDD principles.
These tests define the expected behavior of MedicalPlan, DentalPlan, VisionPlan.
"""

import pytest
from dataclasses import fields


class TestMedicalPlanDataclass:
    """Test MedicalPlan data model structure and defaults."""

    def test_medical_plan_exists(self):
        """MedicalPlan dataclass should exist."""
        from src.insurance.plans import MedicalPlan
        assert MedicalPlan is not None

    def test_medical_plan_is_dataclass(self):
        """MedicalPlan should be a dataclass."""
        from src.insurance.plans import MedicalPlan
        assert hasattr(MedicalPlan, "__dataclass_fields__")

    def test_medical_plan_required_fields(self, gold_ppo_plan):
        """MedicalPlan should have all required fields."""
        required = {"name", "annual_premium", "in_network_oop_max"}
        actual = {f.name for f in fields(gold_ppo_plan)}
        assert required.issubset(actual), f"Missing fields: {required - actual}"

    def test_medical_plan_has_deductible(self, gold_ppo_plan):
        """MedicalPlan should track deductible."""
        assert hasattr(gold_ppo_plan, "deductible")
        assert gold_ppo_plan.deductible >= 0

    def test_medical_plan_has_expected_minor_oop(self, gold_ppo_plan):
        """MedicalPlan should estimate minor usage OOP."""
        assert hasattr(gold_ppo_plan, "expected_minor_oop")
        assert gold_ppo_plan.expected_minor_oop > 0

    def test_medical_plan_oon_emergency_flag(self, gold_ppo_plan):
        """MedicalPlan should track if OON emergency uses in-network rates."""
        assert hasattr(gold_ppo_plan, "oon_emergency_treated_as_in_network")
        # Default should be True per No Surprises Act
        assert gold_ppo_plan.oon_emergency_treated_as_in_network is True

    def test_medical_plan_post_stabilization(self, gold_ppo_plan):
        """MedicalPlan should track post-stabilization coverage."""
        assert hasattr(gold_ppo_plan, "post_stabilization_oon_covered")
        assert hasattr(gold_ppo_plan, "post_stabilization_exposure")


class TestMedicalPlanValues:
    """Test MedicalPlan with realistic values."""

    def test_gold_plan_premium_reasonable(self, gold_ppo_plan):
        """Gold plan premium should be in reasonable range."""
        # $1000-3000/month for couple = $12k-36k annual
        assert 12_000 <= gold_ppo_plan.annual_premium <= 36_000

    def test_platinum_higher_premium_than_gold(self, gold_ppo_plan, platinum_ppo_plan):
        """Platinum should have higher premium than Gold."""
        assert platinum_ppo_plan.annual_premium > gold_ppo_plan.annual_premium

    def test_platinum_lower_oop_max_than_gold(self, gold_ppo_plan, platinum_ppo_plan):
        """Platinum should have lower OOP max than Gold (key benefit)."""
        assert platinum_ppo_plan.in_network_oop_max < gold_ppo_plan.in_network_oop_max

    def test_kaiser_lowest_premium(self, gold_ppo_plan, kaiser_gold_hmo):
        """Kaiser HMO should have lower premium than PPO."""
        assert kaiser_gold_hmo.annual_premium < gold_ppo_plan.annual_premium


class TestDentalPlanDataclass:
    """Test DentalPlan data model."""

    def test_dental_plan_exists(self):
        """DentalPlan dataclass should exist."""
        from src.insurance.plans import DentalPlan
        assert DentalPlan is not None

    def test_dental_plan_is_dataclass(self):
        """DentalPlan should be a dataclass."""
        from src.insurance.plans import DentalPlan
        assert hasattr(DentalPlan, "__dataclass_fields__")

    def test_dental_plan_fields(self, basic_dental):
        """DentalPlan should have name, premium, and expected_oop."""
        assert hasattr(basic_dental, "name")
        assert hasattr(basic_dental, "annual_premium")
        assert hasattr(basic_dental, "expected_oop")

    def test_dental_premium_reasonable(self, basic_dental):
        """Dental premium should be reasonable ($30-100/month)."""
        # $360-1200 annual
        assert 300 <= basic_dental.annual_premium <= 1500


class TestVisionPlanDataclass:
    """Test VisionPlan data model."""

    def test_vision_plan_exists(self):
        """VisionPlan dataclass should exist."""
        from src.insurance.plans import VisionPlan
        assert VisionPlan is not None

    def test_vision_plan_is_dataclass(self):
        """VisionPlan should be a dataclass."""
        from src.insurance.plans import VisionPlan
        assert hasattr(VisionPlan, "__dataclass_fields__")

    def test_vision_plan_fields(self, basic_vision):
        """VisionPlan should have name, premium, and expected_oop."""
        assert hasattr(basic_vision, "name")
        assert hasattr(basic_vision, "annual_premium")
        assert hasattr(basic_vision, "expected_oop")

    def test_vision_premium_reasonable(self, basic_vision):
        """Vision premium should be low ($10-40/month)."""
        # $120-480 annual
        assert 100 <= basic_vision.annual_premium <= 600


class TestPlanTotalCost:
    """Test plan cost calculation helpers."""

    def test_total_premium_calculation(self, gold_ppo_plan, basic_dental, basic_vision):
        """Should be able to sum total premium across all plans."""
        from src.insurance.plans import total_annual_premium
        
        total = total_annual_premium(gold_ppo_plan, basic_dental, basic_vision)
        expected = gold_ppo_plan.annual_premium + basic_dental.annual_premium + basic_vision.annual_premium
        
        assert total == expected

    def test_total_premium_without_dental(self, gold_ppo_plan, basic_vision):
        """Total premium should work without dental."""
        from src.insurance.plans import total_annual_premium
        
        total = total_annual_premium(gold_ppo_plan, None, basic_vision)
        expected = gold_ppo_plan.annual_premium + basic_vision.annual_premium
        
        assert total == expected

    def test_total_premium_medical_only(self, gold_ppo_plan):
        """Total premium should work with medical only."""
        from src.insurance.plans import total_annual_premium
        
        total = total_annual_premium(gold_ppo_plan, None, None)
        
        assert total == gold_ppo_plan.annual_premium
