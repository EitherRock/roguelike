from __future__ import annotations
import lzma
import pickle
import time
from typing import TYPE_CHECKING, Union
from tcod.console import Console
from tcod.map import compute_fov
import exceptions
from message_log import MessageLog
import render_functions

if TYPE_CHECKING:
    from entity import Actor
    from gamemap.game_map import GameMap, DungeonWorld, OverWorld


class Engine:
    game_map: GameMap
    game_world: Union[DungeonWorld, OverWorld]

    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.start_time = time.time()
        self.elapsed_time = 0
        self.player = player
        self.game_worlds = {}
        self.active_map = None

    def update_timer(self):
        self.elapsed_time = time.time() - self.start_time

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # Ignore impossible action exception from AI.

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=self.player.fighter.fov,
        )

        # Apply a circular mask to enforce a circular FOV
        fov_radius = self.player.fighter.fov
        cx, cy = self.player.x, self.player.y
        for x in range(self.game_map.width):
            for y in range(self.game_map.height):
                # Calculate the distance from the player's position
                dx = x - cx
                dy = y - cy
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance > fov_radius:
                    self.game_map.visible[x, y] = False

        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        from gamemap.game_map import DungeonWorld, OverWorld
        self.game_map.render(console)

        self.message_log.render(console=console, x=21, y=45, width=40, height=5)
        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20
        )

        if isinstance(self.game_world, DungeonWorld):
            dungeon_level = self.game_world.current_floor
        elif isinstance(self.game_world, OverWorld):
            dungeon_level = "camp"
        else:
            dungeon_level = "unknown"

        render_functions.render_dungeon_level(
            console=console,
            dungeon_level=dungeon_level,
            location=(0, 47),
        )

        render_functions.render_names_at_mouse_location(
            console=console, x=21, y=44, engine=self
        )

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)

    def switch_maps(self, map_name: str):

        if map_name in self.game_worlds:
            self.active_map = self.game_worlds[map_name]
        else:
            raise ValueError(f"No map found with name {map_name}.")
