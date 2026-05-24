import argparse
import shutil
import sys
from pathlib import Path

PROFILES_DIR = Path.home() / ".local/share/claude_profiles"
ACTIVE_FILE = PROFILES_DIR / ".active"
CLAUDE_JSON = Path.home() / ".claude.json"
CLAUDE_DIR = Path.home() / ".claude"


def get_active():
    if ACTIVE_FILE.exists():
        return ACTIVE_FILE.read_text().strip()
    return None


def set_active(name):
    ACTIVE_FILE.write_text(name)


def require_installed():
    if not CLAUDE_JSON.is_symlink() or not CLAUDE_DIR.is_symlink():
        print(
            "error: ~/.claude.json or ~/.claude/ is not a symlink — run 'claude_profile install' first",
            file=sys.stderr,
        )
        sys.exit(1)


def cmd_install(args):
    profile_name = args.profile

    if CLAUDE_JSON.is_symlink() or CLAUDE_DIR.is_symlink():
        print(
            "error: ~/.claude.json or ~/.claude/ is already a symlink — already installed; use 'claude_profile switch' to change profiles",
            file=sys.stderr,
        )
        sys.exit(1)

    profile_dir = PROFILES_DIR / profile_name
    if profile_dir.exists():
        print(f"error: profile '{profile_name}' already exists", file=sys.stderr)
        sys.exit(1)

    profile_dir.mkdir(parents=True)
    dest_json = profile_dir / "claude.json"
    dest_dir = profile_dir / "claude"

    if CLAUDE_JSON.exists():
        shutil.move(str(CLAUDE_JSON), str(dest_json))
    else:
        dest_json.write_text("{}\n")

    if CLAUDE_DIR.exists():
        shutil.move(str(CLAUDE_DIR), str(dest_dir))
    else:
        dest_dir.mkdir()
        (dest_dir / "settings.json").write_text("{}\n")

    CLAUDE_JSON.symlink_to(dest_json)
    CLAUDE_DIR.symlink_to(dest_dir)
    set_active(profile_name)

    print(f"installed profile '{profile_name}'")
    print(f"  ~/.claude.json -> {dest_json}")
    print(f"  ~/.claude/     -> {dest_dir}")


def cmd_create(args):
    name = args.name
    profile_dir = PROFILES_DIR / name

    if profile_dir.exists():
        print(f"error: profile '{name}' already exists", file=sys.stderr)
        sys.exit(1)

    if args.clone:
        active = get_active()
        if active is None:
            print(
                "error: no active profile to clone from — run 'install' first",
                file=sys.stderr,
            )
            sys.exit(1)
        src = PROFILES_DIR / active
        shutil.copytree(str(src), str(profile_dir))
        print(f"created profile '{name}' (cloned from '{active}')")
    else:
        (profile_dir / "claude").mkdir(parents=True)
        (profile_dir / "claude.json").write_text("{}\n")
        (profile_dir / "claude" / "settings.json").write_text("{}\n")
        print(f"created profile '{name}'")


def cmd_switch(args):
    name = args.name
    require_installed()

    profile_dir = PROFILES_DIR / name
    if not profile_dir.exists():
        print(f"error: profile '{name}' does not exist", file=sys.stderr)
        sys.exit(1)

    dest_json = profile_dir / "claude.json"
    dest_dir = profile_dir / "claude"

    CLAUDE_JSON.unlink()
    CLAUDE_DIR.unlink()
    CLAUDE_JSON.symlink_to(dest_json)
    CLAUDE_DIR.symlink_to(dest_dir)
    set_active(name)

    print(f"switched to profile '{name}'")


def cmd_list(args):
    if not PROFILES_DIR.exists():
        print("no profiles directory — run 'claude_profile install' first")
        return

    active = get_active()
    profiles = sorted(p.name for p in PROFILES_DIR.iterdir() if p.is_dir())

    if not profiles:
        print("no profiles found")
        return

    for p in profiles:
        marker = "*" if p == active else " "
        print(f"  {marker} {p}")


def cmd_uninstall(args):
    require_installed()

    active = get_active()
    if active is None:
        print("error: no active profile found in .active file", file=sys.stderr)
        sys.exit(1)

    profile_dir = PROFILES_DIR / active
    src_json = profile_dir / "claude.json"
    src_dir = profile_dir / "claude"

    # Remove symlinks
    CLAUDE_JSON.unlink()
    CLAUDE_DIR.unlink()

    # Move active profile files back to standard locations
    shutil.move(str(src_json), str(CLAUDE_JSON))
    shutil.move(str(src_dir), str(CLAUDE_DIR))

    # Clean up the now-empty profile directory and .active file
    profile_dir.rmdir()
    ACTIVE_FILE.unlink(missing_ok=True)

    print(f"uninstalled: restored profile '{active}' to standard locations")
    print(f"  ~/.claude.json (restored from {src_json})")
    print(f"  ~/.claude/     (restored from {src_dir})")
    print(f"  profile directory '{profile_dir}' removed")


def main():
    parser = argparse.ArgumentParser(
        prog="claude_profile",
        description="Manage isolated Claude Code configuration profiles",
    )
    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.required = True

    p_install = sub.add_parser("install", help="migrate current config into a profile and install symlinks")
    p_install.add_argument(
        "--profile",
        default="default",
        metavar="NAME",
        help="profile name to create (default: 'default')",
    )
    p_install.set_defaults(func=cmd_install)

    p_create = sub.add_parser("create", help="create a new profile")
    p_create.add_argument("name", help="name of the new profile")
    p_create.add_argument(
        "--clone",
        action="store_true",
        help="copy the active profile instead of starting empty",
    )
    p_create.set_defaults(func=cmd_create)

    p_switch = sub.add_parser("switch", help="switch to a different profile")
    p_switch.add_argument("name", help="profile to activate")
    p_switch.set_defaults(func=cmd_switch)

    p_list = sub.add_parser("list", help="list available profiles")
    p_list.set_defaults(func=cmd_list)

    p_uninstall = sub.add_parser(
        "uninstall",
        help="remove symlinks and restore the active profile to standard locations",
    )
    p_uninstall.set_defaults(func=cmd_uninstall)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
