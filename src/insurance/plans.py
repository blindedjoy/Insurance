"""Health insurance plan data models.

Data classes for representing medical, dental, and vision insurance plans
with their cost-sharing structures.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class MedicalPlan:
    """Medical insurance plan with cost-sharing details.
    
    Represents a health insurance plan from Covered California or similar
    marketplace. Tracks both premium costs and out-of-pocket exposure.
    
    Attributes:
        name: Plan name (e.g., "Blue Shield Gold 80 PPO")
        annual_premium: Total annual premium (after subsidies if any)
        in_network_oop_max: Maximum out-of-pocket for in-network care
        deductible: Annual deductible before insurance pays
        expected_minor_oop: Estimated OOP for "normal year" usage
        oon_emergency_treated_as_in_network: Emergency OON uses in-network cost-sharing
            (True by default per No Surprises Act protections)
        post_stabilization_oon_covered: Coverage for post-emergency OON care
            (False by default for exchange plans - conservative assumption)
        post_stabilization_exposure: Extra OOP risk if not covered
    
    Example:
        >>> gold_ppo = MedicalPlan(
        ...     name="Blue Shield Gold 80 PPO",
        ...     annual_premium=24_000.0,
        ...     in_network_oop_max=17_400.0,
        ...     deductible=0.0,
        ... )
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
    """Dental insurance add-on.
    
    Covered California offers family dental plans through vendors
    like Delta Dental.
    
    Attributes:
        name: Plan name (e.g., "Delta Dental PPO")
        annual_premium: Annual premium cost
        expected_oop: Average annual out-of-pocket dental costs
    
    Example:
        >>> dental = DentalPlan(
        ...     name="Delta Dental PPO",
        ...     annual_premium=800.0,
        ...     expected_oop=200.0,
        ... )
    """
    
    name: str
    annual_premium: float
    expected_oop: float = 200.0


@dataclass
class VisionPlan:
    """Vision insurance add-on.
    
    Covered California offers adult vision through EyeMed and VSP.
    
    Attributes:
        name: Plan name (e.g., "VSP Vision")
        annual_premium: Annual premium cost
        expected_oop: Average annual out-of-pocket vision costs
    
    Example:
        >>> vision = VisionPlan(
        ...     name="VSP Vision",
        ...     annual_premium=300.0,
        ...     expected_oop=50.0,
        ... )
    """
    
    name: str
    annual_premium: float
    expected_oop: float = 50.0


def total_annual_premium(
    medical: MedicalPlan,
    dental: Optional[DentalPlan] = None,
    vision: Optional[VisionPlan] = None,
) -> float:
    """Calculate total annual premium across all plans.
    
    Args:
        medical: Required medical plan
        dental: Optional dental add-on
        vision: Optional vision add-on
        
    Returns:
        Total annual premium in dollars
        
    Example:
        >>> total = total_annual_premium(gold_ppo, dental, vision)
        >>> print(f"Total: ${total:,.0f}")
    """
    total = medical.annual_premium
    
    if dental is not None:
        total += dental.annual_premium
    
    if vision is not None:
        total += vision.annual_premium
    
    return total
