from components import equippable
from entity import Item


leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    char="[", color=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail()
)

helmet = Item(
    char="[", color=(139, 69, 19), name="Helmet", equippable=equippable.Helmet()
)

boots = Item(
    char="[", color=(139, 69, 19), name="Boots", equippable=equippable.Boots()
)
