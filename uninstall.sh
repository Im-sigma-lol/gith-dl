#!/bin/bash

set -e

# Define the path where gith-dl is installed
PREFIX_BIN="$PREFIX/bin"
GITH_DL_DIR="$PREFIX_BIN/gith-dl"

echo "[*] Uninstalling gith-dl..."

# Remove the gith-dl command and other scripts
if [ -f "$GITH_DL_DIR" ]; then
    rm -f "$GITH_DL_DIR"
    echo "[✓] Removed gith-dl command."
else
    echo "[!] gith-dl command not found."
fi

# Optionally remove the whole directory if you want
if [ -d "$PREFIX_BIN" ]; then
    # Remove the gith-dl folder if it's not empty
    rm -rf "$GITH_DL_DIR"
    echo "[✓] Removed gith-dl directory."
else
    echo "[!] Directory not found."
fi

echo "[✓] Uninstallation complete."
