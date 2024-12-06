"""Handle the loading and initialization of game sessions."""
from __future__ import annotations
import copy
import lzma
import pickle
import traceback
from typing import Optional
import tcod
import colors
from engine import Engine
import entity_factories
from game_map import DungeonWorld, OverWorld
import input_handlers
from tcod import libtcodpy


# Load the background image and remove the apha channel.
background_image = tcod.image.load("menu_background.png")[:, :, :3]


def new_game() -> Engine:
    """Return a brand new game session as an Engine instance"""
    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)
    engine.game_worlds["dungeon"] = DungeonWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height
    )

    engine.game_worlds["world"] = OverWorld(
        engine=engine,
        map_width=map_width,
        map_height=map_height
    )

    engine.switch_maps("world")
    engine.game_world = engine.active_map

    # engine.game_world.generate_floor()
    engine.game_world.generate()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to the dungeon!", colors.welcome_text
    )

    dagger = copy.deepcopy(entity_factories.dagger)
    club = copy.deepcopy(entity_factories.club)
    leather_armor = copy.deepcopy(entity_factories.leather_armor)
    lantern = copy.deepcopy(entity_factories.lantern)
    bow = copy.deepcopy(entity_factories.bow)

    dagger.parent = player.inventory
    club.parent = player.inventory
    bow.parent = player.inventory
    leather_armor.parent = player.inventory
    lantern.parent = player.inventory

    player.inventory.items.append(dagger)
    player.equipment.toggle_equip(dagger, add_message=False)

    player.inventory.items.append(club)
    player.equipment.toggle_equip(club, add_message=False)

    player.inventory.items.append(bow)
    player.equipment.toggle_equip(bow, add_message=True)

    player.inventory.items.append(leather_armor)
    player.equipment.toggle_equip(leather_armor, add_message=False)

    player.inventory.items.append(lantern)
    player.equipment.toggle_equip(lantern, add_message=False)

    engine.update_fov()

    return engine


def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "DUNGEON DIVE",
            fg=colors.menu_title,
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By Nathan Lesmann",
            fg=colors.menu_title,
            alignment=libtcodpy.CENTER
        )

        menu_width = 24
        for i, text in enumerate(
            ["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=colors.menu_text,
                bg=colors.black,
                alignment=libtcodpy.CENTER,
                bg_blend=libtcodpy.BKGND_ALPHA(64),
            )

    def ev_keydown(
            self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.KeySym.q, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.KeySym.c:
            try:
                return input_handlers.MainGameEnventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()  # print to stderr.
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.KeySym.n:
            return input_handlers.MainGameEnventHandler(new_game())

        return None
