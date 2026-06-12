import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_import_settings():
    import settings
    assert settings.CAMERA_INDEX is not None


def test_import_gestures():
    import gestures
    assert hasattr(gestures, "pinch")