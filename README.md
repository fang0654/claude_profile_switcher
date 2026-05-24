# Claude Profile Switcher

Manage isolated [Claude Code](https://claude.ai/code) configuration profiles via symbolic links. Useful for keeping separate settings, credentials, and history for different contexts — work, personal, client projects, etc.

## How it works

Claude Code stores its configuration in two places:

- `~/.claude.json` — top-level config
- `~/.claude/` — directory containing settings, credentials, plugins, project history, etc.

Claude Profile Switcher moves those into versioned profile directories and replaces the originals with symlinks. Switching profiles re-points the symlinks instantly without touching Claude Code itself.

```
~/.claude.json  ->  ~/.local/share/claude_profiles/work/claude.json
~/.claude/      ->  ~/.local/share/claude_profiles/work/claude/
```

Profiles are stored under `~/.local/share/claude_profiles/<name>/`.

## Installation

Requires Python 3.9+. Install with [pipx](https://pipx.pypa.io/) (recommended for CLI tools):

```bash
pipx install git+https://github.com/fang0654/claude_profile_switcher
```

Or with pip:

```bash
pip install git+https://github.com/fang0654/claude_profile_switcher
```

This installs the `claude_profile` command.

## Quick start

```bash
# Migrate your existing Claude config into a profile called "default"
claude_profile install

# Create a new empty profile for work
claude_profile create work

# Switch to the work profile
claude_profile switch work

# See all profiles (* marks the active one)
claude_profile list
```

## Commands

### `install`

Migrates your current Claude config into a named profile and sets up symlinks. Run this once before using any other commands.

```bash
claude_profile install [--profile NAME]
```

- Default profile name is `default`
- Moves `~/.claude.json` and `~/.claude/` into the profile directory
- Creates symlinks at the original locations
- Errors if symlinks are already in place (already installed)

### `create`

Creates a new profile without switching to it.

```bash
claude_profile create <name> [--clone]
```

- Without `--clone`: creates an empty profile with minimal config
- With `--clone`: copies the currently active profile (including credentials, settings, and history)

### `switch`

Switches the active profile by re-pointing the symlinks.

```bash
claude_profile switch <name>
```

### `list`

Lists all profiles, marking the active one with `*`.

```bash
claude_profile list
```

```
    default
  * work
    personal
```

### `uninstall`

Removes the symlinks and restores the active profile's files to their standard locations, returning Claude Code to its normal (non-symlinked) state.

```bash
claude_profile uninstall
```

Any profiles other than the active one remain in `~/.local/share/claude_profiles/` but will no longer be managed.

## Credentials

`~/.claude/.credentials.json` lives inside `~/.claude/` and is therefore **profile-specific**. Each profile can be logged in to a different Claude account. Switching profiles switches credentials.

## Profile storage layout

```
~/.local/share/claude_profiles/
├── .active               # contains the active profile name
├── default/
│   ├── claude.json
│   └── claude/
│       ├── settings.json
│       ├── .credentials.json
│       └── ...
├── work/
│   ├── claude.json
│   └── claude/
└── personal/
    ├── claude.json
    └── claude/
```

## Dependencies

Standard library only — no third-party packages required.
