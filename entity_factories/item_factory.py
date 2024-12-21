from components import consumable, equippable
from entity import Item


lantern = Item(
    char="*", color=(255, 255, 0), name="Lantern", equippable=equippable.Lantern()
)

key = Item(
    char="?", color=(255, 255, 0), name="Key", consumable=consumable.Key()
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

firebolt_scroll = Item(
    char="~",
    color=(255, 0, 0),
    name="Firebolt Scroll",
    consumable=consumable.FireBoltDamageConsumable(damage=5, maximum_range=5)
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