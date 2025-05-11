#!/bin/bash

set -e
PREFIX_BIN="$PREFIX/bin"

echo "[*] Installing dependencies from dependencies.txt..."
while read -r line; do
    type=$(echo "$line" | cut -d' ' -f1)
    name=$(echo "$line" | cut -d' ' -f2)

    if [ "$type" = "pkg" ]; then
        if ! command -v "$name" > /dev/null; then
            pkg install -y "$name"
        else
            echo "✓ $name already installed"
        fi
    elif [ "$type" = "pip" ]; then
        if ! command -v pip > /dev/null; then
            pkg install -y python
        fi
        if ! python -c "import $name" 2>/dev/null; then
            pip install "$name"
        else
            echo "✓ $name already installed (pip)"
        fi
    fi
done < dependencies.txt
echo "[*] Installing gith-dl commands..."
install -m 755 gith-dl "$PREFIX_BIN/gith-dl"
install -m 755 gith-dl-repo "$PREFIX_BIN/gith-dl-repo"
install -m 755 gith-dl-gist "$PREFIX_BIN/gith-dl-gist"
echo "[✓] Installed successfully."
