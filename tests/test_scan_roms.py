import rom_cleanup


def test_scan_roms_ignores_to_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(rom_cleanup, "CACHE_FILE", tmp_path / "cache.json")

    rom_file = tmp_path / "game.nes"
    rom_file.write_text("data")

    to_delete_dir = tmp_path / "to_delete"
    to_delete_dir.mkdir()
    (to_delete_dir / "bad.nes").write_text("data")

    rom_groups = rom_cleanup.scan_roms(str(tmp_path), {".nes"})

    rom_paths = [fp for group in rom_groups.values() for fp, _, _ in group]
    assert rom_file in rom_paths
    assert all("to_delete" not in fp.parts for fp in rom_paths)
    assert len(rom_paths) == 1
