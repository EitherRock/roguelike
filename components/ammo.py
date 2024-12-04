from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import actions
import colors
import components.ai
import components.inventory
from enums.damage_types import DamageType
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
)

if TYPE_CHECKING:
    from entity import Actor, Item


class Ammo(BaseComponent):
    parent: Item

