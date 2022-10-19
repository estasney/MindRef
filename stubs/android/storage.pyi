from typing import Optional

def app_storage_path() -> str:
    """Locate the built-in device storage used for this app only.

    This storage is APP-SPECIFIC, and not visible to other apps.
    It will be wiped when your app is uninstalled.

    Returns directory path to storage.
    """
    ...

def primary_external_storage_path() -> str:
    """Locate the built-in device storage that user can see via file browser.
    Often found at: /sdcard/

    This is storage is SHARED, and visible to other apps and the user.
    It will remain untouched when your app is uninstalled.

    Returns directory path to storage.

    WARNING: You need storage permissions to access this storage.
    """
    ...

def secondary_external_storage_path() -> Optional[str]:
    """Locate the external SD Card storage, which may not be present.
    Often found at: /sdcard/External_SD/

    This storage is SHARED, visible to other apps, and may not be
    be available if the user didn't put in an external SD card.
    It will remain untouched when your app is uninstalled.

    Returns None if not found, otherwise path to storage.

    WARNING: You need storage permissions to access this storage.
             If it is not writable and presents as empty even with
             permissions, then the external sd card may not be present.
    """
    ...
