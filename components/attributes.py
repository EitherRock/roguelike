

class Attribute:
    """Base class for an attribute."""
    def __init__(self, quality_multiplier: float):
        self.quality_multiplier = quality_multiplier

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def base_value(self) -> int:
        raise NotImplementedError

    @property
    def value(self) -> int | float:
        calculated_value = self.base_value * self.quality_multiplier
        return int(calculated_value) if calculated_value.is_integer() else calculated_value

    def __repr__(self):
        return f"{self.name}: {self.value}"


class HealthAttribute(Attribute):
    @property
    def name(self) -> str:
        return "health_bonus"

    @property
    def base_value(self) -> int:
        return 10  # Base value for Health


class DefenceAttribute(Attribute):
    @property
    def name(self) -> str:
        return "defense_bonus"

    @property
    def base_value(self) -> int:
        return 5  # Base value for Defence


class CriticalDMGAttribute(Attribute):
    @property
    def name(self) -> str:
        return "critical_multiplier_bonus"

    @property
    def base_value(self) -> float:
        return .25


class CriticalChanceAttribute(Attribute):
    @property
    def name(self) -> str:
        return "critical_chance_bonus"

    @property
    def base_value(self) -> float:
        return .05


class MeleeDMGAttribute(Attribute):
    @property
    def name(self) -> str:
        return "melee_bonus"

    @property
    def base_value(self) -> int:
        return 2


class RangeDMGAttribute(Attribute):
    @property
    def name(self) -> str:
        return "range_dmg_bonus"

    @property
    def base_value(self) -> int:
        return 2


class RangeDISTAttribute(Attribute):
    @property
    def name(self) -> str:
        return "range_dist_bonus"

    @property
    def base_value(self) -> int:
        return 1


class HitChanceAttribute(Attribute):
    pass


class DodgeChanceAttribute(Attribute):
    pass


class MoveCooldownAttribute(Attribute):
    pass
