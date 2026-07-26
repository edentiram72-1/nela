"""Defensive security specialist agents."""

from agents.security.anomaly_discovery import AnomalyDiscoveryAgent
from agents.security.authorized_lab import AuthorizedLabAgent
from agents.security.cyber_defense import CyberDefenseAgent
from agents.security.defensive_specialists import IdentityAccessAgent, NetworkDefenseAgent, SecretsHygieneAgent, SupplyChainSecurityAgent
from agents.security.secure_code_reviewer import SecureCodeReviewerAgent
from agents.security.vulnerability_research import VulnerabilityResearchAgent

__all__ = [
    "AnomalyDiscoveryAgent",
    "AuthorizedLabAgent",
    "CyberDefenseAgent",
    "IdentityAccessAgent",
    "NetworkDefenseAgent",
    "SecureCodeReviewerAgent",
    "SecretsHygieneAgent",
    "SupplyChainSecurityAgent",
    "VulnerabilityResearchAgent",
]
