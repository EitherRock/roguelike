import sys
import os

def format_item_name(name: str, quantity: int) -> str:
    """Returns a formatted name based on the quantity."""
    if quantity == 1:
        return name
    elif name.endswith("y") and not name.endswith(("ay", "ey", "oy", "uy")):
        return name[:-1] + "ies"  # e.g., berry → berries
    elif name.endswith("f"):
        return name[:-1] + "ves"  # e.g., leaf → leaves
    elif name.endswith("fe"):
        return name[:-2] + "ves"  # e.g., knife → knives
    else:
        return name + "s"  # Default plural


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)