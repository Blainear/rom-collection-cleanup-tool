"""Tests for rom_cleanup module."""

from pathlib import Path

import rom_cleanup


def _create_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("")


def test_scan_roms_groups_by_canonical_name(tmp_path, monkeypatch):
    """scan_roms should group ROMs by canonical name."""
    monkeypatch.setattr(rom_cleanup, "CACHE_FILE", tmp_path / "cache.json")
    monkeypatch.setattr(rom_cleanup, "GAME_CACHE", {})

    _create_file(tmp_path / "SuperGame (USA).nes")
    _create_file(tmp_path / "SuperGame (Japan).nes")

    groups = rom_cleanup.scan_roms(str(tmp_path), {".nes"})

    assert "SuperGame" in groups
    entries = groups["SuperGame"]
    assert len(entries) == 2
    regions = {region for _, region, _ in entries}
    assert regions == {"usa", "japan"}


def test_find_duplicates_to_remove(tmp_path, monkeypatch):
    """find_duplicates_to_remove should prefer USA ROMs."""
    monkeypatch.setattr(rom_cleanup, "CACHE_FILE", tmp_path / "cache.json")
    monkeypatch.setattr(rom_cleanup, "GAME_CACHE", {})

    usa = tmp_path / "Game (USA).nes"
    jap = tmp_path / "Game (Japan).nes"
    _create_file(usa)
    _create_file(jap)

    groups = rom_cleanup.scan_roms(str(tmp_path), {".nes"})
    to_remove = rom_cleanup.find_duplicates_to_remove(groups)

    assert to_remove == [jap]


def test_find_duplicates_skip_to_delete(tmp_path, monkeypatch):
    """ROMs in to_delete folder without counterparts should be ignored."""
    monkeypatch.setattr(rom_cleanup, "CACHE_FILE", tmp_path / "cache.json")
    monkeypatch.setattr(rom_cleanup, "GAME_CACHE", {})

    _create_file(tmp_path / "Game (USA).nes")
    _create_file(tmp_path / "Game (Japan).nes")
    _create_file(tmp_path / "to_delete" / "OldGame (Japan).nes")

    groups = rom_cleanup.scan_roms(str(tmp_path), {".nes"})
    to_remove = rom_cleanup.find_duplicates_to_remove(groups)

    assert (tmp_path / "Game (Japan).nes") in to_remove
    assert all("to_delete" not in p.parts for p in to_remove)
