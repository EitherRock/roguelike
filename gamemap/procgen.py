from __future__ import annotations

import copy
import random
from typing import Dict, Iterator, List, Tuple, TYPE_CHECKING
import tcod
import entity_factories
from gamemap.game_map import GameMap
from gamemap.environment_objects import Door
from gamemap import tile_types
from enums.spawn_types import SpawnType
from enums.room_types import RoomType
from components.consumable import Key


if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity, Actor


max_items_by_floor = [
    (1, 1),  # test value
    (4, 2),
    (10, 3),
    (25, 4)
]

max_monsters_by_floor = [
    (1, 1),
    (4, 2),
    (10, 3),
    (25, 4)
]

max_locked_items_by_floor = [
    (1, 2),
    (4, 3),
    (10, 4),
    (25, 5),

]

locked_room_item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [
        (entity_factories.health_potion, 20),
        (entity_factories.long_bow, 5),
        (entity_factories.confusion_scroll, 2),
        (entity_factories.lightning_scroll, 1),
        (entity_factories.fireball_scroll, 1),
        (entity_factories.sword, 1),
        (entity_factories.chain_mail, 1),
        (entity_factories.arrow, 15),
        (entity_factories.rock, 30),
    ],
}

item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [
        (entity_factories.health_potion, 20),
        (entity_factories.bow, 5),
        (entity_factories.arrow, 15),
        (entity_factories.rock, 30)
    ],
    2: [
        (entity_factories.confusion_scroll, 10),
        (entity_factories.arrow, 25)
    ],
    4: [
        (entity_factories.lightning_scroll, 25),
        (entity_factories.sword, 5)
    ],
    6: [
        (entity_factories.fireball_scroll, 25),
        (entity_factories.chain_mail, 15)
    ],
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [
        (entity_factories.orc, 40),
        (entity_factories.rat, 80),
        (entity_factories.goblin, 65)
    ],
    2: [(entity_factories.bat, 60)],
    3: [(entity_factories.troll, 15)],
    5: [(entity_factories.troll, 30)],
    7: [(entity_factories.troll, 60)],
}


def get_max_value_for_floor(
    max_value_by_floor: List[Tuple[int, int]], floor: int
) -> int:
    current_value = 0

    for floor_minimum, value in max_value_by_floor:
        if floor_minimum > floor:
            break
        else:
            current_value = value

    return current_value


def get_entities_at_random(
    weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
    number_of_entities: int,
    floor: int,
) -> List[Entity]:
    entity_weighted_chances = {}

    for key, values in weighted_chances_by_floor.items():
        if key > floor:
            break
        else:
            for value in values:
                entity = value[0]
                weighted_chance = value[1]

                entity_weighted_chances[entity] = weighted_chance

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    chosen_entities = random.choices(
        entities, weights=entity_weighted_chance_values, k=number_of_entities
    )

    return chosen_entities


def place_entities(room: RectangularRoom, dungeon: GameMap, floor_number: int,) -> None:
    # Check if the room is a locked room
    is_locked_room = room.room_type == RoomType.LOCKED

    if is_locked_room:
        # Get the exact number of locked items for the floor
        number_of_locked_items = get_max_value_for_floor(max_locked_items_by_floor, floor_number)
        locked_room_items: List[Entity] = get_entities_at_random(
            locked_room_item_chances, number_of_locked_items, floor_number
        )
        # Spawn each locked room item
        for entity in locked_room_items:
            spawn_single(entity, dungeon, room)
        return  # Skip spawning regular entities in locked rooms.

    # How many monsters can spawn in the room?
    number_of_monsters = random.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    )

    number_of_items = random.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
    )

    # add monster to list per the amount that can be in the room
    monsters: List[Entity] = get_entities_at_random(
        enemy_chances, number_of_monsters, floor_number
    )
    items: List[Entity] = get_entities_at_random(
        item_chances, number_of_items, floor_number
    )

    # Spawn items
    for entity in items:
        spawn_single(entity, dungeon, room)

    # Spawn Monsters
    for entity in monsters:
        if entity.spawn_type == SpawnType.SINGLE:
            spawn_single(entity, dungeon, room)

        elif entity.spawn_type == SpawnType.DOUBLE:
            spawn_double(entity, dungeon, room)

        elif entity.spawn_type == SpawnType.TRIPLE:
            spawn_triple(entity, dungeon, room)

        elif entity.spawn_type == SpawnType.SWARM:
            spawn_swarm(entity, dungeon, room)
        else:
            spawn_single(entity, dungeon, room)


def spawn_single(entity: Entity, dungeon: GameMap, room: RectangularRoom) -> None:
    """
    Spawn a single entity within the given room.

    Args:
        entity: The entity to spawn.
        dungeon: The game map where the entity will be placed.
        room: The room where the entity will be spawned.
    """
    x = random.randint(room.x1 + 1, room.x2 - 1)
    y = random.randint(room.y1 + 1, room.y2 - 1)

    # Ensure no entity is already at the chosen location
    if not any(existing_entity.x == x and existing_entity.y == y for existing_entity in dungeon.entities):
        # entity.spawn(dungeon, x, y)
        room.room_entities.append(entity.spawn(dungeon, x, y))


def spawn_double(entity: Entity, dungeon: GameMap, room: RectangularRoom) -> None:
    """
    Spawn two of an entity within the given room.

    Args:
        entity: The entity to spawn.
        dungeon: The game map where the entity will be placed.
        room: The room where the entity will be spawned.
    """
    for _ in range(2):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        # Ensure no entity is already at the chosen location
        if not any(existing_entity.x == x and existing_entity.y == y for existing_entity in dungeon.entities):
            # entity.spawn(dungeon, x, y)
            room.room_entities.append(entity.spawn(dungeon, x, y))


def spawn_triple(entity: Entity, dungeon: GameMap, room: RectangularRoom) -> None:
    """
    Spawn three of an entity within the given room.

    Args:
        entity: The entity to spawn.
        dungeon: The game map where the entity will be placed.
        room: The room where the entity will be spawned.
    """
    for _ in range(3):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        # Ensure no entity is already at the chosen location
        if not any(existing_entity.x == x and existing_entity.y == y for existing_entity in dungeon.entities):
            # entity.spawn(dungeon, x, y)
            room.room_entities.append(entity.spawn(dungeon, x, y))


def spawn_swarm(
    entity: Entity,
    dungeon: GameMap,
    room: RectangularRoom
) -> None:
    """
    Spawns a swarm of the same entity within the given room at random positions.

    :param entity: The entity to spawn as part of the swarm.
    :param room: The room where the swarm will spawn.
    :param dungeon: The game map where the entities will be placed.
    """
    amount = random.randint(3, 5)
    for _ in range(amount):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(existing_entity.x == x and existing_entity.y == y for existing_entity in dungeon.entities):
            # entity.spawn(dungeon, x, y)
            room.room_entities.append(entity.spawn(dungeon, x, y))


def tunnel_between(
        start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5: # 50% chance.
        # Move horizontally, then vertically.
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def generate_dungeon(
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        map_width: int,
        map_height: int,
        engine: Engine,
) -> tuple[GameMap, list[RectangularRoom]]:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []
    keys: List[Key] = []

    center_of_last_room = (0, 0)
    room_num = 0
    floor_num = engine.game_world.current_floor

    for r in range(max_rooms):
        room_num += 1
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # "RectangularRoom" class makes rectangles easier to work with
        new_room = RectangularRoom(
            room_id=f"{str(floor_num)}_{str(room_num)}",
            x=x,
            y=y,
            width=room_width,
            height=room_height,
            room_type=RoomType.NORMAL)

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # This room intersects, so go to the next attempt.
        # If there are no intersections then the room is valid.

        # Dig out this room's inner area.
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # The first room, where the player starts.
            player.place(*new_room.center, gamemap=dungeon)
            dungeon.upstairs_location = new_room.center

        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.

            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor
                # dungeon.tiles[x, y] = tile_types.tunnel

            center_of_last_room = new_room.center

        dungeon.tiles[center_of_last_room] = tile_types.down_stairs
        dungeon.downstairs_location = center_of_last_room
        dungeon.tiles[dungeon.upstairs_location] = tile_types.up_stairs

        # Finally, append the new room to the list.
        rooms.append(new_room)

    keys = find_and_mark_doors(dungeon, rooms, floor_num=floor_num)

    for room in rooms:
        place_entities(room, dungeon, engine.game_world.current_floor)

    distribute_keys(keys, rooms)

    return dungeon, rooms


def distribute_keys(keys: List[Key], rooms: List[RectangularRoom]) -> None:
    """Distribute keys to enemies after they have been placed."""
    from entity import Actor

    all_enemies = []

    # Collect all enemies and their room IDs
    for room in rooms:
        enemies = [
            entity for entity in getattr(room, "room_entities", [])
            if isinstance(entity, Actor)
        ]
        all_enemies.extend([(enemy, room.room_id) for enemy in enemies])

    # Assign keys to enemies
    for key in keys:
        target_locked_room_id = key.consumable.key_id

        # Find enemies not in the locked room the key corresponds to
        eligible_enemies = [
            (enemy, room_id) for enemy, room_id in all_enemies
            if room_id != target_locked_room_id
        ]

        # Fallback: If all eligible enemies are in locked rooms
        if not eligible_enemies:
            eligible_enemies = all_enemies

        if eligible_enemies:
            chosen_enemy, _ = random.choice(eligible_enemies)
            key.parent = chosen_enemy.inventory
            chosen_enemy.inventory.items.append(key)


def find_and_mark_doors(
        dungeon: GameMap,
        rooms: List[RectangularRoom],
        floor_num: int,
) -> List[Key]:
    """Find and mark door locations where tunnels connect to rooms."""
    from entity import Actor
    keys = []
    for room in rooms:
        print(room.room_id)
        room_bounds = {
            (x, y)
            for x in range(room.x1 + 1, room.x2)
            for y in range(room.y1 + 1, room.y2)
        }
        adjacent_floors_total = 0
        potential_doors = []

        # Check tiles at the room's perimeter
        for x in range(room.x1, room.x2 + 1):
            for y in range(room.y1, room.y2 + 1):
                # Only consider perimeter tiles
                if x in (room.x1, room.x2) or y in (room.y1, room.y2):
                    if dungeon.tiles[x, y] == tile_types.floor:
                        adjacent_floors_total += 1
                        # Floor tile at the edge is a potential door
                        adjacent_floors = 0
                        adjacent_walls = 0

                        north = {
                            "is_walls": False,
                            "x_y": (0, -1)
                        }

                        east = {
                            "is_walls": False,
                            "x_y": (1, 0)
                        }

                        south = {
                            "is_walls": False,
                            "x_y": (0, 1)
                        }

                        west = {
                            "is_walls": False,
                            "x_y": (-1, 0)
                        }

                        for direction in (north, east, south, west):
                            dx = direction["x_y"][0]
                            dy = direction["x_y"][1]
                            nx, ny = x + dx, y + dy

                            if not dungeon.in_bounds(nx, ny):
                                continue
                            if dungeon.tiles[nx, ny] == tile_types.floor and (nx, ny) not in room_bounds:
                                adjacent_floors += 1

                            elif dungeon.tiles[nx, ny] == tile_types.wall:
                                direction["is_walls"] = True

                        # A valid door:
                        # - Must have exactly 1 adjacent floor outside the room
                        # - Must have at least 2 adjacent walls

                        north_wall = north["is_walls"]
                        south_wall = south["is_walls"]
                        east_wall = east["is_walls"]
                        west_wall = west["is_walls"]

                        if adjacent_floors == 1:
                            if north_wall and south_wall and not east_wall and not west_wall:
                                potential_doors.append((x, y))

                            if east_wall and west_wall and not north_wall and not south_wall:
                                potential_doors.append((x, y))

        if adjacent_floors_total == 1:
            if room.room_id != f"{str(floor_num)}_1":
                x, y = potential_doors[0]
                key = copy.deepcopy(entity_factories.key)
                if isinstance(key.consumable, Key):
                    key.consumable.key_id = room.room_id
                    keys.append(key)

                door = Door(x, y, is_open=False, gamemap=dungeon, is_locked=True, room_id=room.room_id)
                dungeon.environment_objects[(x, y)] = door
                dungeon.tiles[x, y] = tile_types.closed_door
                room.room_type = RoomType.LOCKED
            else:
                x, y = potential_doors[0]
                door = Door(x, y, is_open=False, gamemap=dungeon, room_id=room.room_id)
                dungeon.environment_objects[(x, y)] = door
                dungeon.tiles[x, y] = tile_types.closed_door
        else:
            # Mark door tiles
            for x, y in potential_doors:
                door = Door(x, y, is_open=False, gamemap=dungeon, room_id=room.room_id)
                dungeon.environment_objects[(x, y)] = door
                dungeon.tiles[x, y] = tile_types.closed_door
    return keys


class Room:
    def __init__(self, room_id: str, room_type: RoomType):
        self.room_id = room_id
        self.room_type = room_type
        self.room_entities: List = []


class RectangularRoom(Room):
    def __init__(self, room_id: str, x: int, y: int, width: int, height: int, room_type: RoomType):
        super().__init__(room_id, room_type)
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return (
                self.x1 <= other.x2
                and self.x2 >= other.x1
                and self.y1 <= other.y2
                and self.y2 > other.y1
        )