from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import actions
import colors
import components.ai
import components.inventory
from enums.damage_types import DamageType
from enums.consumable_type import ConsumableType
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
)

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def __init__(self, consumable_type: ConsumableType, quantity: int = 1):
        self.consumable_type = consumable_type
        self.quantity = quantity

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        """Invoke this item's ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        if self.quantity > 0:
            self.quantity -= 1
            if self.quantity == 0:
                """Remove the consumed item from its containing inventory."""
                entity = self.parent
                inventory = entity.parent

                if isinstance(inventory, components.inventory.Inventory):
                    inventory.items.remove(entity)


class Scroll(Consumable):
    def __init__(self):
        super().__init__(consumable_type=ConsumableType.SCROLL)


class Potion(Consumable):
    def __init__(self):
        super().__init__(consumable_type=ConsumableType.POTION)

class Miscellaneous(Consumable):
    def __init__(self):
        super().__init__(consumable_type=ConsumableType.MISC)


class ConfusionConsumable(Scroll):
    def __init__(self, number_of_turns: int):
        super().__init__()
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", colors.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        self.engine.message_log.add_message(
            f"The eyes of the {target.name} look vacant, as it starts to stumble around!",
            colors.status_effect_applied,
        )
        target.ai = components.ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns,
        )
        self.consume()


class HealingConsumable(Potion):
    def __init__(self, amount: int):
        super().__init__()
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                colors.health_recovered
            )
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")


class FireballDamageConsumable(Scroll):
    def __init__(self, damage: int, radius: int):
        super().__init__()
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", colors.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy)
        )

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                desc = f"The {actor.name} is engulfed in a fiery explosion,"
                actor.fighter.take_damage(self.damage, DamageType.FIRE, desc)
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()


class FireBoltDamageConsumable(Scroll):
    def __init__(self, damage: int, maximum_range: int):
        super().__init__()
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            desc = f"A fire bolt strikes the {target.name} with a sizzle,"
            target.fighter.take_damage(self.damage, DamageType.FIRE, desc)
            self.consume()
        else:
            raise Impossible("No enemy is close enough to strike.")


class LightningDamageConsumable(Scroll):
    def __init__(self, damage: int, maximum_range: int):
        super().__init__()
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            desc = f"A lightning bolt strikes the {target.name} with a loud thunder,"
            target.fighter.take_damage(self.damage, DamageType.LIGHTNING, desc)
            self.consume()
        else:
            raise Impossible("No enemy is close enough to strike.")


class Key(Miscellaneous):
    def __init__(self):
        super().__init__()
        self.key_id: str

    # def activate(self, action: actions.ItemAction) -> None:
    #     self.consume()
