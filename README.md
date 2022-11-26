# MindRef

<img align="right" height="256" src="https://raw.githubusercontent.com/estasney/MindRef/master/mindref/assets/logo.png">

MindRef is a cross-platform Note Management application leveraging the [Kivy Framework](https://github.com/kivy/kivy).

MindRef renders Markdown notes with a special emphasis on technical notes, such as code snippets or keyboard shortcuts

## Development

### ImportError With Pycharm Debugger

- Patch virtualenv with [apply_patches.sh](./scripts/patches/apply_patches.sh)

### Building for Android

#### p4a Fork
I've forked [python-for-android](https://github.com/kivy/python-for-android) at [forked p4a](https://github.com/estasney/python-for-android)
to provide Python 3.10 support


#### MindRefUtils

With the introduction of SDK 33 on Android, it is no longer possible to simply request EXTERNAL_STORAGE permission and treat files natively.

A user selects a directory to share with Mindref. This provides a Content URI that is only usable via the `DocumentProvider`.

This requires some additional Java 'glue' code to sync External Storage with App Storage.

MindRefUtils can be found at [MindRefUtils](https://github.com/estasney/MindRefUtils)
