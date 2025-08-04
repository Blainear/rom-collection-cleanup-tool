import os
from collections import defaultdict
from pathlib import Path

import pytest

from rom_cleanup import find_duplicates_to_remove
from rom_utils import get_region, get_base_name


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("Super Mario (USA).nes", "usa"),
        ("Super Mario (J).nes", "japan"),
        ("Super Mario [E].nes", "europe"),
        ("Super Mario (W).nes", "world"),
        ("Super Mario.nes", "unknown"),
    ],
)
def test_get_region(filename, expected):
    assert get_region(filename) == expected


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("Super Mario Bros. (USA).zip", "Super Mario Bros."),
        ("Game (Japan) (Rev 2).nes", "Game"),
        ("Another Game [J] (v1.0).snes", "Another Game"),
        ("Game - 1 (USA).zip", "Game"),
    ],
)
def test_get_base_name(filename, expected):
    assert get_base_name(filename) == expected


def build_rom_groups(tmp_path, filenames):
    rom_groups = defaultdict(list)
    for name in filenames:
        file_path = tmp_path / name
        file_path.touch()
        region = get_region(name)
        base_name = get_base_name(name)
        rom_groups[base_name].append((file_path, region, name))
    return rom_groups


def test_find_duplicates_japan_and_usa(tmp_path):
    filenames = ["Game (USA).nes", "Game (J).nes"]
    rom_groups = build_rom_groups(tmp_path, filenames)
    to_remove = find_duplicates_to_remove(rom_groups)
    assert to_remove == [tmp_path / "Game (J).nes"]


def test_find_duplicates_japan_and_europe(tmp_path):
    filenames = ["Game (E).nes", "Game (J).nes"]
    rom_groups = build_rom_groups(tmp_path, filenames)
    to_remove = find_duplicates_to_remove(rom_groups)
    assert to_remove == []


def test_find_duplicates_only_japan(tmp_path):
    filenames = ["Game (J).nes"]
    rom_groups = build_rom_groups(tmp_path, filenames)
    to_remove = find_duplicates_to_remove(rom_groups)
    assert to_remove == []


# Additional comprehensive test cases
@pytest.mark.parametrize(
    "filename,expected",
    [
        ("Super Mario Bros. (USA) (Rev 1).nes", "Super Mario Bros."),
        ("Game (USA) [!].zip", "Game"),  # GoodRoms convention
        ("Another Game (USA) (Beta).snes", "Another Game"),
        ("Test Game (World) (Proto).gb", "Test Game"),
        ("Final Game (Europe) (En,Fr,De).gba", "Final Game"),
        ("Game - 1 (USA).zip", "Game"),
        ("Game v2.0 (Japan).nes", "Game"),
        ("Game Version 3 (Europe).snes", "Game"),
    ],
)
def test_get_base_name_edge_cases(filename, expected):
    assert get_base_name(filename) == expected


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("Game [W].nes", "world"),
        ("Game [World].snes", "world"),
        ("Game (JPN).gba", "japan"),
        ("Game [US].md", "usa"),
        ("Game [EUR].iso", "europe"),
        ("Game.nes", "unknown"),  # No region tag
    ],
)
def test_get_region_extended(filename, expected):
    assert get_region(filename) == expected


def test_get_base_name_empty_input():
    """Test handling of empty or invalid input."""
    assert get_base_name("") == ""
    assert get_base_name(None) == ""


def test_get_region_empty_input():
    """Test handling of empty or invalid input."""
    assert get_region("") == "unknown"
    assert get_region(None) == "unknown"


def test_find_duplicates_multiple_regions(tmp_path):
    """Test with multiple regions including world releases."""
    filenames = ["Game (USA).nes", "Game (J).nes", "Game (E).nes", "Game (W).nes"]
    rom_groups = build_rom_groups(tmp_path, filenames)
    to_remove = find_duplicates_to_remove(rom_groups)
    # Should remove Japanese version when USA exists
    assert to_remove == [tmp_path / "Game (J).nes"]


def test_find_duplicates_japan_europe_world(tmp_path):
    """Test Japan + Europe + World versions (no USA)."""
    filenames = ["Game (J).nes", "Game (E).nes", "Game (W).nes"]
    rom_groups = build_rom_groups(tmp_path, filenames)
    to_remove = find_duplicates_to_remove(rom_groups)
    # Should keep all when no USA version exists
    assert to_remove == []


def test_find_duplicates_different_games(tmp_path):
    """Test that different games are not confused as duplicates."""
    filenames = ["Mario (USA).nes", "Zelda (J).nes", "Sonic (E).nes"]
    rom_groups = build_rom_groups(tmp_path, filenames)
    to_remove = find_duplicates_to_remove(rom_groups)
    # Should not remove anything as these are different games
    assert to_remove == []
