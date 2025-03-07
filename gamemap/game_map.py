from __future__ import annotations
from typing import Iterable, Dict, Iterator, Optional, TYPE_CHECKING, List, Tuple
import numpy as np  # type: ignore
from tcod.console import Console
from entity import Actor, Item
from gamemap import tile_types
import colors
from gamemap.environment_objects import EnvironmentObject, Stairs
from components.consumable import Key

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(
            self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player can currently see

        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player has seen before

        # self.downstairs_location = (0, 0)
        self.downstairs_location = Tuple[int, int]
        self.upstairs_location = None
        self.environment_objects: Dict[Tuple[int, int], EnvironmentObject] = {}
        self.keys: List[Key] = []

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this map's living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(
            self, location_x: int, location_y: int
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                    entity.blocks_movement
                    and entity.x == location_x
                    and entity.y == location_y
            ):
                return entity
        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def get_environment_object_at(self, x: int, y: int) -> Optional[EnvironmentObject]:
        """Retrieve the environment object at the specified position."""
        return self.environment_objects.get((x, y))

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """

        console.rgb[0: self.width, 0: self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(
                    x=entity.x, y=entity.y, string=entity.char, fg=entity.color
                )

    def update_hit_effects(self, current_time):
        """Update the hit timer for each entity."""
        # Update each entity's hit effect based on the elapsed time
        for entity in self.entities:
            if isinstance(entity, Actor):
                if entity.is_alive:
                    entity.update_hit_effect(current_time)


class World:
    def __init__(
            self,
            engine: Engine,
            map_width: int,
            map_height: int,
    ):
        self.engine = engine
        self.map_width = map_width
        self.map_height = map_height

    def generate(self) -> None:
        """This method will be overridden by subclasses."""
        raise NotImplementedError("Subclasses must override the `generate` method.")


class DungeonWorld(World):
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
            self,
            *,
            engine: Engine,
            map_width: int,
            map_height: int,
            max_rooms: int,
            room_min_size: int,
            room_max_size: int,
            current_floor: int = 0,
    ):
        super().__init__(
            engine=engine,
            map_width=map_width,
            map_height=map_height
        )

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor
        self.previous_floors: Dict[int: GameMap] = {}

    def generate(self) -> None:
        from gamemap.procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
        )

    def descend_dungeon(self) -> None:
        """Move deeper into the DungeonWorld."""
        current_floor = self.engine.game_world.current_floor
        self.engine.game_world.previous_floors[current_floor] = self.engine.game_map

        # Check if revisiting a floor
        if (current_floor + 1) in self.engine.game_world.previous_floors:
            self.engine.game_map = self.engine.game_world.previous_floors[current_floor + 1]
            self.engine.game_world.current_floor += 1
            self.engine.player.place(*self.engine.game_map.upstairs_location, gamemap=self.engine.game_map)
        else:
            self.engine.game_world.generate()

        self.engine.message_log.add_message("You descend the staircase.", colors.descend)

    def exit_dungeon(self) -> None:
        """Transition from DungeonWorld back to OverWorld."""
        self.engine.game_world.current_floor = 0
        self.engine.switch_maps("world")
        self.engine.game_world = self.engine.active_map
        self.engine.game_map = self.engine.game_world.previous_floors[self.engine.game_world.current_floor]
        self.engine.game_world.previous_floors.clear()
        self.engine.player.place(*self.engine.game_map.downstairs_location, gamemap=self.engine.game_map)
        self.engine.message_log.add_message("You successfully escape the dungeon.", colors.ascend)

    def ascend_dungeon(self) -> None:
        """Move upward in the DungeonWorld."""
        current_floor = self.engine.game_world.current_floor
        self.engine.game_world.previous_floors[current_floor] = self.engine.game_map

        previous_floor = current_floor - 1
        self.engine.game_world.current_floor = previous_floor
        self.engine.game_map = self.engine.game_world.previous_floors[previous_floor]
        self.engine.player.place(*self.engine.game_map.downstairs_location, gamemap=self.engine.game_map)
        self.engine.message_log.add_message("You ascend the staircase.", colors.ascend)


class OverWorld:
    def __init__(
            self,
            *,
            engine: Engine,
            map_width: int,
            map_height: int,
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.current_floor = 0
        self.previous_floors: Dict[int: GameMap] = {}

    def generate(self) -> None:
        player = self.engine.player
        world = GameMap(self.engine, self.map_width, self.map_height, entities=[player])

        x = self.map_width // 2
        y = self.map_height // 2
        dungeon_entrance = (x, y - 5)
        player.place(x, y, gamemap=world)

        world.tiles = np.full(
            (self.map_width, self.map_height),
            fill_value=tile_types.floor,
            order='F',
        )

        downstairs = Stairs(*dungeon_entrance, gamemap=world, direction="down")
        world.environment_objects[(downstairs.x, downstairs.y)] = downstairs
        world.tiles[dungeon_entrance] = downstairs.tile
        world.downstairs_location = dungeon_entrance

        self.engine.game_map = world

    def enter_dungeon(self) -> None:
        """Transition from OverWorld to DungeonWorld."""
        # Save the current camp map in previous_floors under floor 0
        self.engine.game_world.previous_floors[0] = self.engine.game_map

        self.engine.switch_maps("dungeon")
        self.engine.game_world = self.engine.active_map
        self.engine.game_world.generate()
        self.engine.message_log.add_message("You enter the dungeon, good luck...", colors.descend)



