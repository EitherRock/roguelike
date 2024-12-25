import random
from typing import Dict, List, Tuple

import colors


class Quality:
    def __init__(self, name, color, max_attributes, has_magical_ability=False):
        self.name = name
        self.color = color
        self.max_attributes = max_attributes
        self.has_magical_ability = has_magical_ability

    def generate_attributes(self):
        """Randomly generate attributes based on the maximum allowed."""
        all_attributes = [
            # "Health",
            "Defence",
            # "Hit Chance",
            # "Dodge Chance",
            # "Critical DMG",
            # "Critical Hit Chance",
            # "Move Cooldown",
            "Melee DMG",
            "Ranged DMG",
            "Ranged Dist"
        ]
        return random.sample(all_attributes, k=self.max_attributes)

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
        super().__init__(name="Uncommon", color=colors.uncommon, max_attributes=2)


class Rare(Quality):
    def __init__(self):
        super().__init__(name="Rare", color=colors.rare, max_attributes=1, has_magical_ability=True)


class Legendary(Quality):
    def __init__(self):
        super().__init__(name="Legendary", color=colors.legendary, max_attributes=2, has_magical_ability=True)


quality_chances: Dict[int, List[Tuple[Quality, int]]] = {
    # 0: [(Common(), 100), (Uncommon(), 50), (Rare(), 20), (Legendary(), 5)],
    0: [(Common(), 100), (Uncommon(), 1000), (Rare(), 100), (Legendary(), 100)],
    1: [(Common(), 80), (Uncommon(), 60), (Rare(), 30), (Legendary(), 10)],
    2: [(Common(), 60), (Uncommon(), 70), (Rare(), 40), (Legendary(), 15)],
    3: [(Common(), 40), (Uncommon(), 80), (Rare(), 50), (Legendary(), 20)],
}


def get_random_quality(floor: int) -> Quality:
    # Find the highest floor in `quality_chances` that's less than or equal to `floor`
    valid_floor = max(key for key in quality_chances.keys() if key <= floor)
    quality_list = quality_chances[valid_floor]
    qualities, weights = zip(*quality_list)  # Separate qualities and weights
    return random.choices(qualities, weights=weights, k=1)[0]
