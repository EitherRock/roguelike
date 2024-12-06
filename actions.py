from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


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
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory

                for inv_item in item.parent.items:
                    if inv_item.name == item.name and inv_item.equippable:
                        if isinstance(inv_item.equippable, Ammo):
                            inv_item.equippable.quantity += 1
                            self.engine.message_log.add_message(f"You picked up another {item.name}!")
                            return

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
        from game_map import OverWorld
        """Handle descending stairs."""
        if isinstance(self.engine.game_world, OverWorld):
            self.engine.game_world.enter_dungeon()
        else:
            self.engine.game_world.descend_dungeon()

    def ascend_stairs(self) -> None:
        from game_map import DungeonWorld
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
                    target.fighter.take_damage(damage, damage_type, attack_desc)
        else:
            if weapon_ammo_type:
                raise exceptions.Impossible(f"No {weapon_ammo_type.name}s equipped.")
            else:
                raise exceptions.Impossible("Nothing to throw.")
