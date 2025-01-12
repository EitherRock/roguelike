from __future__ import annotations
import copy
import math
import random
import time
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union
from enums.spawn_types import SpawnType
from components.equippable import Unarmed, UnarmedRanged, Ammo
from components.quality import get_random_quality

from enums.render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.consumable import Consumable
    from components.equipment import Equipment
    from components.equippable import Equippable
    from components.fighter import Fighter
    from components.inventory import Inventory
    from components.level import Level
    from gamemap.game_map import GameMap
    from entity_factories.weapon_factory import weapon_factory

T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    parent: Union[GameMap, Inventory]

    def __init__(
            self,
            parent: Optional[GameMap] = None,
            x: int = 0,
            y: int = 0,
            char: str = "?",
            color: Tuple[int, int, int] = (255, 255, 255),
            blocks_movement: bool = False,
            name: str = "<Unnamed>",
            render_order: RenderOrder = RenderOrder.CORPSE,
            move_cooldown: float = 0.0,
            spawn_type: SpawnType = SpawnType.SINGLE
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.original_color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        self.last_move_time = 0  # time of last movement
        self.hit_timer = 0
        self.last_hit_time = None
        self.move_cooldown = move_cooldown  # cooldown in seconds
        self.spawn_type = spawn_type

        if parent:
            # If parent isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    def spawn(self: T, gamemap: GameMap, x: int, y: int, floor_number: int = 0) -> T:
        """Spawn a copy of this instance at the given location."""
        from components.fighter import Fighter

        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap

        if isinstance(clone, Actor) and isinstance(clone.fighter, Fighter):
            if clone.fighter.allowed_weapon_types:
                random_weapon = random.choice(clone.fighter.allowed_weapon_types)
                self.add_weapon(clone, random_weapon)

        if isinstance(clone, Item):
            if clone.equippable and hasattr(clone.equippable, "quantity"):
                clone.equippable.quantity = clone.equippable.random_quantity()

            if clone.equippable and hasattr(clone.equippable, "quality"):
                if not isinstance(clone.equippable, (Unarmed, UnarmedRanged, Ammo)):
                    clone.equippable.quality = get_random_quality(floor_number)
                    clone.color = clone.equippable.quality.color

        gamemap.entities.add(clone)
        return clone

    def add_weapon(self, clone, weapon_choice) -> None:
        from entity_factories.weapon_factory import weapon_factory
        if weapon_choice in weapon_factory:
            weapon = copy.deepcopy(weapon_factory.get(weapon_choice))
            if weapon:
                weapon.parent = clone.inventory
                clone.inventory.items.append(weapon)
                clone.equipment.toggle_equip(weapon, add_message=False)

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """Place this entity at a new location. Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"):  # Probably uninitialized.
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """
        Return the distance between the current entity and the given (x, y) coordinate.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        current_time = time.time()
        if current_time - self.last_move_time >= self.move_cooldown:
            self.x += dx
            self.y += dy
            self.last_move_time = current_time  # Update the last movement time

    def update_hit_effect(self, current_time: float):
        """Update the hit effect based on elapsed time since the last hit."""
        if self.last_hit_time is not None:
            time_since_hit = current_time - self.last_hit_time
            if time_since_hit >= self.hit_timer:
                self.color = self.original_color  # Revert to original color after duration
                self.last_hit_time = None  # Reset the hit time


class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        ai_cls: Type[BaseAI],
        equipment: Equipment,
        fighter: Fighter,
        inventory: Inventory,
        level: Level,
        move_cooldown: float = 0.2,
        spawn_type: SpawnType = SpawnType.SINGLE
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
            move_cooldown=move_cooldown,
            spawn_type=spawn_type
        )

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.equipment: Equipment = equipment
        self.equipment.parent = self

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

        self.level = level
        self.level.parent = self

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)


class Item(Entity):
    def __init__(
            self,
            *,
            x: int = 0,
            y: int = 0,
            char: str = "?",
            color: Tuple[int, int, int] = (255, 255, 255),
            name: str = "<Unnamed>",
            consumable: Optional[Consumable] = None,
            equippable: Optional[Equippable] = None,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM
        )

        self.consumable = consumable

        if self.consumable:
            self.consumable.parent = self

        self.equippable = equippable

        if self.equippable:
            self.equippable.parent = self

    def __str__(self):
        return f"Name: {self.name}, equippable: {self.equippable}"
