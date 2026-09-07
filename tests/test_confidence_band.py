from pipeline import map_confidence_to_display_band


def test_low_confidence_maps_into_band():
    assert map_confidence_to_display_band(0.62) == 0.824


def test_high_confidence_caps_at_ninety():
    assert map_confidence_to_display_band(0.98) == 0.896


def test_mid_confidence_near_center():
    assert map_confidence_to_display_band(0.75) == 0.85
