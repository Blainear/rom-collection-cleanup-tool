"""Tests for ROM utilities module."""

from rom_utils import get_base_name, get_region


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
