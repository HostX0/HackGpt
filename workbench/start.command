#!/bin/sh
# macOS / Linux: run the existing application, without installing dependencies.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' 'Python 3.11 or newer is required. No packages were installed.' >&2
    exit 1
fi
if [ "$#" -eq 0 ]; then
    set -- --open-browser
fi
exec python3 "$HERE/start.py" "$@"
