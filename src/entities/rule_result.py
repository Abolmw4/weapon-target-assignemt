
from dataclasses import dataclass

class RuleResult:
    rule_name: str
    passed: bool
    reason: str = ""
    warning: str = ""
