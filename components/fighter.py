from __future__ import annotations
import random
import time
from typing import TYPE_CHECKING, Optional, List
import colors
from entity_factories import monster_factory
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
            field_of_view: Optional[int] = None,
            flying: bool = False,
            critical_chance: float = 0.1,
            critical_multiplier: float = 1.5
    ):
        self.base_max_hp = hp
        self._hp = hp
        self.base_defense = base_defense
        self.base_power = base_power
        self.base_fov = field_of_view
        self.base_attack_range = base_attack_range
        self.flying = flying
        self.resistances = resistances or []
        self.immunities = immunities or []
        self._allowed_weapon_types = allowed_weapon_types or []
        self.base_critical_chance = critical_chance
        self.base_critical_multiplier = critical_multiplier

    @property
    def allowed_weapon_types(self) -> List[WeaponType]:
        # Always include UNARMED in the list
        if WeaponType.UNARMED not in self._allowed_weapon_types:
            self._allowed_weapon_types.append(WeaponType.UNARMED)
        return self._allowed_weapon_types

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def max_hp(self) -> int:
        return self.base_max_hp + self.health_bonus

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
    def critical_chance(self) -> float:
        return self.base_critical_chance + self.critical_chance_bonus

    @property
    def critical_multiplier(self) -> float:
        return self.base_critical_multiplier + self.critical_multiplier_bonus

    @property
    def defense_bonus(self) -> int:
        bonus = 0
        if self.parent.equipment:
            bonus += self.parent.equipment.defence_bonus
        return bonus

    @property
    def critical_chance_bonus(self) -> float:
        bonus = 0
        if self.parent.equipment:
            bonus += self.parent.equipment.critical_chance_bonus
        return bonus

    @property
    def critical_multiplier_bonus(self) -> float:
        bonus = 0
        if self.parent.equipment:
            bonus += self.parent.equipment.critical_multiplier_bonus
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

    @property
    def health_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.health_bonus
        else:
            return 0

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = colors.player_die
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_color = colors.enemy_die

            for item in self.parent.inventory.items:
                if item.name == "Key":
                    self.parent.inventory.drop(item)

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
        if self.hp <= 0:
            return  # Prevent processing if already dead.

        if self is self.engine.player:
            attack_color = colors.player_atk
        else:
            attack_color = colors.enemy_atk

        # Didja get a crit?
        crit = random.random() < self.critical_chance

        if damage_type in self.resistances:
            amount = amount // 2

            if crit:
                self.engine.message_log.add_message("CRIT!", attack_color)
                amount *= self.critical_multiplier

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
            if crit:
                self.engine.message_log.add_message("CRIT!", attack_color)
                amount *= self.critical_multiplier

            self.hp -= max(0, int(amount))
            self.engine.message_log.add_message(
                f"{desc} for {amount} hit points.", attack_color
            )

        self.parent.hit_timer = .1
        self.parent.last_hit_time = self.engine.elapsed_time
        self.parent.color = colors.hit


class Slime(Fighter):

    def die(self) -> None:
        small_slime = monster_factory.small_slime
        valid_locations = self.find_valid_spawn_locations()

        for i, (x, y) in enumerate(valid_locations):
            if i >= 4:  # Spawn at most 4 slimes
                break
            small_slime.spawn(self.engine.game_map, x, y)

        death_message = f"{self.parent.name} is dead!"
        death_message_color = colors.enemy_die

        for item in self.parent.inventory.items:
            if item.name == "Key":
                self.parent.inventory.drop(item)

        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)

        self.engine.player.level.add_xp(self.parent.level.xp_given)

    def find_valid_spawn_locations(self, radius: int = 2) -> list[tuple[int, int]]:
        """Find valid spawn locations within a radius around the dying slime."""
        slime_x, slime_y = self.parent.x, self.parent.y
        game_map = self.engine.game_map

        valid_locations = []

        # Check all tiles within the given radius
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x, y = slime_x + dx, slime_y + dy

                # Skip the slime's own position
                if dx == 0 and dy == 0:
                    continue

                # Check if the tile is within bounds
                if not game_map.in_bounds(x, y):
                    continue

                # Check if the tile is walkable
                if not game_map.tiles[x, y]["walkable"]:
                    continue

                # Check if the tile has an entity
                if any(entity.x == x and entity.y == y for entity in game_map.entities):
                    continue

                # If all checks pass, this is a valid location
                valid_locations.append((x, y))

        return valid_locations


