import json
from itertools import chain


def test_pi_ss_env_detect(platform_):
    """
    Given environment
    Load KVNoteAFly
    Check that plugin option is enabled / disabled correctly
    """
    expected = platform_
    from kvnoteafly.domain.plugin_settings import SETTINGS_PLUGIN_DATA

    data = json.loads(SETTINGS_PLUGIN_DATA)
    assert isinstance(data, list)
    if expected:
        assert any((x.get("title") == "ScreenSaver") for x in data)
    else:
        assert all((x.get("title") != "ScreenSaver") for x in data)
