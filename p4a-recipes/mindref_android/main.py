"""Android entrypoint. Staged as the app-root main.py by the Makefile prebuild.

All startup logic (font registration, platform dispatch) lives in
mindref.main so desktop and Android cannot drift apart.
"""

from mindref.main import main

if __name__ == "__main__":
    main()
