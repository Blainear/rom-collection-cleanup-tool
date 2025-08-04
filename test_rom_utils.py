import pytest
from rom_utils import get_region, get_base_name


def test_get_region_returns_expected_region():
    """get_region returns region string based on filename."""
    assert get_region("Super Mario Bros (USA).nes") == "usa"


def test_get_base_name_strips_metadata():
    """get_base_name removes region and revision info from filename."""
    assert get_base_name("Super Mario Bros (USA) (Rev 1).nes") == "Super Mario Bros"
