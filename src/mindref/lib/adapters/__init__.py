from kivy import platform

if platform == "android":
    from mindref.lib.adapters.brokered.android.android_file_system import (
        AndroidFileSystemAdapter,
    )

    FileManager = AndroidFileSystemAdapter
else:
    from mindref.lib.adapters.direct_file_system import DirectFileSystemAdapter

    FileManager = DirectFileSystemAdapter

__all__ = ["FileManager"]
