from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
import colors
from components.base_component import BaseComponent
from enums.damage_types import DamageType
from enums.weapon_types import WeaponType
from enums.render_order import RenderOrder

if TYPE_CHECKING:
    from entity import Actor


class Fighter(BaseComponent):
    parent: Actor

    def __init__(
            self,
            hp: int,
            base_defense: int,
            base_power: int,
            base_attack_range: int = 3,
            resistances: Optional[List[DamageType]] = None,
            immunities: Optional[List[DamageType]] = None,
            allowed_weapon_types: Optional[List[WeaponType]] = None,
            field_of_view: Optional[int] = None
    ):
        self.max_hp = hp
        self._hp = hp
        self.base_defense = base_defense
        self.base_power = base_power
        self.base_fov = field_of_view
        self.base_attack_range = base_attack_range
        self.resistances = resistances or []
        self.immunities = immunities or []
        self._allowed_weapon_types = allowed_weapon_types or []

    @property
    def allowed_weapon_types(self) -> List[WeaponType]:
        # Always include UNARMED in the list
        if WeaponType.UNARMED not in self._allowed_weapon_types:
            self._allowed_weapon_types.append(WeaponType.UNARMED)
        return self._allowed_weapon_types

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    @property
    def defense(self) -> int:
        return self.base_defense + self.defense_bonus

    @property
    def melee_power(self) -> int:
        return self.base_power + self.melee_bonus

    @property
    def range_power(self) -> int:
        return self.base_power + self.range_dmg_bonus

    @property
    def fov(self) -> int:
        return self.base_fov + self.fov_bonus

    @property
    def ranged_attack_range(self) -> int:
        return self.base_attack_range + self.rang_dist_bonus

    @property
    def defense_bonus(self) -> int:
        bonus = 0
        if self.parent.equipment:
            bonus += self.parent.equipment.defence_bonus
        return bonus

    @property
    def melee_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.melee_bonus
        else:
            return 0

    @property
    def range_dmg_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.range_dmg_bonus
        else:
            return 0

    @property
    def rang_dist_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.range_dist_bonus
        else:
            return 0

    @property
    def fov_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.fov_bonus
        else:
            return 0

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = colors.player_die
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_color = colors.enemy_die
        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)

        self.engine.player.level.add_xp(self.parent.level.xp_given)

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def take_damage(self, amount: int, damage_type: DamageType, desc: str) -> None:
        if self is self.engine.player:
            attack_color = colors.player_atk
        else:
            attack_color = colors.enemy_atk

        if damage_type in self.resistances:
            amount = amount // 2
            self.hp -= max(0, int(amount))
            self.engine.message_log.add_message(
                f"{desc} but {self.parent.name} is RESISTANT to {damage_type.name} and only takes {amount} damage.",
                attack_color
            )
        elif damage_type in self.immunities:
            if self != self.engine.player:
                self.engine.message_log.add_message(
                    f"{desc} but {self.parent.name} is IMMUNE to {damage_type.name} damage!",
                    attack_color
                )
        else:
            self.hp -= max(0, int(amount))
            self.engine.message_log.add_message(
                f"{desc} for {amount} hit points.", attack_color
            )


