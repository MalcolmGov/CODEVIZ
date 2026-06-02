#!/usr/bin/env bash
# git-commit.sh — safe commit wrapper for virtiofs/FUSE mounts
#
# Problem: the sandbox FUSE mount allows rename() but blocks unlink().
# Git creates HEAD.lock / index.lock during commits and adds, then tries
# to delete them. The delete fails silently, leaving stale locks that
# block the next operation ("Another git process seems to be running").
#
# Solution: rename stale locks out of the way before running git.
# Stale files accumulate in .git/stale-locks/
# Clean them from your Mac with: make clean-locks

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
  echo "❌  Not inside a git repository." >&2
  exit 1
fi

STALE_DIR="$REPO_ROOT/.git/stale-locks"
mkdir -p "$STALE_DIR"

TIMESTAMP="$(date +%s)"
CLEARED=0

for LOCK in HEAD index MERGE_HEAD CHERRY_PICK_HEAD; do
  LOCK_FILE="$REPO_ROOT/.git/${LOCK}.lock"
  if [ -f "$LOCK_FILE" ]; then
    mv "$LOCK_FILE" "$STALE_DIR/${LOCK}.lock.${TIMESTAMP}"
    echo "⚠️   Cleared stale lock: .git/${LOCK}.lock"
    CLEARED=$((CLEARED + 1))
  fi
done

[ "$CLEARED" -gt 0 ] && echo ""

# Accept an optional leading list of files to stage before committing
# Usage: git-commit.sh [files...] -- -m "message"
# OR:    git-commit.sh -m "message"         (commits whatever is staged)

# Split args: everything before "--" is treated as files to add
FILES=()
GIT_ARGS=()
SPLIT=false
for arg in "$@"; do
  if [ "$arg" = "--" ]; then
    SPLIT=true
  elif [ "$SPLIT" = false ] && [[ "$arg" != -* ]]; then
    FILES+=("$arg")
  else
    GIT_ARGS+=("$arg")
  fi
done

# If files were specified, stage them now (locks already cleared above)
if [ "${#FILES[@]}" -gt 0 ]; then
  git add "${FILES[@]}"
fi

# If no explicit GIT_ARGS, use all positional args as commit args
if [ "${#GIT_ARGS[@]}" -eq 0 ]; then
  git commit "$@"
else
  git commit "${GIT_ARGS[@]}"
fi
