from src.entities.weapon import Weapon
from src.entities.target import Target
from src.rules.base_rule import BaseRule
from src.entities.rule_result import RuleResult

class ChannelRule(BaseRule):
    def __init__(self):
        super().__init__()
        pass
    
    def check(self, weapon: Weapon, target: Target) -> RuleResult:
        if weapon.used_channels < weapon.engagement_channels:
            return RuleResult(rule_name="ChannelRule", passed=True)
        
        return RuleResult(rule_name="ChannelRule", passed=False, reason="engagment channel not stasfied\n"
                                                                         f"eapon engagment channel: {weapon.engagement_channels} "
                                                                         f"channel is used: {weapon.used_channels}")
