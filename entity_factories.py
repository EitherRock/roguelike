from components.ai import HostileEnemy
from components import consumable, equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from enums.spawn_types import SpawnType
from components.level import Level
from entity import Actor, Item
from enums.weapon_types import WeaponType
from enums.damage_types import DamageType
from enums.ammo_types import AmmoType


player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=100, base_defense=1, base_power=2, field_of_view=3),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
    move_cooldown=.3
)

rat = Actor(
    char="r",
    color=(72, 72, 72),
    name="Rat",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(
        hp=5,
        base_defense=0,
        base_power=3,
        field_of_view=0,
        immunities=[DamageType.SLASHING, DamageType.LIGHTNING]),
    inventory=Inventory(capacity=1),
    level=Level(xp_given=15),
    move_cooldown=.2,
    spawn_type=SpawnType.SWARM
)

bat = Actor(
    char="b",
    color=(0, 0, 0),
    name="Bat",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(
        hp=5,
        base_defense=0,
        base_power=3,
        field_of_view=0,
        flying=True
    ),
    inventory=Inventory(capacity=1),
    level=Level(xp_given=20),
    move_cooldown=.2,
    spawn_type=SpawnType.SWARM
)

goblin = Actor(
    char="g",
    color=(58, 130, 58),
    name="Goblin",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=8, base_defense=0, base_power=5, field_of_view=0),
    inventory=Inventory(capacity=1),
    level=Level(xp_given=20),
    move_cooldown=.4,
    spawn_type=SpawnType.DOUBLE
)

orc = Actor(
    char="o",
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=0, base_power=8, field_of_view=0, resistances=[DamageType.BLUDGEONING]),
    inventory=Inventory(capacity=1),
    level=Level(xp_given=35),
    move_cooldown=.6
)

troll = Actor(
    char="T",
    color=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(
        hp=16,
        base_defense=1,
        base_power=10,
        field_of_view=0,
        resistances=[DamageType.BLUDGEONING, DamageType.SLASHING]
    ),
    inventory=Inventory(capacity=1),
    level=Level(xp_given=100),
    move_cooldown=1
)

confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10)
)

fireball_scroll = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
)

health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4)
)

lightning_scroll = Item(
    char="~",
    color=(255, 255, 0),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5)
)
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

dagger = Item(char="/", color=(0, 191, 255), name="Dagger", equippable=equippable.Dagger())

sword = Item(char="/", color=(0, 191, 255), name="Sword", equippable=equippable.Sword())

club = Item(char="/", color=(0, 191, 255), name="Club", equippable=equippable.Club())

unarmed = Item(char="/", color=(0, 191, 255), name="Unarmed", equippable=equippable.Unarmed())

bow = Item(
    char="/",
    color=(0, 191, 255),
    name="Bow",
    equippable=equippable.Bow(ammo_type=AmmoType.ARROW, range_dmg_bonus=2, range_dist_bonus=2)
)

long_bow = Item(
    char="/",
    color=(80, 191, 255),
    name="Long Bow",
    equippable=equippable.Bow(ammo_type=AmmoType.ARROW, range_dmg_bonus=4, range_dist_bonus=4)
)

leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    char="[", color=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail()
)

lantern = Item(
    char="*", color=(255, 255, 0), name="Lantern", equippable=equippable.Lantern()
)

weapon_factory = {
    WeaponType.DAGGER: dagger,
    WeaponType.UNARMED: unarmed,
    WeaponType.SWORD: sword,
    WeaponType.CLUB: club,
    WeaponType.BOW: bow,
}
