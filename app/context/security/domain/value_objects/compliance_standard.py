from __future__ import annotations

from enum import Enum


class ComplianceStandard(Enum):
    GDPR = "gdpr"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"
    CCPA = "ccpa"
    PCI_DSS = "pci_dss"
    FEDRAMP = "fedramp"
