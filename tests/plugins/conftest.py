import pytest


def pytest_generate_tests(metafunc):
    if "platform_" in metafunc.fixturenames:
        metafunc.parametrize(
            "platform_", ["pi_platform", "native_platform"], indirect=True
        )


@pytest.fixture
def platform_(request, monkeypatch):
    if request.param == "pi_platform":
        import mindref.domain.plugin_settings

        monkeypatch.setattr(
            mindref.domain.plugin_settings, "_has_rpi_backlight", lambda: True
        )
        monkeypatch.setattr(
            mindref.domain.plugin_settings, "_SETTINGS_PLUGIN_DATA", None
        )
        return True

    else:
        import mindref.domain.plugin_settings

        monkeypatch.setattr(
            mindref.domain.plugin_settings, "_has_rpi_backlight", lambda: False
        )
        monkeypatch.setattr(
            mindref.domain.plugin_settings, "_SETTINGS_PLUGIN_DATA", None
        )
        return False
