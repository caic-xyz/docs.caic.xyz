#!/bin/bash
# Update documentation screenshots from caic.
#
# Usage: ./scripts/update-screenshots.sh [--android]
#
# Options:
#   --android   Also generate Android screenshots (requires emulator + APK, see
#               caic/scripts/gen-android-screenshots.sh for prerequisites)
#
# This script:
#   1. Clones caic into a sibling directory (../caic) if not already present
#   2. Runs Playwright screenshot generation in caic
#   3. Optionally runs Android screenshot generation in caic
#   4. Copies all screenshots (WebP + AVIF) into docs/public/screenshots/

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_DIR="$(dirname "$SCRIPT_DIR")"
CAIC_DIR="$(dirname "$DOCS_DIR")/caic"
SRC="$CAIC_DIR/e2e/screenshots"
DST="$DOCS_DIR/public/screenshots"

ANDROID=false
for arg in "$@"; do
	case "$arg" in
	--android) ANDROID=true ;;
	esac
done

# Clone caic if not present.
if [ ! -d "$CAIC_DIR" ]; then
	echo "Cloning caic into $CAIC_DIR..."
	git clone https://github.com/fghbuild/caic.git "$CAIC_DIR"
fi

# Install dependencies.
echo "Installing caic dependencies..."
cd "$CAIC_DIR"
pnpm install --frozen-lockfile
pnpm exec playwright install chromium

# Generate web UI screenshots.
echo "Generating web UI screenshots..."
pnpm exec playwright test --config e2e/playwright.config.ts gen-screenshots

# Generate Android screenshots.
if [ "$ANDROID" = true ]; then
	echo "Generating Android screenshots..."
	"$CAIC_DIR/scripts/gen-android-screenshots.sh"
fi

# Copy frontend screenshots (WebP + AVIF).
FRONTEND_SRC="$SRC/frontend"
if [ ! -d "$FRONTEND_SRC" ] || [ -z "$(ls -A "$FRONTEND_SRC"/*.webp "$FRONTEND_SRC"/*.avif 2>/dev/null)" ]; then
	echo "No screenshots found in $FRONTEND_SRC" >&2
	exit 1
fi

mkdir -p "$DST"
count=0
for ext in webp avif; do
	for f in "$FRONTEND_SRC"/*."$ext" 2>/dev/null; do
		[ -f "$f" ] && cp "$f" "$DST"/ && count=$((count + 1))
	done
done

# Copy Android screenshots if present.
ANDROID_SRC="$SRC/android"
if [ -d "$ANDROID_SRC" ]; then
	for f in "$ANDROID_SRC"/*.avif 2>/dev/null; do
		[ -f "$f" ] && cp "$f" "$DST"/ && count=$((count + 1))
	done
fi

echo "Copied $count screenshots to $DST"
