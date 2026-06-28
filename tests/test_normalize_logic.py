from utils import normalize_artist, normalize_track_name

def test_normalize_artist():
    assert normalize_artist("KiD CuDi!  ") == "kid cudi"
    assert normalize_artist("Kid Cudi") == "kid cudi"
    assert normalize_artist(None) == "unknown artist"
    assert normalize_artist("¡MAYDAY!") == "mayday"

def test_remastered_matches_original():
    assert normalize_track_name("Thirteen (Remastered)") == normalize_track_name("Thirteen")

def test_featured_matches_original():
    assert normalize_track_name("Thirteen (feat. Johnny Cash)") == normalize_track_name("Thirteen")

def test_explicit_matches_original():
    assert normalize_track_name("Thirteen [Explicit]") == normalize_track_name("Thirteen")