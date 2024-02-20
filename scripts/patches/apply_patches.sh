#!/bin/bash

# This patches issues with kivy and pytest that prevent the Pycharm Debugger from working because of posixpath.sep
# This modifies packages installed in a virtualenv
# These are generated with diff --text --unified --new-file {{old_file}} {{new_file}} > {{diff.patch}}


set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
VENV_PATH=$(readlink -f "$SCRIPT_DIR"/../../venv)



if [[ ! -e $VENV_PATH ]]; then
    echo Could not find "$VENV_PATH"
    exit 1
fi

SITE_PKG_PATH=$(find "$VENV_PATH" -name "site-packages")

if [[ ! -e $SITE_PKG_PATH ]]; then
    echo Could not find site-packages for "$VENV_PATH"
    exit 1
fi

declare -A patchTargets
patchTargets[flatDirs.patch]="$SITE_PKG_PATH/pythonforandroid/bootstraps/common/build/templates/build.tmpl.gradle"

for patchFile in "${!patchTargets[@]}"; do
  target="${patchTargets[$patchFile]}"
  if [[ ! -e "$target" ]]; then
      echo Could not find target for "$patchFile", "$target"
  else
    patch --batch -s -i "$patchFile" "$target"
  fi
done


#patchTargets[filechooser.patch]="$SITE_PKG_PATH/kivy/uix/filechooser.py"
#patchTargets[app.patch]="$SITE_PKG_PATH/kivy/app.py"
#patchTargets[pathlib.patch]="$SITE_PKG_PATH/_pytest/pathlib.py"
#
#