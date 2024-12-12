from __future__ import annotations
from typing import Tuple, TYPE_CHECKING
from gamemap.tile_types import closed_door, open_door, locked_door
import colors


if TYPE_CHECKING:
    from gamemap.game_map import GameMap


class EnvironmentObject:
    """Base class for all environment objects in the game."""
    def __init__(self, x: int, y: int, gamemap: GameMap):
        self.x = x
        self.y = y
        self.gamemap = gamemap  # Reference to the GameMap this object belongs to

    def interact(self) -> None:
        """Define what happens when the object is interacted with."""
        raise NotImplementedError()

    @property
    def position(self) -> Tuple[int, int]:
        """Return the (x, y) position of the object."""
        return self.x, self.y


class Door(EnvironmentObject):
    """A class to represent an interactable door."""

    def __init__(
            self,
            x: int,
            y: int,
            is_open: bool,
            gamemap: GameMap,
            room_id: int,
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


