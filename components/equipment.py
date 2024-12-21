from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from components.base_component import BaseComponent
from enums.equipments_types import EquipmentType
from enums.damage_types import DamageType
from util import format_item_name
from components.equippable import Ammo

if TYPE_CHECKING:
    from entity import Actor, Item
    from enums.weapon_distances import WeaponDistanceType


class Equipment(BaseComponent):
    parent: Actor

    def __init__(
            self,
            melee_weapon: Optional[Item] = None,
            ranged_weapon: Optional[Item] = None,
            head: Optional[Item] = None,
            chest: Optional[Item] = None,
            boots: Optional[Item] = None,
            armor: Optional[Item] = None,
            utility: Optional[Item] = None,
            ammo: Optional[Item] = None
    ):
        self.weapon = melee_weapon
        self.ranged_weapon = ranged_weapon
        self.armor = armor
        self.head = head
        self.chest = chest
        self.boots = boots
        self.utility = utility
        self.ammo = ammo

    @property
    def damage_type(self) -> Optional[DamageType]:
        from components.equippable import Weapon
        if self.weapon and isinstance(self.weapon, Weapon):
            return self.weapon.damage_type
        elif self.ranged_weapon and isinstance(self.ranged_weapon, Weapon):
            return self.ranged_weapon.damage_type

    @property
    def defence_bonus(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.defense_bonus
        if self.ranged_weapon is not None and self.ranged_weapon.equippable is not None:
            bonus += self.ranged_weapon.equippable.defense_bonus
        if self.head is not None and self.head.equippable is not None:
            bonus += self.head.equippable.defense_bonus
        if self.chest is not None and self.chest.equippable is not None:
            bonus += self.chest.equippable.defense_bonus
        if self.boots is not None and self.boots.equippable is not None:
            bonus += self.boots.equippable.defense_bonus

        return bonus

    @property
    def melee_bonus(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.melee_bonus
        if self.ranged_weapon is not None and self.ranged_weapon.equippable is not None:
            bonus += self.ranged_weapon.equippable.melee_bonus
        if self.utility is not None and self.utility.equippable is not None:
            bonus += self.utility.equippable.melee_bonus
        if self.head is not None and self.head.equippable is not None:
            bonus += self.head.equippable.melee_bonus
        if self.chest is not None and self.chest.equippable is not None:
            bonus += self.chest.equippable.melee_bonus
        if self.boots is not None and self.boots.equippable is not None:
            bonus += self.boots.equippable.melee_bonus

        return bonus

    @property
    def range_dmg_bonus(self) -> int:
        bonus = 0

        if self.ranged_weapon is not None and self.ranged_weapon.equippable is not None:
            bonus += self.ranged_weapon.equippable.range_dmg_bonus
        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.range_dmg_bonus
        if self.ammo is not None and self.ammo.equippable is not None:
            bonus += self.ammo.equippable.range_dmg_bonus
        if self.head is not None and self.head.equippable is not None:
            bonus += self.head.equippable.range_dmg_bonus
        if self.chest is not None and self.chest.equippable is not None:
            bonus += self.chest.equippable.range_dmg_bonus
        if self.boots is not None and self.boots.equippable is not None:
            bonus += self.boots.equippable.range_dmg_bonus
        if self.utility is not None and self.utility.equippable is not None:
            bonus += self.utility.equippable.range_dmg_bonus

        return bonus

    @property
    def range_dist_bonus(self) -> int:
        bonus = 0

        if self.ranged_weapon is not None and self.ranged_weapon.equippable is not None:
            bonus += self.ranged_weapon.equippable.range_dist_bonus
        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.range_dist_bonus
        if self.ammo is not None and self.ammo.equippable is not None:
            bonus += self.ammo.equippable.range_dist_bonus
        if self.head is not None and self.head.equippable is not None:
            bonus += self.head.equippable.range_dist_bonus
        if self.chest is not None and self.chest.equippable is not None:
            bonus += self.chest.equippable.range_dist_bonus
        if self.boots is not None and self.boots.equippable is not None:
            bonus += self.boots.equippable.range_dist_bonus
        if self.utility is not None and self.utility.equippable is not None:
            bonus += self.utility.equippable.range_dist_bonus

        return bonus

    @property
    def fov_bonus(self) -> int:
        bonus = 0

        if self.utility is not None and self.utility.equippable is not None:
            bonus += self.utility.equippable.fov_bonus

        return bonus

    def item_is_equipped(self, item: Item) -> bool:
        return self.weapon == item \
            or self.head == item \
            or self.chest == item \
            or self.boots == item \
            or self.utility == item \
            or self.ranged_weapon == item \
            or self.ammo == item

    def unequip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You remove the {item_name}."
        )

    def equip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You equip the {item_name}."
        )

    def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if current_item is not None:
            self.unequip_from_slot(slot, add_message)

        setattr(self, slot, item)

        if add_message:
            quantity = 1
            if isinstance(item.equippable, Ammo):
                quantity = item.equippable.quantity
            self.equip_message(format_item_name(item.name, quantity))

    def unequip_from_slot(self, slot: str, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if add_message:
            quantity = 1
            if isinstance(current_item.equippable, Ammo):
                quantity = current_item.equippable.quantity
            self.unequip_message(format_item_name(current_item.name, quantity))

        setattr(self, slot, None)

    def toggle_equip(self, equippable_item: Item, add_message: bool = True) -> None:
        from components.equippable import Weapon
        from enums.weapon_distances import WeaponDistanceType

        # Weapon slots melee and ranged
        if (
            equippable_item.equippable
            and equippable_item.equippable.equipment_type == EquipmentType.WEAPON
        ):
            if isinstance(equippable_item.equippable, Weapon):
                if equippable_item.equippable.weapon_range == WeaponDistanceType.MELEE:
                    slot = "weapon"
                elif equippable_item.equippable.weapon_range == WeaponDistanceType.RANGED:
                    slot = "ranged_weapon"

        # Utility slot
        elif (
            equippable_item.equippable
            and equippable_item.equippable.equipment_type == EquipmentType.UTILITY
        ):
            slot = "utility"

        # Ammo slot
        elif (
                equippable_item.equippable
                and equippable_item.equippable.equipment_type == EquipmentType.AMMO
        ):
            slot = "ammo"

        # Head slot
        elif (
            equippable_item.equippable
            and equippable_item.equippable.equipment_type == EquipmentType.HEAD
        ):
            slot = "head"

        elif (
            equippable_item.equippable
            and equippable_item.equippable.equipment_type == EquipmentType.CHEST
        ):
            slot = "chest"

        elif (
            equippable_item.equippable
            and equippable_item.equippable.equipment_type == EquipmentType.BOOTS
        ):
            slot = "boots"

        if getattr(self, slot) == equippable_item:
            self.unequip_from_slot(slot, add_message)
        else:
            self.equip_to_slot(slot, equippable_item, add_message)

