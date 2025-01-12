import random
from typing import Dict, List, Tuple

import colors
from components import attributes


class Quality:
    def __init__(self, name, color, max_attributes, multiplier=1.0, has_magical_ability=False):
        self.name = name
        self.color = color
        self.max_attributes = max_attributes
        self.multiplier = multiplier
        self.has_magical_ability = has_magical_ability

    def generate_attributes(self):
        """Generate attributes using the quality multiplier."""
        attribute_classes = [
            attributes.HealthAttribute,
            attributes.DefenceAttribute,
            attributes.CriticalDMGAttribute,
            attributes.MeleeDMGAttribute,
            attributes.CriticalChanceAttribute,
            attributes.RangeDMGAttribute,
            attributes.RangeDISTAttribute,

        ]
        selected_classes = random.sample(attribute_classes, k=self.max_attributes)
        return [attr_class(self.multiplier) for attr_class in selected_classes]

    def generate_magical_ability(self):
        """Randomly assign a magical ability if applicable."""
        if self.has_magical_ability:
            magical_abilities = ["Fire", "Lifesteal", "Lightning", "Poison"]
            return random.choice(magical_abilities)
        return None

    def __str__(self):
        return self.name


class Common(Quality):
    def __init__(self):
        super().__init__(name="Common", color=colors.common, max_attributes=1)


class Uncommon(Quality):
    def __init__(self):
        super().__init__(name="Uncommon", color=colors.uncommon, multiplier=1.5, max_attributes=2)


class Rare(Quality):
    def __init__(self):
        super().__init__(name="Rare", color=colors.rare, max_attributes=1, multiplier=2.0, has_magical_ability=True)


class Legendary(Quality):
    def __init__(self):
        super().__init__(
            name="Legendary",
            color=colors.legendary,
            max_attributes=2,
            multiplier=2.5,
            has_magical_ability=True
        )


quality_chances: Dict[int, List[Tuple[Quality, int]]] = {
    0: [(Common(), 100), (Uncommon(), 50), (Rare(), 20), (Legendary(), 5)],
    4: [(Common(), 80), (Uncommon(), 60), (Rare(), 30), (Legendary(), 10)],
    8: [(Common(), 60), (Uncommon(), 70), (Rare(), 40), (Legendary(), 15)],
    12: [(Common(), 40), (Uncommon(), 80), (Rare(), 50), (Legendary(), 20)],
}


def get_random_quality(floor: int) -> Quality:
    # Find the highest floor in `quality_chances` that's less than or equal to `floor`
    valid_floor = max(key for key in quality_chances.keys() if key <= floor)
    quality_list = quality_chances[valid_floor]
    qualities, weights = zip(*quality_list)  # Separate qualities and weights
    return random.choices(qualities, weights=weights, k=1)[0]
