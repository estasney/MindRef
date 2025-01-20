# MindRef

<img align="right" height="256" src="https://raw.githubusercontent.com/estasney/MindRef/master/mindref/assets/logo.png">

MindRef is a cross-platform Note Management application leveraging the [Kivy Framework](https://github.com/kivy/kivy).

MindRef renders Markdown notes with a special emphasis on technical notes, such as code snippets or keyboard shortcuts

## Development

### ImportError With Pycharm Debugger

- Patch virtualenv with [apply_patches.sh](./scripts/patches/apply_patches.sh)

### Building for Android

#### p4a Fork

I've forked [python-for-android](https://github.com/kivy/python-for-android)
at [forked p4a](https://github.com/estasney/python-for-android)
to provide Python 3.12 support

Building with p4a requires a python installation that is not binary. Disabling the uv managed python downloads was
required.

Now using [kivy/python-for-android](https://github.com/kivy/python-for-android) which is Python 3.10 compatible
However, it still requires a single patch to build.tmpl.gradle to include

```
flatDir {
    dirs 'libs'
}
```

The patch is located at [flatDirs.patch](./scripts/patches/flatDirs.patch)

#### MindRefUtils

With the introduction of SDK 33 on Android, it is no longer possible to simply request EXTERNAL_STORAGE permission and
treat files natively.

A user selects a directory to share with Mindref. This provides a Content URI that is only usable via
the `DocumentProvider`.

This requires some additional Java 'glue' code to sync External Storage with App Storage.

MindRefUtils can be found at [MindRefUtils](https://github.com/estasney/MindRefUtils)

### Benchmarks

#### normalize_coordinates

*100,000 iterations, 10 repeats*

    - Python 3.10.9
        - 0.0281 seconds
    - Cython
        - 0.0048 seconds

*Cython is 5.8x faster than Python*

#### rolling_index

*1,000,000 iterations, 10 repeats*

    - Python 3.10.9
        - 0.2755 seconds
    - Cython
        - 0.1278 seconds

* Cython is 2.15x faster than Python*

#### compute_ref_coordinates

*100,000 iterations, 10 repeats*

    - Python 3.10.9
        - 0.0200 seconds
    - Cython
        - 0.0116 seconds

* Cython is 1.72x faster than Python*

#### color_str_components

*100,000 iterations, 10 repeats*

    - Python 3.10.9
        - 0.0234 seconds
    - Cython
        - 0.0075 seconds

* Cython is 3.12x faster than Python*
