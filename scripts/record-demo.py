#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pexpect"]
# ///
"""Quick-start demo for md, recorded via asciinema.

Requires: md, docker/podman running, asciinema.

Usage:
    uv run record-demo.py /path/to/repo          # Record
    uv run record-demo.py /path/to/repo --no-rec  # Just run (no asciinema)

The repo must have an "origin" remote with a "main" branch.
The script simulates typing for a natural feel while executing real commands.
"""

import argparse
import contextlib
import os
import shutil
import subprocess
import sys
import time

import pexpect

PAUSE_BEFORE = 1.0  # pause before each comment
PAUSE_AFTER = 1.0  # pause after each command completes

# ANSI colors.
GREEN = "\033[1;32m"
DIM = "\033[0;90m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Invisible marker injected into the host prompt for pexpect matching.
HOST_MARKER = "\u200b"  # zero-width space
# Container prompt marker set by md.
CONTAINER_MARKER = "🐳"


def simulate_typing(child: pexpect.spawn, text: str, marker: str, comment: str = "") -> None:
    """Simulate typing a command, wait for the prompt, with optional inline comment.

    Types text character-by-character into the pexpect child. After each
    character, drains the PTY echo so it appears in real time via logfile_read.
    Without this, pexpect buffers all echo data until the next expect() call,
    making the typing appear instant.

    If comment is set, it is printed in dim gray directly to stdout after the
    command text, before sending Enter.
    """
    time.sleep(PAUSE_BEFORE)
    for ch in text:
        child.send(ch)
        time.sleep(0.04)
        with contextlib.suppress(pexpect.TIMEOUT, pexpect.EOF):
            child.read_nonblocking(size=1024, timeout=0.01)
    if comment:
        time.sleep(0.5)
        sys.stdout.write(f"  {DIM}# {comment}{RESET}")
        sys.stdout.flush()
    time.sleep(0.4)
    child.sendline("")
    child.expect(marker)
    time.sleep(PAUSE_AFTER)


def demo(repo_dir: str, cols: int, rows: int) -> None:
    os.environ["LANG"] = "C"
    repo = os.path.basename(repo_dir)
    src_dir = f"~/src/{repo}"

    print(f"{GREEN}# Disclaimer: This video is real time, not sped up.{RESET}")

    # Spawn the user's real shell, then silently inject an invisible marker
    # (zero-width space) into PROMPT_COMMAND so pexpect can match on it.
    child = pexpect.spawn(
        "bash",
        encoding="utf-8",
        timeout=120,
        cwd=repo_dir,
        dimensions=(rows, cols),
        env={**os.environ, "LANG": "C"},
    )
    # Wait for the shell to start and display its prompt.
    time.sleep(1)
    with contextlib.suppress(pexpect.TIMEOUT, pexpect.EOF):
        child.read_nonblocking(size=4096, timeout=0.5)
    child.logfile_read = None
    child.sendline(f"PROMPT_COMMAND=\"${{PROMPT_COMMAND}};echo;echo -n '{HOST_MARKER}'\"")
    child.expect(HOST_MARKER)
    child.logfile_read = sys.stdout

    # --- Host: create branch and start container ---
    simulate_typing(
        child,
        "git checkout -b demo-wip origin/main",
        HOST_MARKER,
        "Create a working branch",
    )
    simulate_typing(
        child,
        "md start -q",
        CONTAINER_MARKER,
        "Start container associated with this branch and SSH in",
    )

    # Silently inject a newline into the container prompt.
    child.logfile_read = None
    child.sendline('PROMPT_COMMAND="echo;${PROMPT_COMMAND}"')
    child.expect(CONTAINER_MARKER)
    child.logfile_read = sys.stdout

    # --- Inside the container ---
    simulate_typing(
        child, f"cd {src_dir}", CONTAINER_MARKER, "Navigate to the repo inside the container"
    )
    simulate_typing(
        child,
        "echo '# demo change' >> README.md",
        CONTAINER_MARKER,
        "Make a small change",
    )
    simulate_typing(child, "git --no-pager diff", CONTAINER_MARKER, "Show the diff")
    simulate_typing(child, "exit", HOST_MARKER, "Exit the ssh session to the container")

    # --- Back on host ---
    simulate_typing(
        child, "md pull", HOST_MARKER, "Pull changes from the container (wraps git pull)"
    )
    simulate_typing(
        child,
        "git --no-pager log --oneline -3",
        HOST_MARKER,
        "Changes are now local",
    )
    simulate_typing(child, "md purge", HOST_MARKER, "Delete the container")
    simulate_typing(
        child,
        "git checkout - && git branch -D demo-wip",
        HOST_MARKER,
        "Delete the working branch",
    )

    time.sleep(PAUSE_AFTER)
    print(f"{GREEN}Done!{RESET} Container purged, branch cleaned up.")
    time.sleep(PAUSE_AFTER)

    child.logfile_read = None
    child.sendline("exit")
    child.expect(pexpect.EOF)


def preflight(repo_dir: str, *, record: bool) -> int:
    """Check prerequisites. Returns 0 on success, non-zero on failure."""
    errors: list[str] = []

    # Check for leftover demo-wip branch.
    result = subprocess.run(
        "git rev-parse --verify demo-wip",
        shell=True,
        cwd=repo_dir,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        errors.append(
            "Branch 'demo-wip' already exists. Clean up first:\n"
            "  md purge && git branch -D demo-wip"
        )

    if record:
        if not shutil.which("asciinema"):
            errors.append(
                "asciinema not found. Install it with:\n"
                "  brew install asciinema      # macOS\n"
                "  sudo apt install asciinema  # Debian/Ubuntu\n"
                "  sudo pacman -S asciinema    # Arch\n"
                "  See https://docs.asciinema.org/getting-started/"
            )
        if not shutil.which("agg"):
            errors.append("agg not found. Install it from:\n  https://github.com/asciinema/agg")

    if errors:
        for err in errors:
            print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Record md quick-start demo")
    parser.add_argument("repo", help="Path to git repository to use for the demo")
    parser.add_argument("--no-rec", action="store_true", help="Run without asciinema recording")
    parser.add_argument("--cols", type=int, default=120, help="Terminal width (default: 120)")
    parser.add_argument("--rows", type=int, default=46, help="Terminal height (default: 46)")
    args = parser.parse_args()

    repo_dir = os.path.abspath(args.repo)
    if not os.path.isdir(os.path.join(repo_dir, ".git")):
        print(f"Error: {repo_dir} is not a git repository", file=sys.stderr)
        return 1

    if err := preflight(repo_dir, record=not args.no_rec):
        return err

    if args.no_rec:
        demo(repo_dir, args.cols, args.rows)
        return 0

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, os.pardir, "public")
    cast_file = os.path.join(output_dir, "md-quickstart.cast")

    # Spawn asciinema via pexpect to force the PTY size. asciinema reads the
    # terminal dimensions from the PTY, ignoring --cols/--rows in v3.
    script = os.path.abspath(__file__)
    rec_cmd = (
        f"asciinema rec --overwrite --title 'md quick start'"
        f" --command 'uv run {script} {repo_dir}"
        f" --no-rec --cols {args.cols} --rows {args.rows}'"
        f" {cast_file}"
    )
    child = pexpect.spawn(rec_cmd, encoding="utf-8", timeout=300, dimensions=(args.rows, args.cols))
    child.logfile_read = sys.stdout
    child.expect(pexpect.EOF)
    child.close()
    if child.exitstatus != 0:
        print(f"asciinema exited with status {child.exitstatus}", file=sys.stderr)
        return 1

    print(f"\nRecorded: {cast_file}")

    gif_file = os.path.join(output_dir, "md-quickstart.gif")
    subprocess.run(
        [
            "agg",
            "--theme",
            "monokai",
            "--font-size",
            "16",
            "--renderer",
            "resvg",
            "--fps-cap",
            "15",
            "--speed",
            "1",
            "--last-frame-duration",
            "20",
            cast_file,
            gif_file,
        ],
        check=True,
    )
    print(f"Generated: {gif_file}")

    avif_file = os.path.join(output_dir, "md-quickstart.avif")
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-stats",
            "-y",
            "-i",
            gif_file,
            "-c:v",
            "libaom-av1",
            "-cpu-used",
            "4",
            "-row-mt",
            "1",
            "-tiles",
            "2x2",
            "-crf",
            "30",
            "-pix_fmt",
            "yuv420p",
            avif_file,
        ],
        check=True,
    )
    print(f"Generated: {avif_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
