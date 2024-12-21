from components.ai import HostileEnemy
from components.equipment import Equipment
from components.fighter import Fighter, Slime
from components.inventory import Inventory
from enums.spawn_types import SpawnType
from components.level import Level
from entity import Actor
from enums.damage_types import DamageType


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

slime = Actor(
    char="S",
    color=(72, 230, 72),
    name="Slime",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Slime(
        hp=12,
        base_defense=0,
        base_power=3,
        field_of_view=0,
    ),
    inventory=Inventory(capacity=1),
    level=Level(xp_given=15),
    move_cooldown=1,
    spawn_type=SpawnType.SINGLE
)

small_slime = Actor(
    char="s",
    color=(72, 230, 72),
    name="Small Slime",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(
        hp=7,
        base_defense=0,
        base_power=3,
        field_of_view=0,
    ),
    inventory=Inventory(capacity=1),
    level=Level(xp_given=15),
    move_cooldown=.8,
    spawn_type=SpawnType.SINGLE
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
