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

    def _calculate_bonus(self, bonus_type: str) -> int:
        """Generic method to calculate bonuses based on the specified type."""
        bonus = 0

        # Map equipment slots to their attributes
        equipment_slots = {
            "weapon": self.weapon,
            "ranged_weapon": self.ranged_weapon,
            "head": self.head,
            "chest": self.chest,
            "boots": self.boots,
            "armor": self.armor,
            "utility": self.utility,
            "ammo": self.ammo,
        }

        # Bonus mapping for quality attributes
        attribute_bonus_map = {
            "Defence": "defense_bonus",
            "Melee DMG": "melee_bonus",
            "Ranged DMG": "range_dmg_bonus",
            "Ranged Dist": "range_dist_bonus",
        }

        # Iterate through equipment and sum up the bonuses
        for item in equipment_slots.values():
            if item and item.equippable:
                bonus += getattr(item.equippable, bonus_type, 0)

                # Add bonuses from quality attributes
                if hasattr(item.equippable, "attributes"):
                    attributes = getattr(item.equippable, "attributes", [])
                    if not isinstance(attributes, list):
                        attributes = []

                    for attribute in attributes:
                        # Match the attribute to its corresponding bonus type
                        mapped_bonus = attribute_bonus_map.get(attribute)

                        if mapped_bonus == bonus_type:
                            # Add an additional fixed value or derived value (e.g., +2 per attribute)
                            bonus += 2  # Adjust this value based on your design
        return bonus

    @property
    def damage_type(self) -> Optional[DamageType]:
        from components.equippable import Weapon

        if self.weapon and isinstance(self.weapon, Weapon):
            return self.weapon.damage_type
        elif self.ranged_weapon and isinstance(self.ranged_weapon, Weapon):
            return self.ranged_weapon.damage_type
        return None

    @property
    def defence_bonus(self) -> int:
        return self._calculate_bonus("defense_bonus")

    @property
    def melee_bonus(self) -> int:
        return self._calculate_bonus("melee_bonus")

    @property
    def range_dmg_bonus(self) -> int:
        return self._calculate_bonus("range_dmg_bonus")

    @property
    def range_dist_bonus(self) -> int:
        return self._calculate_bonus("range_dist_bonus")

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

