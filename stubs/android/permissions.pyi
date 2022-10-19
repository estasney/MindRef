from typing import Callable, Literal, Optional

PERMISSIONS = Literal[
    "android.permission.ACCEPT_HANDOVER",
    "android.permission.ACCESS_BACKGROUND_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_LOCATION_EXTRA_COMMANDS",
    "android.permission.ACCESS_NETWORK_STATE",
    "android.permission.ACCESS_NOTIFICATION_POLICY",
    "android.permission.ACCESS_WIFI_STATE",
    "com.android.voicemail.permission.ADD_VOICEMAIL",
    "android.permission.ANSWER_PHONE_CALLS",
    "android.permission.BATTERY_STATS",
    "android.permission.BIND_ACCESSIBILITY_SERVICE",
    "android.permission.BIND_AUTOFILL_SERVICE",
    "android.permission.BIND_CARRIER_MESSAGING_SERVICE",
    "android.permission.BIND_CARRIER_SERVICES",
    "android.permission.BIND_CHOOSER_TARGET_SERVICE",
    "android.permission.BIND_CONDITION_PROVIDER_SERVICE",
    "android.permission.BIND_DEVICE_ADMIN",
    "android.permission.BIND_DREAM_SERVICE",
    "android.permission.BIND_INCALL_SERVICE",
    "android.permission.BIND_INPUT_METHOD",
    "android.permission.BIND_MIDI_DEVICE_SERVICE",
    "android.permission.BIND_NFC_SERVICE",
    "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE",
    "android.permission.BIND_PRINT_SERVICE",
    "android.permission.BIND_QUICK_SETTINGS_TILE",
    "android.permission.BIND_REMOTEVIEWS",
    "android.permission.BIND_SCREENING_SERVICE",
    "android.permission.BIND_TELECOM_CONNECTION_SERVICE",
    "android.permission.BIND_TEXT_SERVICE",
    "android.permission.BIND_TV_INPUT",
    "android.permission.BIND_VISUAL_VOICEMAIL_SERVICE",
    "android.permission.BIND_VOICE_INTERACTION",
    "android.permission.BIND_VPN_SERVICE",
    "android.permission.BIND_VR_LISTENER_SERVICE",
    "android.permission.BIND_WALLPAPER",
    "android.permission.BLUETOOTH",
    "android.permission.BLUETOOTH_ADVERTISE",
    "android.permission.BLUETOOTH_CONNECT",
    "android.permission.BLUETOOTH_SCAN",
    "android.permission.BLUETOOTH_ADMIN",
    "android.permission.BODY_SENSORS",
    "android.permission.BROADCAST_PACKAGE_REMOVED",
    "android.permission.BROADCAST_STICKY",
    "android.permission.CALL_PHONE",
    "android.permission.CALL_PRIVILEGED",
    "android.permission.CAMERA",
    "android.permission.CAPTURE_AUDIO_OUTPUT",
    "android.permission.CAPTURE_SECURE_VIDEO_OUTPUT",
    "android.permission.CAPTURE_VIDEO_OUTPUT",
    "android.permission.CHANGE_COMPONENT_ENABLED_STATE",
    "android.permission.CHANGE_CONFIGURATION",
    "android.permission.CHANGE_NETWORK_STATE",
    "android.permission.CHANGE_WIFI_MULTICAST_STATE",
    "android.permission.CHANGE_WIFI_STATE",
    "android.permission.CLEAR_APP_CACHE",
    "android.permission.CONTROL_LOCATION_UPDATES",
    "android.permission.DELETE_CACHE_FILES",
    "android.permission.DELETE_PACKAGES",
    "android.permission.DIAGNOSTIC",
    "android.permission.DISABLE_KEYGUARD",
    "android.permission.DUMP",
    "android.permission.EXPAND_STATUS_BAR",
    "android.permission.FACTORY_TEST",
    "android.permission.FOREGROUND_SERVICE",
    "android.permission.GET_ACCOUNTS",
    "android.permission.GET_ACCOUNTS_PRIVILEGED",
    "android.permission.GET_PACKAGE_SIZE",
    "android.permission.GET_TASKS",
    "android.permission.GLOBAL_SEARCH",
    "android.permission.INSTALL_LOCATION_PROVIDER",
    "android.permission.INSTALL_PACKAGES",
    "com.android.launcher.permission.INSTALL_SHORTCUT",
    "android.permission.INSTANT_APP_FOREGROUND_SERVICE",
    "android.permission.INTERNET",
    "android.permission.KILL_BACKGROUND_PROCESSES",
    "android.permission.LOCATION_HARDWARE",
    "android.permission.MANAGE_DOCUMENTS",
    "android.permission.MANAGE_OWN_CALLS",
    "android.permission.MASTER_CLEAR",
    "android.permission.MEDIA_CONTENT_CONTROL",
    "android.permission.MODIFY_AUDIO_SETTINGS",
    "android.permission.MODIFY_PHONE_STATE",
    "android.permission.MOUNT_FORMAT_FILESYSTEMS",
    "android.permission.MOUNT_UNMOUNT_FILESYSTEMS",
    "android.permission.NEARBY_WIFI_DEVICES",
    "android.permission.NFC",
    "android.permission.NFC_TRANSACTION_EVENT",
    "android.permission.PACKAGE_USAGE_STATS",
    "android.permission.PERSISTENT_ACTIVITY",
    "android.permission.POST_NOTIFICATIONS",
    "android.permission.PROCESS_OUTGOING_CALLS",
    "android.permission.READ_CALENDAR",
    "android.permission.READ_CALL_LOG",
    "android.permission.READ_CONTACTS",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.READ_FRAME_BUFFER",
    "android.permission.READ_INPUT_STATE",
    "android.permission.READ_LOGS",
    "android.permission.READ_MEDIA_AUDIO",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.READ_MEDIA_VIDEO",
    "android.permission.READ_PHONE_NUMBERS",
    "android.permission.READ_PHONE_STATE",
    "android.permission.READ_SMS",
    "android.permission.READ_SYNC_SETTINGS",
    "android.permission.READ_SYNC_STATS",
    "com.android.voicemail.permission.READ_VOICEMAIL",
    "android.permission.REBOOT",
    "android.permission.RECEIVE_BOOT_COMPLETED",
    "android.permission.RECEIVE_MMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.RECEIVE_WAP_PUSH",
    "android.permission.RECORD_AUDIO",
    "android.permission.REORDER_TASKS",
    "android.permission.REQUEST_COMPANION_RUN_IN_BACKGROUND",
    "android.permission.REQUEST_COMPANION_USE_DATA_IN_BACKGROUND",
    "android.permission.REQUEST_DELETE_PACKAGES",
    "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS",
    "android.permission.REQUEST_INSTALL_PACKAGES",
    "android.permission.RESTART_PACKAGES",
    "android.permission.SEND_RESPOND_VIA_MESSAGE",
    "android.permission.SEND_SMS",
    "com.android.alarm.permission.SET_ALARM",
    "android.permission.SET_ALWAYS_FINISH",
    "android.permission.SET_ANIMATION_SCALE",
    "android.permission.SET_DEBUG_APP",
    "android.permission.SET_PREFERRED_APPLICATIONS",
    "android.permission.SET_PROCESS_LIMIT",
    "android.permission.SET_TIME",
    "android.permission.SET_TIME_ZONE",
    "android.permission.SET_WALLPAPER",
    "android.permission.SET_WALLPAPER_HINTS",
    "android.permission.SIGNAL_PERSISTENT_PROCESSES",
    "android.permission.STATUS_BAR",
    "android.permission.SYSTEM_ALERT_WINDOW",
    "android.permission.TRANSMIT_IR",
    "com.android.launcher.permission.UNINSTALL_SHORTCUT",
    "android.permission.UPDATE_DEVICE_STATS",
    "android.permission.USE_BIOMETRIC",
    "android.permission.USE_FINGERPRINT",
    "android.permission.USE_SIP",
    "android.permission.VIBRATE",
    "android.permission.WAKE_LOCK",
    "android.permission.WRITE_APN_SETTINGS",
    "android.permission.WRITE_CALENDAR",
    "android.permission.WRITE_CALL_LOG",
    "android.permission.WRITE_CONTACTS",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.WRITE_GSERVICES",
    "android.permission.WRITE_SECURE_SETTINGS",
    "android.permission.WRITE_SETTINGS",
    "android.permission.WRITE_SYNC_SETTINGS",
    "com.android.voicemail.permission.WRITE_VOICEMAIL",
]

class Permission:
    ACCEPT_HANDOVER: Literal["android.permission.ACCEPT_HANDOVER"]
    ACCESS_BACKGROUND_LOCATION: Literal["android.permission.ACCESS_BACKGROUND_LOCATION"]
    ACCESS_COARSE_LOCATION: Literal["android.permission.ACCESS_COARSE_LOCATION"]
    ACCESS_FINE_LOCATION: Literal["android.permission.ACCESS_FINE_LOCATION"]
    ACCESS_LOCATION_EXTRA_COMMANDS: Literal[
        "android.permission.ACCESS_LOCATION_EXTRA_COMMANDS"
    ]

    ACCESS_NETWORK_STATE: Literal["android.permission.ACCESS_NETWORK_STATE"]
    ACCESS_NOTIFICATION_POLICY: Literal["android.permission.ACCESS_NOTIFICATION_POLICY"]

    ACCESS_WIFI_STATE: Literal["android.permission.ACCESS_WIFI_STATE"]
    ADD_VOICEMAIL: Literal["com.android.voicemail.permission.ADD_VOICEMAIL"]
    ANSWER_PHONE_CALLS: Literal["android.permission.ANSWER_PHONE_CALLS"]
    BATTERY_STATS: Literal["android.permission.BATTERY_STATS"]
    BIND_ACCESSIBILITY_SERVICE: Literal["android.permission.BIND_ACCESSIBILITY_SERVICE"]

    BIND_AUTOFILL_SERVICE: Literal["android.permission.BIND_AUTOFILL_SERVICE"]
    BIND_CARRIER_MESSAGING_SERVICE: Literal[
        "android.permission.BIND_CARRIER_MESSAGING_SERVICE"
    ]

    BIND_CARRIER_SERVICES: Literal["android.permission.BIND_CARRIER_SERVICES"]

    BIND_CHOOSER_TARGET_SERVICE: Literal[
        "android.permission.BIND_CHOOSER_TARGET_SERVICE"
    ]

    BIND_CONDITION_PROVIDER_SERVICE: Literal[
        "android.permission.BIND_CONDITION_PROVIDER_SERVICE"
    ]

    BIND_DEVICE_ADMIN: Literal["android.permission.BIND_DEVICE_ADMIN"]
    BIND_DREAM_SERVICE: Literal["android.permission.BIND_DREAM_SERVICE"]
    BIND_INCALL_SERVICE: Literal["android.permission.BIND_INCALL_SERVICE"]
    BIND_INPUT_METHOD: Literal["android.permission.BIND_INPUT_METHOD"]

    BIND_MIDI_DEVICE_SERVICE: Literal["android.permission.BIND_MIDI_DEVICE_SERVICE"]

    BIND_NFC_SERVICE: Literal["android.permission.BIND_NFC_SERVICE"]

    BIND_NOTIFICATION_LISTENER_SERVICE: Literal[
        "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE"
    ]

    BIND_PRINT_SERVICE: Literal["android.permission.BIND_PRINT_SERVICE"]

    BIND_QUICK_SETTINGS_TILE: Literal["android.permission.BIND_QUICK_SETTINGS_TILE"]

    BIND_REMOTEVIEWS: Literal["android.permission.BIND_REMOTEVIEWS"]

    BIND_SCREENING_SERVICE: Literal["android.permission.BIND_SCREENING_SERVICE"]

    BIND_TELECOM_CONNECTION_SERVICE: Literal[
        "android.permission.BIND_TELECOM_CONNECTION_SERVICE"
    ]

    BIND_TEXT_SERVICE: Literal["android.permission.BIND_TEXT_SERVICE"]

    BIND_TV_INPUT: Literal["android.permission.BIND_TV_INPUT"]

    BIND_VISUAL_VOICEMAIL_SERVICE: Literal[
        "android.permission.BIND_VISUAL_VOICEMAIL_SERVICE"
    ]

    BIND_VOICE_INTERACTION: Literal["android.permission.BIND_VOICE_INTERACTION"]

    BIND_VPN_SERVICE: Literal["android.permission.BIND_VPN_SERVICE"]

    BIND_VR_LISTENER_SERVICE: Literal["android.permission.BIND_VR_LISTENER_SERVICE"]

    BIND_WALLPAPER: Literal["android.permission.BIND_WALLPAPER"]

    BLUETOOTH: Literal["android.permission.BLUETOOTH"]

    BLUETOOTH_ADVERTISE: Literal["android.permission.BLUETOOTH_ADVERTISE"]

    BLUETOOTH_CONNECT: Literal["android.permission.BLUETOOTH_CONNECT"]

    BLUETOOTH_SCAN: Literal["android.permission.BLUETOOTH_SCAN"]

    BLUETOOTH_ADMIN: Literal["android.permission.BLUETOOTH_ADMIN"]

    BODY_SENSORS: Literal["android.permission.BODY_SENSORS"]

    BROADCAST_PACKAGE_REMOVED: Literal["android.permission.BROADCAST_PACKAGE_REMOVED"]

    BROADCAST_STICKY: Literal["android.permission.BROADCAST_STICKY"]

    CALL_PHONE: Literal["android.permission.CALL_PHONE"]

    CALL_PRIVILEGED: Literal["android.permission.CALL_PRIVILEGED"]

    CAMERA: Literal["android.permission.CAMERA"]

    CAPTURE_AUDIO_OUTPUT: Literal["android.permission.CAPTURE_AUDIO_OUTPUT"]

    CAPTURE_SECURE_VIDEO_OUTPUT: Literal[
        "android.permission.CAPTURE_SECURE_VIDEO_OUTPUT"
    ]

    CAPTURE_VIDEO_OUTPUT: Literal["android.permission.CAPTURE_VIDEO_OUTPUT"]

    CHANGE_COMPONENT_ENABLED_STATE: Literal[
        "android.permission.CHANGE_COMPONENT_ENABLED_STATE"
    ]

    CHANGE_CONFIGURATION: Literal["android.permission.CHANGE_CONFIGURATION"]

    CHANGE_NETWORK_STATE: Literal["android.permission.CHANGE_NETWORK_STATE"]

    CHANGE_WIFI_MULTICAST_STATE: Literal[
        "android.permission.CHANGE_WIFI_MULTICAST_STATE"
    ]

    CHANGE_WIFI_STATE: Literal["android.permission.CHANGE_WIFI_STATE"]

    CLEAR_APP_CACHE: Literal["android.permission.CLEAR_APP_CACHE"]

    CONTROL_LOCATION_UPDATES: Literal["android.permission.CONTROL_LOCATION_UPDATES"]

    DELETE_CACHE_FILES: Literal["android.permission.DELETE_CACHE_FILES"]

    DELETE_PACKAGES: Literal["android.permission.DELETE_PACKAGES"]

    DIAGNOSTIC: Literal["android.permission.DIAGNOSTIC"]

    DISABLE_KEYGUARD: Literal["android.permission.DISABLE_KEYGUARD"]

    DUMP: Literal["android.permission.DUMP"]

    EXPAND_STATUS_BAR: Literal["android.permission.EXPAND_STATUS_BAR"]

    FACTORY_TEST: Literal["android.permission.FACTORY_TEST"]

    FOREGROUND_SERVICE: Literal["android.permission.FOREGROUND_SERVICE"]

    GET_ACCOUNTS: Literal["android.permission.GET_ACCOUNTS"]

    GET_ACCOUNTS_PRIVILEGED: Literal["android.permission.GET_ACCOUNTS_PRIVILEGED"]

    GET_PACKAGE_SIZE: Literal["android.permission.GET_PACKAGE_SIZE"]

    GET_TASKS: Literal["android.permission.GET_TASKS"]

    GLOBAL_SEARCH: Literal["android.permission.GLOBAL_SEARCH"]

    INSTALL_LOCATION_PROVIDER: Literal["android.permission.INSTALL_LOCATION_PROVIDER"]

    INSTALL_PACKAGES: Literal["android.permission.INSTALL_PACKAGES"]

    INSTALL_SHORTCUT: Literal["com.android.launcher.permission.INSTALL_SHORTCUT"]

    INSTANT_APP_FOREGROUND_SERVICE: Literal[
        "android.permission.INSTANT_APP_FOREGROUND_SERVICE"
    ]

    INTERNET: Literal["android.permission.INTERNET"]

    KILL_BACKGROUND_PROCESSES: Literal["android.permission.KILL_BACKGROUND_PROCESSES"]

    LOCATION_HARDWARE: Literal["android.permission.LOCATION_HARDWARE"]

    MANAGE_DOCUMENTS: Literal["android.permission.MANAGE_DOCUMENTS"]

    MANAGE_OWN_CALLS: Literal["android.permission.MANAGE_OWN_CALLS"]

    MASTER_CLEAR: Literal["android.permission.MASTER_CLEAR"]

    MEDIA_CONTENT_CONTROL: Literal["android.permission.MEDIA_CONTENT_CONTROL"]

    MODIFY_AUDIO_SETTINGS: Literal["android.permission.MODIFY_AUDIO_SETTINGS"]

    MODIFY_PHONE_STATE: Literal["android.permission.MODIFY_PHONE_STATE"]

    MOUNT_FORMAT_FILESYSTEMS: Literal["android.permission.MOUNT_FORMAT_FILESYSTEMS"]

    MOUNT_UNMOUNT_FILESYSTEMS: Literal["android.permission.MOUNT_UNMOUNT_FILESYSTEMS"]

    NEARBY_WIFI_DEVICES: Literal["android.permission.NEARBY_WIFI_DEVICES"]

    NFC: Literal["android.permission.NFC"]

    NFC_TRANSACTION_EVENT: Literal["android.permission.NFC_TRANSACTION_EVENT"]

    PACKAGE_USAGE_STATS: Literal["android.permission.PACKAGE_USAGE_STATS"]

    PERSISTENT_ACTIVITY: Literal["android.permission.PERSISTENT_ACTIVITY"]

    POST_NOTIFICATIONS: Literal["android.permission.POST_NOTIFICATIONS"]

    PROCESS_OUTGOING_CALLS: Literal["android.permission.PROCESS_OUTGOING_CALLS"]

    READ_CALENDAR: Literal["android.permission.READ_CALENDAR"]

    READ_CALL_LOG: Literal["android.permission.READ_CALL_LOG"]

    READ_CONTACTS: Literal["android.permission.READ_CONTACTS"]

    READ_EXTERNAL_STORAGE: Literal["android.permission.READ_EXTERNAL_STORAGE"]

    READ_FRAME_BUFFER: Literal["android.permission.READ_FRAME_BUFFER"]

    READ_INPUT_STATE: Literal["android.permission.READ_INPUT_STATE"]

    READ_LOGS: Literal["android.permission.READ_LOGS"]

    READ_MEDIA_AUDIO: Literal["android.permission.READ_MEDIA_AUDIO"]

    READ_MEDIA_IMAGES: Literal["android.permission.READ_MEDIA_IMAGES"]

    READ_MEDIA_VIDEO: Literal["android.permission.READ_MEDIA_VIDEO"]

    READ_PHONE_NUMBERS: Literal["android.permission.READ_PHONE_NUMBERS"]

    READ_PHONE_STATE: Literal["android.permission.READ_PHONE_STATE"]

    READ_SMS: Literal["android.permission.READ_SMS"]

    READ_SYNC_SETTINGS: Literal["android.permission.READ_SYNC_SETTINGS"]

    READ_SYNC_STATS: Literal["android.permission.READ_SYNC_STATS"]

    READ_VOICEMAIL: Literal["com.android.voicemail.permission.READ_VOICEMAIL"]

    REBOOT: Literal["android.permission.REBOOT"]

    RECEIVE_BOOT_COMPLETED: Literal["android.permission.RECEIVE_BOOT_COMPLETED"]

    RECEIVE_MMS: Literal["android.permission.RECEIVE_MMS"]

    RECEIVE_SMS: Literal["android.permission.RECEIVE_SMS"]

    RECEIVE_WAP_PUSH: Literal["android.permission.RECEIVE_WAP_PUSH"]

    RECORD_AUDIO: Literal["android.permission.RECORD_AUDIO"]

    REORDER_TASKS: Literal["android.permission.REORDER_TASKS"]

    REQUEST_COMPANION_RUN_IN_BACKGROUND: Literal[
        "android.permission.REQUEST_COMPANION_RUN_IN_BACKGROUND"
    ]

    REQUEST_COMPANION_USE_DATA_IN_BACKGROUND: Literal[
        "android.permission.REQUEST_COMPANION_USE_DATA_IN_BACKGROUND"
    ]

    REQUEST_DELETE_PACKAGES: Literal["android.permission.REQUEST_DELETE_PACKAGES"]

    REQUEST_IGNORE_BATTERY_OPTIMIZATIONS: Literal[
        "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS"
    ]

    REQUEST_INSTALL_PACKAGES: Literal["android.permission.REQUEST_INSTALL_PACKAGES"]

    RESTART_PACKAGES: Literal["android.permission.RESTART_PACKAGES"]

    SEND_RESPOND_VIA_MESSAGE: Literal["android.permission.SEND_RESPOND_VIA_MESSAGE"]

    SEND_SMS: Literal["android.permission.SEND_SMS"]

    SET_ALARM: Literal["com.android.alarm.permission.SET_ALARM"]

    SET_ALWAYS_FINISH: Literal["android.permission.SET_ALWAYS_FINISH"]

    SET_ANIMATION_SCALE: Literal["android.permission.SET_ANIMATION_SCALE"]

    SET_DEBUG_APP: Literal["android.permission.SET_DEBUG_APP"]

    SET_PREFERRED_APPLICATIONS: Literal["android.permission.SET_PREFERRED_APPLICATIONS"]

    SET_PROCESS_LIMIT: Literal["android.permission.SET_PROCESS_LIMIT"]

    SET_TIME: Literal["android.permission.SET_TIME"]

    SET_TIME_ZONE: Literal["android.permission.SET_TIME_ZONE"]

    SET_WALLPAPER: Literal["android.permission.SET_WALLPAPER"]

    SET_WALLPAPER_HINTS: Literal["android.permission.SET_WALLPAPER_HINTS"]

    SIGNAL_PERSISTENT_PROCESSES: Literal[
        "android.permission.SIGNAL_PERSISTENT_PROCESSES"
    ]

    STATUS_BAR: Literal["android.permission.STATUS_BAR"]

    SYSTEM_ALERT_WINDOW: Literal["android.permission.SYSTEM_ALERT_WINDOW"]

    TRANSMIT_IR: Literal["android.permission.TRANSMIT_IR"]

    UNINSTALL_SHORTCUT: Literal["com.android.launcher.permission.UNINSTALL_SHORTCUT"]

    UPDATE_DEVICE_STATS: Literal["android.permission.UPDATE_DEVICE_STATS"]

    USE_BIOMETRIC: Literal["android.permission.USE_BIOMETRIC"]

    USE_FINGERPRINT: Literal["android.permission.USE_FINGERPRINT"]

    USE_SIP: Literal["android.permission.USE_SIP"]

    VIBRATE: Literal["android.permission.VIBRATE"]

    WAKE_LOCK: Literal["android.permission.WAKE_LOCK"]

    WRITE_APN_SETTINGS: Literal["android.permission.WRITE_APN_SETTINGS"]

    WRITE_CALENDAR: Literal["android.permission.WRITE_CALENDAR"]

    WRITE_CALL_LOG: Literal["android.permission.WRITE_CALL_LOG"]

    WRITE_CONTACTS: Literal["android.permission.WRITE_CONTACTS"]

    WRITE_EXTERNAL_STORAGE: Literal["android.permission.WRITE_EXTERNAL_STORAGE"]

    WRITE_GSERVICES: Literal["android.permission.WRITE_GSERVICES"]

    WRITE_SECURE_SETTINGS: Literal["android.permission.WRITE_SECURE_SETTINGS"]

    WRITE_SETTINGS: Literal["android.permission.WRITE_SETTINGS"]

    WRITE_SYNC_SETTINGS: Literal["android.permission.WRITE_SYNC_SETTINGS"]

    WRITE_VOICEMAIL: Literal["com.android.voicemail.permission.WRITE_VOICEMAIL"]

PermissionCallback = Callable[[list[PERMISSIONS], list[bool]], None]

def request_permissions(
    permissions: list[PERMISSIONS], callback: Optional[PermissionCallback]
): ...
def request_permission(
    permission: PERMISSIONS, callback: Optional[PermissionCallback]
): ...
def check_permission(permission: PERMISSIONS): ...
