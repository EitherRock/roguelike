from __future__ import annotations

import copy
from typing import Optional, Tuple, TYPE_CHECKING

import colors
import exceptions
from stack_limit import STACK_LIMITS
from util import format_item_name
from gamemap.environment_objects import EnvironmentObject

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item
    from gamemap.environment_objects import Door


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """

        raise NotImplementedError()


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        from components.equippable import Ammo
        from components.consumable import Scroll, Potion
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:

                # Check if the item has equippable or consumable properties with a quantity
                has_quantity = False
                stack_limit = float("inf")
                existing_quantity = 0
                new_quantity = 0
                new_item_type = None
                existing_item_type = None

                if hasattr(item, "equippable") and item.equippable \
                        and getattr(item.equippable, "quantity", None) is not None:
                    has_quantity = True
                    if isinstance(item.equippable, Ammo):
                        new_quantity = item.equippable.quantity
                        new_item_type = item.equippable
                        stack_limit = STACK_LIMITS[new_item_type.ammo_type.name]

                elif hasattr(item, "consumable") and item.consumable \
                        and getattr(item.consumable, "quantity", None) is not None:
                    if isinstance(item.consumable, (Potion, Scroll)):
                        has_quantity = True
                        new_quantity = item.consumable.quantity
                        new_item_type = item.consumable
                        stack_limit = STACK_LIMITS[new_item_type.consumable_type.name]

                if has_quantity:
                    for inv_item in inventory.items:
                        if inv_item.name == item.name:
                            # Determine stack limit and existing quantities
                            if isinstance(inv_item.equippable, Ammo):
                                # stack_limit = STACK_LIMITS[inv_item.equippable.ammo_type.name]
                                existing_quantity = inv_item.equippable.quantity
                                existing_item_type = inv_item.equippable

                            elif isinstance(inv_item.consumable, (Potion, Scroll)):
                                # stack_limit = STACK_LIMITS[inv_item.consumable.consumable_type.name]
                                existing_quantity = inv_item.consumable.quantity
                                existing_item_type = inv_item.consumable

                            if existing_quantity >= stack_limit:
                                raise exceptions.Impossible(
                                    f"{format_item_name(item.name, existing_quantity)} full."
                                )

                            # Add quantities up to the stack limit
                            amount_to_take = min(stack_limit - existing_quantity, new_quantity)
                            existing_item_type.quantity += amount_to_take
                            new_item_type.quantity -= amount_to_take

                            self.engine.message_log.add_message(
                                f"You picked up {amount_to_take}x {format_item_name(item.name, amount_to_take)}!"
                            )

                            # Remove item if fully picked up
                            if new_item_type.quantity <= 0:
                                self.engine.game_map.entities.remove(item)
                                item.parent = inventory
                            return

                    # If it's the first time picking up this type of item
                    if new_quantity > stack_limit:
                        amount_to_take = stack_limit
                        new_item_type.quantity -= amount_to_take
                        new_item = copy.deepcopy(item)
                        if isinstance(new_item.equippable, Ammo):
                            new_item.equippable.quantity = amount_to_take
                        else:
                            new_item.consumable.quantity = amount_to_take

                        inventory.items.append(new_item)
                        self.engine.message_log.add_message(
                            f"You picked up {amount_to_take}x {format_item_name(item.name, amount_to_take)}!"
                        )
                        return

                    inventory.items.append(item)
                    self.engine.message_log.add_message(
                        f"You picked up {new_quantity}x {format_item_name(item.name, new_quantity)}!"
                    )
                    self.engine.game_map.entities.remove(item)
                    item.parent = inventory
                    return

                # Handle non-stackable items
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = inventory
                inventory.items.append(item)
                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                return

        raise exceptions.Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(
        self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this action's destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        if self.item.consumable:
            self.item.consumable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)
        self.entity.inventory.drop(self.item)


class EquipAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)


class WaitAction(Action):
    def perform(self) -> None:
        pass


class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.descend_stairs()
        elif (self.entity.x, self.entity.y) == self.engine.game_map.upstairs_location:
            self.ascend_stairs()
        else:
            raise exceptions.Impossible("There are no stairs here.")

    def descend_stairs(self) -> None:
        from gamemap.game_map import OverWorld
        """Handle descending stairs."""
        if isinstance(self.engine.game_world, OverWorld):
            self.engine.game_world.enter_dungeon()
        else:
            self.engine.game_world.descend_dungeon()

    def ascend_stairs(self) -> None:
        from gamemap.game_map import DungeonWorld
        """Handle ascending stairs."""
        if isinstance(self.engine.game_world, DungeonWorld):
            if self.engine.game_world.current_floor == 1:
                self.engine.game_world.exit_dungeon()
            else:
                self.engine.game_world.ascend_dungeon()


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination"""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination"""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination"""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        from components.equippable import Weapon
        from enums.damage_types import DamageType
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        if target.fighter.flying:
            self.engine.message_log.add_message(f"Cannot reach flying {target.name}", colors.red)
            return

        damage = self.entity.fighter.melee_power - target.fighter.defense
        if damage <= 0:
            damage = 1

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"

        if self.entity.equipment.weapon and isinstance(self.entity.equipment.weapon.equippable, Weapon):
            damage_type = self.entity.equipment.weapon.equippable.damage_type
        else:
            damage_type = DamageType.BLUDGEONING

        target.fighter.take_damage(damage, damage_type, attack_desc)


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by entity.
            raise exceptions.Impossible("That way is blocked.")

        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()

        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()


class RangedAction(Action):
    def __init__(self, entity: Actor, target_xy: Tuple[int, int]):
        """
        A ranged attack action.
        :param entity: The actor performing the action.
        :param target_xy: The target's coordinates (x, y).
        """
        super().__init__(entity)
        self.target_xy = target_xy

    def perform(self) -> None:
        from components.equippable import Ammo, Bow

        target_x, target_y = self.target_xy

        target = self.engine.game_map.get_actor_at_location(target_x, target_y)
        if not target:
            raise exceptions.Impossible("No target at the specified location.")

        equipment = self.entity.equipment
        weapon_ammo_type = None
        if equipment.ranged_weapon and isinstance(equipment.ranged_weapon.equippable, Bow):

            weapon_ammo_type = equipment.ranged_weapon.equippable.ammo_type

        """
        Check if ammo is equipped, if ranged weapon is equipped then check if ammo type matches weapon type, else rock
        """
        if equipment.ammo and isinstance(equipment.ammo.equippable, Ammo):
            ammo_type = equipment.ammo.equippable.ammo_type

            if weapon_ammo_type:
                if ammo_type == weapon_ammo_type:
                    damage = self.entity.fighter.range_power - target.fighter.defense
                    damage_type = equipment.ammo.equippable.damage_type
                    attack_desc = f"{self.entity.name.capitalize()} fires an arrow at {target.name}"
                    equipment.ammo.equippable.use()
                    target.fighter.take_damage(damage, damage_type, attack_desc)
                else:
                    raise exceptions.Impossible(
                        f"{equipment.ranged_weapon.name} cannot use {ammo_type.name.lower().capitalize()} as ammo."
                    )

            else:
                damage = self.entity.fighter.range_power - target.fighter.defense
                damage_type = equipment.ammo.equippable.damage_type

                if damage_type:
                    attack_desc = f"{self.entity.name.capitalize()} throws a rock at {target.name}"
                    equipment.ammo.equippable.use()
                    target.fighter.take_damage(damage, damage_type, attack_desc)
        else:
            if weapon_ammo_type:
                raise exceptions.Impossible(f"No {weapon_ammo_type.name}s equipped.")
            else:
                raise exceptions.Impossible("Nothing to throw.")


class EnvironmentAction(Action):
    def __init__(self, env_object: EnvironmentObject, entity: Actor):
        super().__init__(entity)
        self.object = env_object

    def perform(self) -> None:
        from gamemap.environment_objects import Door
        if isinstance(self.object, Door):
            action = DoorAction(self.object, self.entity)
            return action.perform()


class DoorAction(Action):
    def __init__(self, door: Door, entity: Actor):
        super().__init__(entity)
        self.door = door

    def perform(self) -> None:
        from components.consumable import Key

        if not self.door.is_locked:
            if self.door.is_open:
                self.door.close()
                self.entity.gamemap.engine.message_log.add_message("You close the door.", colors.white)
            else:
                self.door.open()
                self.entity.gamemap.engine.message_log.add_message("You open the door.", colors.white)
        else:
            # Check player's inventory for a key that matches the door's ID
            for item in self.entity.inventory.items:
                if isinstance(item.consumable, Key):
                    if item.consumable.key_id == self.door.room_id:
                        self.door.unlock()  # Unlock the door
                        self.entity.gamemap.engine.message_log.add_message(
                            "You use the key to unlock the door.", colors.white
                        )
                        self.door.open()
                        item.consumable.consume()
                        self.entity.gamemap.engine.message_log.add_message("You open the door.", colors.white)
                        return  # Exit after unlocking and opening the door

            # If no matching key is found
            self.door.update_tile()
            self.entity.gamemap.engine.message_log.add_message("The door is locked.",
                                                               colors.white)
