from __future__ import annotations
from typing import TYPE_CHECKING
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
        power_bonus: int = 0,
        defense_bonus: int = 0,
        fov_bonus: int = 0
    ):
        self.equipment_type = equipment_type

        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus

        self.fov_bonus = fov_bonus


class Weapon(Equippable):
    def __init__(
        self,
        weapon_range: WeaponDistanceType,
        weapon_type: WeaponType,
        damage_type: DamageType,
        power_bonus: int = 0,
        defense_bonus: int = 0,
        fov_bonus: int = 0
    ) -> None:
        """
        A base class for all weapons. Includes attributes specific to weapons.
        :param power_bonus: The bonus power provided by the weapon.
        :param defense_bonus: The bonus defense provided by the weapon.
        :param fov_bonus: The bonus field-of-view provided by the weapon.
        :param weapon_range: The attack range of the weapon.
        :param weapon_type: The type of weapon (e.g., Melee, Ranged).
        """
        super().__init__(
            equipment_type=EquipmentType.WEAPON,
            power_bonus=power_bonus,
            defense_bonus=defense_bonus,
            fov_bonus=fov_bonus,
        )
        self.weapon_range = weapon_range
        self.weapon_type = weapon_type
        self.damage_type = damage_type


class Unarmed(Weapon):
    def __init__(
            self
    ) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.MELEE,
            weapon_type=WeaponType.UNARMED,
            damage_type=DamageType.BLUDGEONING,
            power_bonus=0
        )


class Dagger(Weapon):
    def __init__(
            self
    ) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.MELEE,
            weapon_type=WeaponType.DAGGER,
            damage_type=DamageType.SLASHING,
            power_bonus=2
        )


class Sword(Weapon):
    def __init__(self) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.MELEE,
            weapon_type=WeaponType.SWORD,
            damage_type=DamageType.SLASHING,
            power_bonus=4
        )


class Club(Weapon):
    def __init__(self) -> None:
        super().__init__(
            weapon_range=WeaponDistanceType.MELEE,
            weapon_type=WeaponType.CLUB,
            damage_type=DamageType.BLUDGEONING,
            power_bonus=4
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
