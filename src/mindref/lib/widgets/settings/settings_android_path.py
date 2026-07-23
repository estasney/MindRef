from kivy.logger import Logger
from kivy.uix.settings import SettingString


class SettingsAndroidPath(SettingString):
    """
    This setting corresponds to the Android external storage path.
    In Android, we cannot use a FilePicker to select a path,
    we have to use JNI and Android's Document API to get the path.
    Then, we need to get persistent access to the path
    """

    def on_panel(self, instance, value):
        if value is None:
            return
        self.fbind("on_release", self._create_popup)

    def _create_popup(self, *args):
        """
        Here we override to prevent the default behavior of opening a file picker.
        Instead, we'll offload the path selection to the Android system.
        """
        from mindref.lib import get_app
        from mindref.lib.adapters.brokered.android.android_file_system import (
            AndroidFileSystemAdapter,
        )

        app = get_app()
        if not app.platform_android:
            raise RuntimeError("This setting is only available on Android platform.")
        if not isinstance(app.fs, AndroidFileSystemAdapter):
            raise TypeError("This setting requires an AndroidFileSystemAdapter.")

        app.fs.prompt_for_external_storage(self._external_path_callback)

    def _external_path_callback(self, value):
        Logger.info(f"SettingsAndroidPath: External storage path selected - {value}")
        self.value = value
