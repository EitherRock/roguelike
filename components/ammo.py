from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import actions
import colors
import components.ai
import components.inventory
from enums.damage_types import DamageType
from components.base_component import BaseComponent
from exceptions import Impossible


if TYPE_CHECKING:
    from entity import Actor, Item
    from enums.damage_types import DamageType


class Ammo(BaseComponent):
    parent: Item

    def __init__(
            self,
            quantity: int,
            damage_type: DamageType,
            damage_modifier: int = 0,
    ):
        self.quantity = quantity
        self.damage_modifier = damage_modifier
        self.damage_type = damage_type

    def use(self) -> None:
        """Reduce the quantity of the ammo by 1. Removes the item if quantity is 0."""
        if self.quantity > 0:
            self.quantity -= 1
            if self.quantity == 0:
                """Remove the consumed item from its containing inventory."""
                entity = self.parent
                inventory = entity.parent
                if isinstance(inventory, components.inventory.Inventory):
                    inventory.items.remove(entity)