
from dataclasses import dataclass
@dataclass
class RuleResult:
    rule_name: str
    passed: bool
    reason: str = ""
    warning: str = ""
