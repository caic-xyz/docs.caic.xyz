#!/usr/bin/env bash
# Refresh the curated documentation screenshots from caic's deterministic baselines.

set -euo pipefail

usage() {
	cat <<'EOF'
Usage: scripts/update-screenshots.sh [--android]

Regenerate and verify caic's deterministic frontend screenshots, then publish
the curated documentation assets. Pass --android to also regenerate and verify
the Go Mode screenshots with the canonical Android emulator.
EOF
}

android=false
case "${1:-}" in
"") ;;
--android) android=true ;;
-h | --help)
	usage
	exit 0
	;;
*)
	usage >&2
	printf 'error: unknown argument: %s\n' "$1" >&2
	exit 2
	;;
esac
if (( $# > 1 )); then
	usage >&2
	printf 'error: expected at most one argument\n' >&2
	exit 2
fi

require_command() {
	local name="$1"
	if ! command -v "$name" >/dev/null 2>&1; then
		printf 'error: required command not found: %s\n' "$name" >&2
		exit 1
	fi
}

for command_name in ffmpeg ffprobe git go make pnpm python3 realpath rsync; do
	require_command "$command_name"
done
if [[ "$android" == true ]]; then
	require_command adb
	require_command java
fi

git_bin="$(command -v git)"
make_bin="$(command -v make)"
python_bin="$(command -v python3)"
rsync_bin="$(command -v rsync)"
realpath_bin="$(command -v realpath)"
readonly git_bin make_bin python_bin realpath_bin rsync_bin

script_dir="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly script_dir
docs_dir="$(CDPATH='' cd -- "$script_dir/.." && pwd -P)"
readonly docs_dir
source_parent="$(CDPATH='' cd -- "$docs_dir/.." && pwd -P)"
readonly source_parent
caic_dir="$source_parent/caic"
public_dir="$docs_dir/public"
publish_dir="$public_dir/screenshots"
readonly caic_dir public_dir publish_dir
readonly canonical_origin='https://github.com/caic-xyz/caic'
readonly source_commit='daaf57672c6a91045ef3c6e0999823eb6a8c09e9'

if [[ -e "$caic_dir" && ! -d "$caic_dir" ]]; then
	printf 'error: caic path exists but is not a directory: %s\n' "$caic_dir" >&2
	exit 1
fi
if [[ ! -d "$caic_dir" ]]; then
	printf 'Cloning caic into %s...\n' "$caic_dir"
	"$git_bin" clone --no-checkout -- "$canonical_origin" "$caic_dir"
	"$git_bin" -C "$caic_dir" checkout --detach "$source_commit"
fi
if ! "$git_bin" -C "$caic_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
	printf 'error: caic path is not a Git checkout: %s\n' "$caic_dir" >&2
	exit 1
fi

source_origin="$("$git_bin" -C "$caic_dir" remote get-url origin)"
readonly source_origin
if [[ "$source_origin" != "$canonical_origin" ]]; then
	printf 'error: caic origin must be %s, found %s\n' "$canonical_origin" "$source_origin" >&2
	exit 1
fi
source_revision="$("$git_bin" -C "$caic_dir" rev-parse HEAD)"
readonly source_revision
if [[ "$source_revision" != "$source_commit" ]]; then
	printf 'error: caic must be checked out at %s, found %s\n' "$source_commit" "$source_revision" >&2
	exit 1
fi
if [[ -n "$("$git_bin" -C "$caic_dir" status --porcelain=v1 --untracked-files=all)" ]]; then
	printf 'error: caic worktree must be clean: %s\n' "$caic_dir" >&2
	exit 1
fi

orchestrator="$caic_dir/scripts/visual_screenshots.py"
readonly orchestrator
if [[ ! -f "$orchestrator" ]]; then
	printf 'error: caic visual orchestrator not found: %s\n' "$orchestrator" >&2
	exit 1
fi
if [[ ! -f "$caic_dir/Makefile" || ! -f "$caic_dir/package.json" ]]; then
	printf 'error: caic checkout is missing its build files: %s\n' "$caic_dir" >&2
	exit 1
fi
if [[ -L "$public_dir" ]]; then
	printf 'error: refusing to use symlinked public directory: %s\n' "$public_dir" >&2
	exit 1
fi
if [[ -L "$publish_dir" ]]; then
	printf 'error: refusing to replace symlinked screenshot directory: %s\n' "$publish_dir" >&2
	exit 1
fi

docs_root="$("$git_bin" -C "$docs_dir" rev-parse --show-toplevel)"
docs_root="$("$realpath_bin" -e -- "$docs_root")"
readonly docs_root
if [[ "$docs_root" != "$docs_dir" ]]; then
	printf 'error: documentation directory is not the repository root: %s\n' "$docs_dir" >&2
	exit 1
fi
mkdir -p -- "$publish_dir"
public_real="$("$realpath_bin" -e -- "$public_dir")"
publish_real="$("$realpath_bin" -e -- "$publish_dir")"
readonly public_real publish_real
case "$public_real" in
"$docs_root"/*) ;;
*)
	printf 'error: public directory resolves outside the docs repository: %s\n' "$public_real" >&2
	exit 1
	;;
esac
case "$publish_real" in
"$public_real"/*) ;;
*)
	printf 'error: screenshot directory resolves outside the public directory: %s\n' "$publish_real" >&2
	exit 1
	;;
esac
destination_root="$("$git_bin" -C "$publish_real" rev-parse --show-toplevel)"
destination_root="$("$realpath_bin" -e -- "$destination_root")"
readonly destination_root
if [[ "$destination_root" != "$docs_root" ]]; then
	printf 'error: screenshot directory is not owned by the docs repository: %s\n' "$publish_real" >&2
	exit 1
fi

printf 'Preparing caic frontend dependencies...\n'
"$make_bin" -C "$caic_dir" frontend-build playwright-browser

printf 'Verifying deterministic frontend screenshots...\n'
"$python_bin" "$orchestrator" check --platform frontend

if [[ "$android" == true ]]; then
	printf 'Preparing the canonical Android emulator...\n'
	"$make_bin" -C "$caic_dir" android-setup-emulator
	"$python_bin" "$caic_dir/scripts/android_start_emulator.py" --auto-reuse
	printf 'Verifying deterministic Android screenshots...\n'
	"$python_bin" "$orchestrator" check --platform android
fi

frontend_source="$caic_dir/e2e/screenshots/frontend/desktop"
android_source="$caic_dir/e2e/screenshots/android/phone"
readonly frontend_source android_source

readonly -a frontend_assets=(
	settings-mounts.webp
	task-ask.webp
	task-detail.webp
	task-native-subagents.webp
	task-plan.webp
	task-repository-changes.webp
	task-widget.webp
)
readonly -a android_assets=(
	gomode-settings.webp
	gomode-task-detail.webp
	gomode-task-list.webp
)

validate_asset() {
	local path="$1"
	if [[ ! -f "$path" || ! -s "$path" ]]; then
		printf 'error: required screenshot is missing or empty: %s\n' "$path" >&2
		exit 1
	fi
}

for asset in "${frontend_assets[@]}"; do
	validate_asset "$frontend_source/$asset"
done
for asset in "${android_assets[@]}"; do
	validate_asset "$android_source/$asset"
done

staging_dir="$(mktemp -d)"
readonly staging_dir
cleanup() {
	if [[ -n "$staging_dir" && -d "$staging_dir" ]]; then
		rm -rf -- "$staging_dir"
	fi
}
trap cleanup EXIT

mkdir -p -- "$staging_dir/frontend/desktop" "$staging_dir/android/phone"
for asset in "${frontend_assets[@]}"; do
	cp -- "$frontend_source/$asset" "$staging_dir/frontend/desktop/$asset"
done
for asset in "${android_assets[@]}"; do
	cp -- "$android_source/$asset" "$staging_dir/android/phone/$asset"
done

"$rsync_bin" --archive --delete -- "$staging_dir/" "$publish_real/"
printf 'Published %d curated screenshots to %s\n' \
	"$(( ${#frontend_assets[@]} + ${#android_assets[@]} ))" "$publish_real"
