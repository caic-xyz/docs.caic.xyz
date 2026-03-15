#!/bin/bash
# Copy generated screenshots from caic into the docs public directory.
#
# Usage: ./scripts/update-screenshots.sh
#
# Prerequisites: run the screenshot generators first:
#   cd ../caic && npx playwright test --config e2e/playwright.config.ts gen-screenshots
#   Android screenshots: see scripts/gen-android-screenshots.sh

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_DIR="$(dirname "$SCRIPT_DIR")"
CAIC_DIR="$(dirname "$DOCS_DIR")/caic"
SRC="$CAIC_DIR/e2e/screenshots"
DST="$DOCS_DIR/public/screenshots"

if [ ! -d "$SRC" ] || [ -z "$(ls -A "$SRC" 2>/dev/null)" ]; then
	echo "No screenshots found in $SRC" >&2
	echo "Run: cd $CAIC_DIR && npx playwright test --config e2e/playwright.config.ts gen-screenshots" >&2
	exit 1
fi

mkdir -p "$DST"
cp "$SRC"/*.png "$DST"/
echo "Copied $(ls "$SRC"/*.png | wc -l) screenshots to $DST"
