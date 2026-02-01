"""
Gem System for Pirates of the Lost Seas.

Defines gem types, values, and placement logic.
"""

import random

# Gem names indexed by type (0-17)
GEM_NAMES: dict[int, str] = {
    0: "opal",
    1: "ruby",
    2: "garnet",
    3: "diamond",
    4: "sapphire",
    5: "emerald",
    6: "gem of the palace",
    7: "large plastic gem (what is this doing here!)",
    8: "awesome blue bastardstone",
    9: "amethyst",
    10: "golden ring",
    11: "awesome red ppulpstone",
    12: "awesome red gorestone",
    13: "moonstone",
    14: "lapis lazuli",
    15: "amber",
    16: "citrine",
    17: "definitely not cursed black pearl (tm)",
}

# Gem types with special values (2 points)
RARE_GEMS = {6, 8, 11, 12}

# Legendary gem (3 points)
LEGENDARY_GEM = 17

# Total number of gem types
TOTAL_GEM_TYPES = 18


def get_gem_value(gem_type: int) -> int:
    """
    Get the point value of a gem by its type index.

    Args:
        gem_type: The gem type (0-17)

    Returns:
        The point value (1, 2, or 3)
    """
    if gem_type == LEGENDARY_GEM:
        return 3
    if gem_type in RARE_GEMS:
        return 2
    return 1


def get_gem_name(gem_type: int) -> str:
    """
    Get the name of a gem by its type index.

    Args:
        gem_type: The gem type (0-17)

    Returns:
        The gem name, or "unknown gem" if invalid
    """
    return GEM_NAMES.get(gem_type, "unknown gem")


def calculate_score_from_gems(gems: list[int]) -> int:
    """
    Calculate total score from a list of gem types.

    Args:
        gems: List of gem type indices

    Returns:
        Total score
    """
    if not gems:
        return 0
    return sum(get_gem_value(gem) for gem in gems)


def place_gems(map_size: int = 40) -> dict[int, int]:
    """
    Place all gems randomly across the map.

    Args:
        map_size: Total number of tiles (default 40)

    Returns:
        Dictionary mapping position -> gem_type (-1 if no gem)
    """
    gem_positions: dict[int, int] = {}

    # Initialize all positions with no gems
    for i in range(1, map_size + 1):
        gem_positions[i] = -1

    # Place all 18 gems randomly
    available_positions = list(range(1, map_size + 1))
    random.shuffle(available_positions)

    for gem_type in range(TOTAL_GEM_TYPES):
        pos = available_positions.pop()
        gem_positions[pos] = gem_type

    return gem_positions


def format_gem_list(gems: list[int]) -> str:
    """
    Format a list of gems as a comma-separated string.

    Args:
        gems: List of gem type indices

    Returns:
        Formatted string like "ruby, diamond, emerald"
    """
    if not gems:
        return "no gems"
    return ", ".join(get_gem_name(gem) for gem in gems)
