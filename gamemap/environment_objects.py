from __future__ import annotations
from typing import Tuple, TYPE_CHECKING
from gamemap.tile_types import closed_door, open_door, locked_door, up_stairs, down_stairs
import colors


if TYPE_CHECKING:
    from gamemap.game_map import GameMap


class EnvironmentObject:
    """Base class for all environment objects in the game."""
    def __init__(self, x: int, y: int, gamemap: GameMap):
        self.x = x
        self.y = y
        self.gamemap = gamemap  # Reference to the GameMap this object belongs to

    @property
    def position(self) -> Tuple[int, int]:
        """Return the (x, y) position of the object."""
        return self.x, self.y

    @property
    def tile(self):
        """Return the tile type for this environment object."""
        raise NotImplementedError("Subclasses must implement the `tile` property.")


class Door(EnvironmentObject):
    """A class to represent an interactable door."""

    def __init__(
            self,
            x: int,
            y: int,
            is_open: bool,
            gamemap: GameMap,
            room_id: str,
            is_locked: bool = False
    ):
        super().__init__(x, y, gamemap)
        self.x = x
        self.y = y
        self.is_open = is_open
        self.is_locked = is_locked
        self.room_id = room_id

    @property
    def tile(self):
        """Return the tile type based on the door's state."""
        if self.is_locked:
            return locked_door
        return open_door if self.is_open else closed_door

    def open(self):
        self.is_open = True
        self.is_locked = False  # Ensure the door is unlocked when opened
        self.update_tile()

    def close(self):
        self.is_open = False
        self.update_tile()

    def lock(self):
        self.is_locked = True
        self.is_open = False
        self.update_tile()

    def unlock(self):
        self.is_locked = False
        self.update_tile()

    def update_tile(self) -> None:
        """Update the game map tile to reflect the door's state."""
        self.gamemap.tiles[self.x, self.y] = self.tile


class Stairs(EnvironmentObject):
    """A generalized class to represent stairs, either up or down."""

    def __init__(self, x: int, y: int, gamemap: GameMap, direction: str):
        """
        :param direction: "up" for upstairs, "down" for downstairs.
        """
        super().__init__(x, y, gamemap)
        if direction not in {"up", "down"}:
            raise ValueError("Direction must be either 'up' or 'down'.")
        self.direction = direction

    @property
    def tile(self):
        """Return the tile type based on the direction."""
        return up_stairs if self.direction == "up" else down_stairs

