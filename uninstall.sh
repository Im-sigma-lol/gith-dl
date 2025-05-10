#!/bin/bash

echo "[*] Uninstalling gith-dl commands..."
rm -f "$PREFIX/bin/gith-dl" "$PREFIX/bin/gith-dl-repo" "$PREFIX/bin/gith-dl-gist"
echo "[✓] Uninstalled."
