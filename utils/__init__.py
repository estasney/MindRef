from kivy.lang import Builder


def import_kv(path):
    import os

    base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
    kv_path = os.path.relpath(path, base_path).rsplit(".", 1)[0] + ".kv"
    if kv_path not in Builder.files:
        Builder.load_file(kv_path, rulesonly=True)