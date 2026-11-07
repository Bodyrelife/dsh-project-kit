#!/usr/bin/env bash
# Install the dsh-project-kit skills into a DeepSeek Harness skills root.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILLS_SRC="$SCRIPT_DIR/skills"
SKILL_NAMES=(prime update-docs)

mode="user"
project_dir=""
use_copy=0
force=0
uninstall=0

usage() {
  cat <<'USAGE'
Install /prime and /update-docs skills for DeepSeek Harness.

Usage: ./install.sh [options]

Options:
  --project <dir>   Install into <dir>/.dsh/skills (project-level) instead of
                    the user-level root.
  --copy            Copy the skill directories instead of symlinking them.
  --force           Replace existing skills with the same name.
  --uninstall       Remove the two skills from the target root.
  -h, --help        Show this help.

Target root defaults to ${DSH_HOME:-~/.dsh}/skills.
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --project)
      [ $# -ge 2 ] || { echo "error: --project needs a directory" >&2; exit 2; }
      mode="project"; project_dir="$2"; shift 2 ;;
    --copy) use_copy=1; shift ;;
    --force) force=1; shift ;;
    --uninstall) uninstall=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ "$mode" = "project" ]; then
  # Resolve the project directory so the skills land where the user expects.
  [ -d "$project_dir" ] || { echo "error: not a directory: $project_dir" >&2; exit 1; }
  project_dir="$(cd "$project_dir" && pwd -P)"
  dest="$project_dir/.dsh/skills"
else
  dest="${DSH_HOME:-$HOME/.dsh}/skills"
fi

if [ "$uninstall" = "1" ]; then
  for name in "${SKILL_NAMES[@]}"; do
    target="$dest/$name"
    if [ -L "$target" ] || [ -d "$target" ]; then
      rm -rf -- "$target"
      echo "removed $target"
    fi
  done
  exit 0
fi

mkdir -p -- "$dest"

for name in "${SKILL_NAMES[@]}"; do
  src="$SKILLS_SRC/$name"
  target="$dest/$name"

  if [ ! -f "$src/SKILL.md" ]; then
    echo "error: missing $src/SKILL.md (incomplete checkout?)" >&2
    exit 1
  fi

  if [ -e "$target" ] || [ -L "$target" ]; then
    if [ "$force" = "1" ]; then
      rm -rf -- "$target"
    else
      echo "error: $target already exists (use --force to replace)" >&2
      exit 1
    fi
  fi

  if [ "$use_copy" = "1" ]; then
    cp -R -- "$src" "$target"
    echo "copied  $name -> $target"
  else
    ln -s -- "$src" "$target"
    echo "linked  $name -> $target"
  fi
done

echo
echo "Installed into $dest"
echo "In a DSH session:"
echo "  /prime            load project context (light)"
echo "  /prime --full     load everything"
echo "  /update-docs      sync docs after an architectural change"
