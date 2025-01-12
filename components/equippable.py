from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from components.base_component import BaseComponent
from enums.equipments_types import EquipmentType
from enums.weapon_types import WeaponType
from enums.weapon_distances import WeaponDistanceType
from enums.damage_types import DamageType
from enums.ammo_types import AmmoType
from components.quality import Quality, Common, Uncommon, Rare, Legendary
import random

if TYPE_CHECKING:
    from entity import Item


class Equippable(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        melee_bonus: int = 0,
        range_dmg_bonus: int = 0,
        range_dist_bonus: int = 0,
        defense_bonus: int = 0,
        fov_bonus: int = 0,
        quality: Optional[Quality] = None
    ):
        self.equipment_type = equipment_type

        self.melee_bonus = melee_bonus
        self.range_dmg_bonus = range_dmg_bonus
        self.range_dist_bonus = range_dist_bonus
        self.defense_bonus = defense_bonus

        self.fov_bonus = fov_bonus

        self._quality = quality
        self.attributes = quality.generate_attributes() if quality else []
        self.magic_ability = quality.generate_magical_ability() if quality else None

    @property
    def quality(self) -> Optional[Quality]:
        return self._quality

    @quality.setter
    def quality(self, new_quality: Quality) -> None:
        self._quality = new_quality

        # Update attributes and magical abilities based on the new quality
        if new_quality:
            self.attributes = new_quality.generate_attributes()
            self.magic_ability = new_quality.generate_magical_ability()
        else:
            # Reset attributes if no quality is provided
            self.attributes = []
            self.magic_ability = None


class Weapon(Equippable):
    def __init__(
        self,
        weapon_range: WeaponDistanceType,
        weapon_type: WeaponType,
        quality: Optional[Quality] = None,
        damage_type: Optional[DamageType] = None,
        melee_bonus: int = 0,
        range_dmg_bonus: int = 0,
        range_dist_bonus: int = 0,
        defense_bonus: int = 0,
        fov_bonus: int = 0,
    ) -> None:
        """
        A base class for all weapons. Includes attributes specific to weapons.
        :param melee_bonus: The bonus power provided by the weapon.
        :param defense_bonus: The bonus defense provided by the weapon.
        :param fov_bonus: The bonus field-of-view provided by the weapon.
        :param weapon_range: The attack range of the weapon.
        :param weapon_type: The type of weapon (e.g., Melee, Ranged).
        """
        super().__init__(
            equipment_type=EquipmentType.WEAPON,
            melee_bonus=melee_bonus,
            defense_bonus=defense_bonus,
            fov_bonus=fov_bonus,
            quality=quality
        )
        self.weapon_range = weapon_range
        self.weapon_type = weapon_type
        self.damage_type = damage_type
        self.range_dmg_bonus = range_dmg_bonus
        self.range_dist_bonus = range_dist_bonus


class Unarmed(Weapon):
    def __init__(
            self
    ) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.MELEE,
            weapon_type=WeaponType.UNARMED,
            damage_type=DamageType.BLUDGEONING,
        )


class UnarmedRanged(Weapon):
    def __init__(
            self
    ) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.RANGED,
            weapon_type=WeaponType.UNARMED,
            damage_type=DamageType.BLUDGEONING
        )


class Bow(Weapon):
    def __init__(
            self,
            range_dmg_bonus: int,
            range_dist_bonus: int,
            quality: Quality = None,
            ammo_type: AmmoType = AmmoType.ARROW,
    ) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.RANGED,
            weapon_type=WeaponType.BOW,
            damage_type=DamageType.PIERCING,
            range_dmg_bonus=range_dmg_bonus,
            range_dist_bonus=range_dist_bonus,
            quality=quality
        )
        self.ammo_type = ammo_type


class Dagger(Weapon):
    def __init__(
            self,
            quality: Quality = None,
            melee_dmg: int = 2
    ) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.MELEE,
            weapon_type=WeaponType.DAGGER,
            damage_type=DamageType.SLASHING,
            melee_bonus=melee_dmg,
            quality=quality
        )


class Sword(Weapon):
    def __init__(self, quality: Quality = None, melee_dmg: int = 4) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.MELEE,
            weapon_type=WeaponType.SWORD,
            damage_type=DamageType.SLASHING,
            melee_bonus=melee_dmg,
            quality=quality
        )


class Club(Weapon):
    def __init__(self, quality: Quality = None, melee_dmg: int = 4) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.MELEE,
            weapon_type=WeaponType.CLUB,
            damage_type=DamageType.BLUDGEONING,
            melee_bonus=melee_dmg,
            quality=quality
            )


class Axe(Weapon):
    def __init__(self, quality: Quality = None, melee_dmg: int = 4) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.MELEE,
            weapon_type=WeaponType.CLUB,
            damage_type=DamageType.CLEAVE,
            melee_bonus=melee_dmg,
            quality=quality
        )


class LeatherArmor(Equippable):
    def __init__(self, quality: Quality = None) -> None:
        super().__init__(equipment_type=EquipmentType.CHEST, defense_bonus=1, quality=quality)


class ChainMail(Equippable):
    def __init__(self, quality: Quality = None) -> None:
        super().__init__(equipment_type=EquipmentType.CHEST, defense_bonus=3, quality=quality)


class Helmet(Equippable):
    def __init__(self, quality: Quality = None) -> None:
        super().__init__(equipment_type=EquipmentType.HEAD, defense_bonus=1, quality=quality)


class Boots(Equippable):
    def __init__(self, quality: Quality = None) -> None:
        super().__init__(equipment_type=EquipmentType.BOOTS, defense_bonus=1, quality=quality)


class LightSource(Equippable):
    def __init__(self, fov_bonus: int) -> None:
        super().__init__(equipment_type=EquipmentType.UTILITY, fov_bonus=fov_bonus)


class Ammo(Equippable):
    def __init__(
            self,
            damage_type: DamageType,
            ammo_type: AmmoType,
    ):
        super().__init__(equipment_type=EquipmentType.AMMO, range_dmg_bonus=1)
        self.quantity: int = 0
        self.damage_type = damage_type
        self.ammo_type = ammo_type

    def use(self) -> None:
        import components.inventory
        """Reduce the quantity of the ammo by 1. Removes the item if quantity is 0."""
        if self.quantity > 0:
            self.quantity -= 1
            if self.quantity == 0:
                """Remove the consumed item from its containing inventory."""
                entity = self.parent
                inventory = entity.parent
                player = inventory.parent
                player.equipment.toggle_equip(entity, add_message=False)

                if isinstance(inventory, components.inventory.Inventory):
                    inventory.items.remove(entity)

    def random_quantity(self) -> int:
        return random.randint(1, 10)
