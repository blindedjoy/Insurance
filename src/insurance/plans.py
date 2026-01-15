"""Health insurance plan data models.

Data classes for representing medical, dental, and vision insurance plans
with their cost-sharing structures.

Research findings (2026-01-15):
- Emergency OON: Protected at in-network rates (No Surprises Act)
- Air ambulance: Protected by federal law
- Ground ambulance: NOT protected ($500-$2,000 exposure)
- Post-stabilization: Covered until consent waiver signed
- PPO OON: $5,500 deductible, 50% coinsurance, $25k OOP max
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class NetworkType(Enum):
    """Health plan network type.
    
    Determines out-of-network coverage rules:
    - HMO: Referrals required, OON emergency only
    - PPO: No referrals, some OON coverage (limited on exchange)
    - EPO: No referrals, NO OON coverage (except emergency)
    
    Research finding: All types have equal emergency OON protection
    per No Surprises Act. Difference is post-stabilization.
    """
    HMO = "hmo"
    PPO = "ppo"
    EPO = "epo"


@dataclass
class MedicalPlan:
    """Medical insurance plan with cost-sharing details.
    
    Represents a health insurance plan from Covered California or similar
    marketplace. Tracks both premium costs and out-of-pocket exposure.
    
    Attributes:
        name: Plan name (e.g., "Blue Shield Gold 80 PPO")
        annual_premium: Total annual premium (after subsidies if any)
        in_network_oop_max: Maximum out-of-pocket for in-network care
        network_type: HMO, PPO, or EPO (affects OON coverage)
        deductible: Annual deductible before insurance pays
        expected_minor_oop: Estimated OOP for "normal year" usage
        oon_emergency_treated_as_in_network: Emergency OON uses in-network cost-sharing
            (True by default per No Surprises Act protections)
        post_stabilization_oon_covered: Coverage for post-emergency OON care
            (False by default for exchange plans - conservative assumption)
        post_stabilization_exposure: Extra OOP risk if not covered
        oon_deductible: PPO out-of-network deductible ($5,500 typical)
        oon_oop_max: PPO out-of-network OOP max ($25,000 typical)
        oon_coinsurance: PPO OON coinsurance (0.50 = you pay 50%)
        ground_ambulance_exposure: Not protected by federal law ($500-$2,000)
    
    Example:
        >>> gold_ppo = MedicalPlan(
        ...     name="Blue Shield Gold 80 PPO",
        ...     annual_premium=24_000.0,
        ...     in_network_oop_max=17_400.0,
        ...     network_type=NetworkType.PPO,
        ... )
    """
    
    name: str
    annual_premium: float
    in_network_oop_max: float
    network_type: NetworkType = NetworkType.PPO  # Default for backwards compatibility
    deductible: float = 0.0
    expected_minor_oop: float = 400.0
    oon_emergency_treated_as_in_network: bool = True  # No Surprises Act
    post_stabilization_oon_covered: bool = False  # Conservative for exchange plans
    post_stabilization_exposure: float = 30_000.0  # Tail risk estimate
    # PPO OON fields (research: Blue Shield PPO on Covered California)
    oon_deductible: float = 5_500.0  # PPO OON deductible
    oon_oop_max: float = 25_000.0  # PPO OON cap (individual)
    oon_coinsurance: float = 0.50  # You pay 50% after deductible
    # Ground ambulance (research: NOT protected by federal law)
    ground_ambulance_exposure: float = 1_500.0  # Midpoint of $500-$2,000


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
