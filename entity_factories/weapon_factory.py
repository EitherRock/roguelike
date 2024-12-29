from components import equippable
from entity import Item
from enums.weapon_types import WeaponType
from enums.damage_types import DamageType
from enums.ammo_types import AmmoType


arrow = Item(
    char="|",
    color=(106, 13, 173),
    name="Arrow",
    equippable=equippable.Ammo(
        ammo_type=AmmoType.ARROW,
        damage_type=DamageType.PIERCING
    )
)

rock = Item(
    char="|",
    color=(100, 100, 100),
    name="Rock",
    equippable=equippable.Ammo(
        ammo_type=AmmoType.ROCK,
        damage_type=DamageType.BLUDGEONING
    )
)

dagger = Item(char="/", name="Dagger", equippable=equippable.Dagger())

sword = Item(char="/", name="Sword", equippable=equippable.Sword())

long_sword = Item(
    char="/",
    name="Long Sword",
    equippable=equippable.Sword(melee_dmg=6)
)

club = Item(char="/", name="Club", equippable=equippable.Club())

unarmed = Item(char="/", color=(0, 191, 255), name="Unarmed", equippable=equippable.Unarmed())

bow = Item(
    char="/",
    name="Bow",
    equippable=equippable.Bow(
        ammo_type=AmmoType.ARROW,
        range_dmg_bonus=2,
        range_dist_bonus=2
    )
)

long_bow = Item(
    char="/",
    color=(80, 191, 255),
    name="Long Bow",
    equippable=equippable.Bow(
        ammo_type=AmmoType.ARROW,
        range_dmg_bonus=4,
        range_dist_bonus=4
    )
)

weapon_factory = {
    WeaponType.DAGGER: dagger,
    WeaponType.UNARMED: unarmed,
    WeaponType.SWORD: sword,
    WeaponType.CLUB: club,
    WeaponType.BOW: bow,
}
