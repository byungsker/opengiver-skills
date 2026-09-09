# Linear Simple

[English](README.md) | [Korean](README.ko.md)

| | |
|---|---|
| **Name** | linear-simple |
| **Description** | Linear GraphQL API skill - Direct curl calls without MCP for better token efficiency |
| **Version** | 1.1.6 |
| **Triggers** | "Linear issue", "BYU-125", "check issue", "create issue" |

---

A Claude Code plugin for Linear GraphQL API. Direct curl calls without MCP, improving token efficiency by 50-70%.

## Features

- **Create Issue**: Set title, description, priority
- **Get Issue**: Query by identifier (e.g., BYU-125)
- **Update Issue**: Change status (In Progress, Done, etc.)
- **Add Comment**: Post comments to issues
- **PR Update**: Create PR + add comment + update status in one command
- **Hierarchical Config**: User-level API key + project-level team/project settings

## Installation

### Method 1: Install the shared Skill for all agents (`npx skills`)

Install the portable `SKILL.md` for Codex, Claude Code, Hermes Agent, and OpenClaw in that order.

```bash
npx skills add https://github.com/byungsker/opengiver-skills \
  --skill linear-simple \
  --agent codex claude-code hermes-agent openclaw \
  --global --copy --yes --full-depth
```

| Agent | Default path |
|---|---|
| Codex | `~/.agents/skills/linear-simple` |
| Claude Code | `~/.claude/skills/linear-simple` |
| Hermes Agent | `~/.hermes/skills/linear-simple` |
| OpenClaw | `~/.openclaw/skills/linear-simple` |

### Method 2: Install the native Codex plugin

```bash
codex plugin marketplace add byungsker/opengiver-skills --ref main
codex plugin add linear-simple@opengiver-skills
```

### Method 3: Install the native Claude Code plugin

```bash
claude plugin marketplace add byungsker/opengiver-skills
claude plugin install linear-simple@opengiver-skills
```

### Method 4: Install the native Hermes Agent Skill

```bash
hermes skills install \
  https://raw.githubusercontent.com/byungsker/opengiver-skills/main/plugins/linear-simple/skills/linear-simple/SKILL.md \
  --yes
```

### Method 5: Install the native OpenClaw Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/linear-simple"
mkdir -p "$target"
cp -R "$repo_dir/plugins/linear-simple/skills/linear-simple/." "$target/"
openclaw skills list
```

The current OpenClaw CLI has no Skill install subcommand; the copy above uses its managed global Skill directory. For a workspace-only installation, copy the same directory to `skills/linear-simple` in that workspace.

## Setup (Required)

After installation, configure your Linear API:

```bash
/linear-simple:setup
```

Claude will:
1. Ask for your Linear API key (get from Linear Settings > API)
2. Save API key to `~/.config/linear-simple/config.json`
3. Ask: "Set up Linear team/project for this workspace?" (Yes/No)
   - **Yes** → Select team/project → Save to `.claude/linear-simple.json` (added to `.gitignore`)
   - **No** → Use default team from user config

To share workspace config with your team, remove `.claude/linear-simple.json` from `.gitignore`.

## Configuration

### Hierarchical Config Structure

| Level | Location | Contains |
|-------|----------|----------|
| User | `~/.config/linear-simple/config.json` | API key, default team |
| Project | `.claude/linear-simple.json` | Team, project (workspace-specific) |

### User Config (`~/.config/linear-simple/config.json`)
```json
{
  "api_key": "lin_api_xxxxx",
  "default_team_id": "uuid",
  "default_team_key": "BYU",
  "default_team_name": "Team Name"
}
```

### Project Config (`.claude/linear-simple.json`)
```json
{
  "team_id": "uuid",
  "team_key": "BYU",
  "team_name": "Team Name",
  "project_id": "uuid",
  "project_name": "Bookgolas"
}
```

**Loading Priority:**
1. Project config (if exists) → for team/project
2. User config → for API key + fallback team

## Usage

### Slash Commands
```bash
/linear-simple:setup                        # Configure API and project
/linear-simple:get BYU-125                  # Get issue details
/linear-simple:list                         # List recent issues (asks for count)
/linear-simple:list 10                      # List recent 10 issues
/linear-simple:create "Fix API bug"         # Create new issue
/linear-simple:status BYU-125 "In Progress" # Update status
/linear-simple:comment BYU-125 "Done!"      # Add comment
/linear-simple:pr-update                    # PR + comment + status update
```

### Natural Language

**Get Issue**
```
"Read issue BYU-125 and help me plan the implementation"
"What's in BYU-125? I need to understand the requirements"
"Show me BYU-125 details"
```

**List Issues**
```
"Show me the recent 10 issues"
"What issues are currently in progress?"
"List all backlog items"
```

**Create Issue**
```
"Create an issue"
→ Agent: "What title and description should I use?"
→ You: "Title: [Product] Implement checkout flow
        Description: (generate something appropriate based on the title)"

"Make a new issue for the login bug we just discussed"
"Add an issue: API rate limiting implementation"
```

**Update Status**
```
"Change BYU-125 to In Progress"
"Mark BYU-125 as Done"
"Set BYU-125 to In Review"
```

**Add Comment**
```
"Create a PR and add a comment to this task's issue"
→ Agent checks context for issue number, creates PR, and posts PR details as comment

"Comment on BYU-125: Started implementation"
"Add note to BYU-125 with today's progress"
```

**PR + Update (Combined)**
```
"Create PR and update the Linear issue"
→ Agent: Creates PR, adds PR link as comment, changes status to "In Review"

"Push this PR and sync with Linear"
"Finish this task - create PR and mark issue as In Review"
```

## Token Efficiency: MCP vs Skill

| Method | Tokens (10 operations) |
|--------|------------------------|
| MCP | ~570,000 tokens |
| Skill | ~520,000 tokens |
| **Saved** | **~50,000 tokens (9%)** |

In longer conversations, efficiency gains increase significantly (up to 99% savings).

## Plugin Structure

```
linear-simple/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── commands/
│   ├── setup.md              # /linear-simple:setup
│   ├── get.md                # /linear-simple:get
│   ├── list.md               # /linear-simple:list
│   ├── create.md             # /linear-simple:create
│   ├── status.md             # /linear-simple:status
│   ├── comment.md            # /linear-simple:comment
│   └── pr-update.md          # /linear-simple:pr-update
├── skills/
│   └── linear-simple/
│       ├── SKILL.md          # Natural language skill
│       └── references/
│           └── graphql-patterns.md
├── README.md
└── README.ko.md
```

## License

MIT
