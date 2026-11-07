#!/usr/bin/env python3
"""Validate every skill in skills/ before it reaches a harness.

A malformed SKILL.md is dropped silently by the loader, so a typo in the
frontmatter looks exactly like a missing skill. This check fails loudly
instead: name grammar, directory/frontmatter agreement, allowed keys,
required fields, and referenced resources.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_KEYS = {
    "name",
    "description",
    "whenToUse",
    "metadata",
    "disable-model-invocation",
    "user-invocable",
}
LEGACY_KEYS = {
    "user_invocable": "user-invocable",
    "userInvocable": "user-invocable",
    "disableModelInvocation": "disable-model-invocation",
    "modelInvocable": "disable-model-invocation",
}
RESOURCE_REF = re.compile(r"references/[A-Za-z0-9._-]+")


def fail(errors: list[str], where: str, message: str) -> None:
    errors.append(f"{where}: {message}")


def parse_frontmatter(text: str, where: str, errors: list[str]) -> dict[str, str] | None:
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match:
        fail(errors, where, "missing YAML frontmatter (must start with ---)")
        return None

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            fail(errors, where, f"frontmatter line is not a key/value pair: {line!r}")
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        elif value[:1] in "\"'":
            fail(errors, where, f"unterminated quoted value for {key!r}")
        fields[key] = value
    return fields


def check_skill(skill_dir: Path, errors: list[str]) -> None:
    where = skill_dir.relative_to(ROOT).as_posix()
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        fail(errors, where, "missing SKILL.md")
        return

    text = skill_file.read_text(encoding="utf-8")
    fields = parse_frontmatter(text, where, errors)
    if fields is None:
        return

    name = fields.get("name", "")
    if not name:
        fail(errors, where, "missing required field 'name'")
    elif not NAME.match(name):
        fail(errors, where, f"name {name!r} is not kebab-case ([a-z0-9-], no leading/trailing dash)")
    elif name != skill_dir.name:
        fail(errors, where, f"name {name!r} does not match directory {skill_dir.name!r}")

    if not fields.get("description", "").strip():
        fail(errors, where, "missing required field 'description'")

    for key in fields:
        if key in LEGACY_KEYS:
            fail(errors, where, f"key {key!r} is rejected by the loader; use {LEGACY_KEYS[key]!r}")
        elif key not in ALLOWED_KEYS:
            fail(errors, where, f"unknown frontmatter key {key!r}")

    for ref in set(RESOURCE_REF.findall(text)):
        if not (skill_dir / ref).is_file():
            fail(errors, where, f"body references {ref!r} but the file does not exist")


def check_bundle_declaration(errors: list[str]) -> None:
    """Keep the optional bundle mode honest: a declared patch and entry must exist."""
    manifest = ROOT / "package.json"
    if not manifest.is_file():
        fail(errors, "package.json", "missing (the bundle mode needs it)")
        return

    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(errors, "package.json", f"invalid JSON: {error}")
        return

    patch = data.get("dsh", {}).get("bundle", {}).get("patch")
    if patch is None:
        fail(errors, "package.json", "missing dsh.bundle.patch")
    elif not (ROOT / patch).is_file():
        fail(errors, "package.json", f"dsh.bundle.patch points at {patch!r}, which does not exist")

    entry = data.get("main")
    if entry is None:
        fail(errors, "package.json", "missing main (the plugin entry)")
    elif not (ROOT / entry).is_file():
        fail(errors, "package.json", f"main points at {entry!r}, which does not exist")


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"error: no skills/ directory at {SKILLS_DIR}", file=sys.stderr)
        return 1

    errors: list[str] = []
    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    if not skill_dirs:
        print("error: skills/ is empty", file=sys.stderr)
        return 1

    for skill_dir in skill_dirs:
        check_skill(skill_dir, errors)
    check_bundle_declaration(errors)

    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        print(f"\n{len(errors)} problem(s) in {len(skill_dirs)} skill(s)", file=sys.stderr)
        return 1

    for skill_dir in skill_dirs:
        size = (skill_dir / "SKILL.md").stat().st_size
        print(f"ok   {skill_dir.name} ({size} bytes)")
    print(f"\nall {len(skill_dirs)} skills valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
