from kivy import platform

if platform == "android":
    from .brokered.android.android_file_system import AndroidFileSystemAdapter

    FileManager = AndroidFileSystemAdapter
else:
    from .direct_file_system import DirectFileSystemAdapter

    FileManager = DirectFileSystemAdapter

__all__ = ["FileManager"]
