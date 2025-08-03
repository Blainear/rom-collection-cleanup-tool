import os
from collections import defaultdict
from pathlib import Path

import pytest

from rom_cleanup import get_region, get_base_name, find_duplicates_to_remove


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
