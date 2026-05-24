# Claude Profile Switcher

A Python package that manages isolated Claude Code configuration profiles via symbolic links. Installed as the `claude_profile` command.

## Overview

Claude Code stores its configuration in two locations:
- `~/.claude.json` — top-level config file
- `~/.claude/` — config directory containing settings, plugins, projects, history, etc.

This tool moves those into versioned profile directories under `~/.local/share/claude_profiles/<name>/` and replaces the originals with symlinks. Switching profiles re-points the symlinks.

## Profile Storage Layout

```
~/.local/share/claude_profiles/
├── default/
│   ├── claude.json          # copy of original ~/.claude.json
│   └── claude/              # copy of original ~/.claude/
│       ├── settings.json
│       ├── .credentials.json
│       ├── plugins/
│       ├── projects/
│       └── ...
├── work/
│   ├── claude.json
│   └── claude/
└── personal/
    ├── claude.json
    └── claude/
```

The symlinks at the standard locations point into whichever profile is active:
```
~/.claude.json  ->  ~/.local/share/claude_profiles/work/claude.json
~/.claude/      ->  ~/.local/share/claude_profiles/work/claude/
```

Active profile is tracked in `~/.local/share/claude_profiles/.active` (contains the profile name as a single line).

## Commands

### `install`

Migrates the current live config into a named profile and installs symlinks.

```
claude_profile install [--profile NAME]
```

- Default profile name: `default`
- Moves `~/.claude.json` → `~/.local/share/claude_profiles/<name>/claude.json`
- Moves `~/.claude/` → `~/.local/share/claude_profiles/<name>/claude/`
- Creates symlinks at original locations pointing to profile copies
- Writes the profile name to `.active`
- Errors if symlinks already exist (already installed); prompt user to run `switch` instead

### `create`

Creates a new empty profile or clones the active one.

```
claude_profile create <name> [--clone]
```

- Without `--clone`: creates `~/.local/share/claude_profiles/<name>/` with a minimal `settings.json` and empty `claude.json` (`{}`)
- With `--clone`: copies the currently active profile's directory tree into the new profile
- Does not switch to the new profile automatically
- Errors if a profile with that name already exists

### `switch`

Changes the active profile by re-pointing the symlinks.

```
claude_profile switch <name>
```

- Verifies the named profile exists
- Removes current symlinks at `~/.claude.json` and `~/.claude/`
- Creates new symlinks pointing at the target profile
- Updates `.active`
- Errors if the path at `~/.claude.json` or `~/.claude/` is a real file/directory (not a symlink) — means `install` was never run

### `list`

Prints all available profiles, marking the active one.

```
claude_profile list
```

Output format:
```
  default
* work
  personal
```

### `uninstall`

Removes the symlinks and restores the active profile's files to their standard locations.

```
claude_profile uninstall
```

- Errors if `~/.claude.json` or `~/.claude/` are not symlinks (not installed)
- Removes the symlinks at `~/.claude.json` and `~/.claude/`
- Moves the active profile's `claude.json` and `claude/` back to `~/.claude.json` and `~/.claude/`
- Removes the now-empty profile directory and `.active` file
- Other profiles (if any) remain in `~/.local/share/claude_profiles/` but are no longer managed

## Implementation Notes

### Credentials

`~/.claude/.credentials.json` lives inside `~/.claude/` and is therefore profile-specific by default. This allows multiple accounts across profiles. Document this behavior clearly so users understand credential isolation.

### Minimal `settings.json` for new profiles

When `create` is run without `--clone`, seed `~/.local/share/claude_profiles/<name>/claude/settings.json` with:
```json
{}
```
And `claude.json` with `{}`. Claude Code will populate defaults on first run.

### Directory vs file symlinks

Both `~/.claude` (directory) and `~/.claude.json` (file) need symlinks. Use `os.symlink()` for both — Python handles file and directory symlinks the same way on Linux.

### Safety checks

- Before `install`: verify neither `~/.claude.json` nor `~/.claude/` is already a symlink
- Before `switch`: verify both paths are symlinks (install has been run)
- Before `create`: verify profile name doesn't already exist
- Before `switch`: verify target profile directory exists

### Dependencies

Standard library only: `os`, `shutil`, `pathlib`, `argparse`, `sys`. No third-party packages.

## File Structure

```
claude_profile_switcher/
├── pyproject.toml
└── claude_profile_switcher/
    ├── __init__.py
    └── cli.py          # all logic and argparse entrypoint
```

The `main()` function in `cli.py` is the package entrypoint. `__init__.py` can be empty.

### `pyproject.toml`

```toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "claude-profile-switcher"
version = "0.1.0"
requires-python = ">=3.9"

[project.scripts]
claude_profile = "claude_profile_switcher.cli:main"
```

Install locally with `pip install -e .` (editable) or `pip install .`.

## Constants

These live at the top of `cli.py`:

```python
PROFILES_DIR = Path.home() / ".local/share/claude_profiles"
ACTIVE_FILE  = PROFILES_DIR / ".active"
CLAUDE_JSON  = Path.home() / ".claude.json"
CLAUDE_DIR   = Path.home() / ".claude"
```
