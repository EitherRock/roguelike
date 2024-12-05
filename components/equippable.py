from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from components.base_component import BaseComponent
from enums.equipments_types import EquipmentType
from enums.weapon_types import WeaponType
from enums.weapon_distances import WeaponDistanceType
from enums.damage_types import DamageType

if TYPE_CHECKING:
    from entity import Item


class Equippable(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        melee_bonus: int = 0,
        range_bonus: int = 0,
        defense_bonus: int = 0,
        fov_bonus: int = 0
    ):
        self.equipment_type = equipment_type

        self.melee_bonus = melee_bonus
        self.range_bonus = range_bonus
        self.defense_bonus = defense_bonus

        self.fov_bonus = fov_bonus


class Weapon(Equippable):
    def __init__(
        self,
        weapon_range: WeaponDistanceType,
        weapon_type: WeaponType,
        damage_type: Optional[DamageType] = None,
        melee_bonus: int = 0,
        range_bonus: int = 0,
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
        )
        self.weapon_range = weapon_range
        self.weapon_type = weapon_type
        self.damage_type = damage_type
        self.range_bonus = range_bonus


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
            self
    ) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.RANGED,
            weapon_type=WeaponType.BOW,
            damage_type=DamageType.BLUDGEONING,
            range_bonus=2
        )


class Dagger(Weapon):
    def __init__(
            self
    ) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.MELEE,
            weapon_type=WeaponType.DAGGER,
            damage_type=DamageType.SLASHING,
            melee_bonus=2
        )


class Sword(Weapon):
    def __init__(self) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.MELEE,
            weapon_type=WeaponType.SWORD,
            damage_type=DamageType.SLASHING,
            melee_bonus=4
        )


class Club(Weapon):
    def __init__(self) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.MELEE,
            weapon_type=WeaponType.CLUB,
            damage_type=DamageType.BLUDGEONING,
            melee_bonus=4
            )


class LeatherArmor(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=1)


class ChainMail(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=3)


class Lantern(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.UTILITY, fov_bonus=5)
