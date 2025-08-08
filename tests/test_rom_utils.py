"""Tests for ROM utilities module."""

from rom_utils import (
    get_base_name,
    get_region,
    get_version_info,
    is_multi_disc_game,
)


class TestGetRegion:
    """Test the get_region function."""

    def test_usa_region(self):
        """Test USA region detection."""
        assert get_region("Super Mario Bros. (USA).nes") == "usa"
        assert get_region("Game [U].snes") == "usa"
        assert get_region("Title (US).md") == "usa"

    def test_europe_region(self):
        """Test Europe region detection."""
        assert get_region("Game (Europe).gba") == "europe"
        assert get_region("Title [E].nes") == "europe"
        assert get_region("Game [EUR].iso") == "europe"

    def test_japan_region(self):
        """Test Japan region detection."""
        assert get_region("Game (Japan).snes") == "japan"
        assert get_region("Title [J].nes") == "japan"
        assert get_region("Game (JPN).gba") == "japan"

    def test_world_region(self):
        """Test World region detection."""
        assert get_region("Game (World).nes") == "world"
        assert get_region("Title [W].snes") == "world"

    def test_unknown_region(self):
        """Test unknown region detection."""
        assert get_region("Game.nes") == "unknown"
        assert get_region("Title - No Region.snes") == "unknown"


class TestGetBaseName:
    """Test the get_base_name function."""

    def test_basic_extraction(self):
        """Test basic name extraction."""
        assert get_base_name("Super Mario Bros. (USA).nes") == "Super Mario Bros."
        assert get_base_name("Game [Europe].snes") == "Game"

    def test_revision_removal(self):
        """Test revision and version removal."""
        assert get_base_name("Game (USA) (Rev 1).nes") == "Game"
        assert get_base_name("Title v2.0 (Japan).snes") == "Title"
        assert get_base_name("Game Version 3 (Europe).gba") == "Game"

    def test_special_characters(self):
        """Test handling of special characters."""
        assert get_base_name("Game - 1 (USA).zip") == "Game"
        assert get_base_name("Game (USA) [!].snes") == "Game"

    def test_empty_input(self):
        """Test empty input handling."""
        assert get_base_name("") == ""
        assert get_base_name(None) == ""


class TestIntegration:
    """Integration tests for ROM utilities."""

    def test_combined_functionality(self):
        """Test region and base name extraction together."""
        filename = "Super Mario Bros. 3 (USA) (Rev 1).nes"

        base_name = get_base_name(filename)
        region = get_region(filename)

        assert base_name == "Super Mario Bros. 3"
        assert region == "usa"

    def test_edge_cases(self):
        """Test edge cases."""
        # Multiple parentheses
        filename = "Game (Proto) (USA) (Beta).nes"
        assert get_base_name(filename) == "Game"
        assert get_region(filename) == "usa"

        # No extension
        filename = "Game (Europe)"
        assert get_base_name(filename) == "Game"
        assert get_region(filename) == "europe"


class TestGetVersionInfo:
    """Tests for get_version_info."""

    def test_revision_and_edition(self):
        """Extract both revision and edition information."""
        filename = "Game (Rev 1) (Limited Edition).nes"
        assert get_version_info(filename) == "Rev 1 Limited Edition"

    def test_multiple_revisions(self):
        """Handle multiple revision tags without duplicates."""
        filename = "Game (Rev 1) (Rev 2) (Demo).snes"
        assert get_version_info(filename) == "Rev 1 Rev 2 Demo"

    def test_invalid_input(self):
        """Return empty string for invalid input."""
        assert get_version_info("") == ""
        assert get_version_info(None) == ""


class TestIsMultiDiscGame:
    """Tests for is_multi_disc_game."""

    def test_positive_detection(self):
        """Detect multi-disc games when most files have disc numbers."""
        files = [
            "Game (Disc 1).iso",
            "Game (Disc 2).iso",
        ]
        assert is_multi_disc_game(files)

    def test_negative_detection(self):
        """Return False when disc markers are insufficient."""
        files = [
            "Game (Disc 1).iso",
            "Game Bonus Content.iso",
        ]
        assert not is_multi_disc_game(files)

    def test_three_file_threshold(self):
        """With three files, at least two must be discs to trigger detection."""
        files = [
            "Game (Disc 1).iso",
            "Game (Disc 2).iso",
            "Game Manual.txt",
        ]
        assert is_multi_disc_game(files)
