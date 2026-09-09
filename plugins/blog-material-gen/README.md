# Blog Material Generator

[English](README.md) | [한국어](README.ko.md)

| | |
|---|---|
| **Name** | blog-material-gen |
| **Description** | Auto-generate blog material from daily Git branches to Notion with Slack notifications |
| **Version** | 1.0.0 |
| **Triggers** | "blog material", "daily branch analysis", "generate writing material" |

---

A Claude Code plugin that automatically analyzes daily Git branches and generates blog material to Notion database.

## Features

- Git branch/commit analysis → Auto-extract blog ideas
- Date-based Notion page creation
- Same date, different workspace → Append to existing page with `[workspace]` tag
- Auto-mask sensitive data (API keys, tokens, passwords, etc.)
- Slack notifications (optional)
- **LLM-powered blog draft generation** - Optional AI-generated blog drafts using OpenAI, Anthropic, or Google Gemini
- **PR and commit links** - Auto-generated GitHub URLs in Notion output for easy navigation

## Installation

### Method 1: Marketplace (Recommended)

```bash
# Step 1: Add the marketplace
/plugin marketplace add byungsker/opengiver-skills

# Step 2: Install the plugin
/plugin install blog-material-gen@opengiver-skills

# Step 3: Restart Claude Code
```

### Method 2: Interactive UI

```bash
# Open plugin manager
/plugin

# Navigate to "Marketplaces" tab → Add → Enter: byungsker/opengiver-skills
# Then go to "Discover" tab → Find "blog-material-gen" → Install
```

## Setup

### 1. Create Notion Integration

1. Visit [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Enter name (e.g., "Blog Material Gen")
4. Select associated workspace
5. "Submit" → Copy API Key (`secret_xxx...`)

### 2. Connect Notion Database

1. Open your target database in Notion
2. Click `...` → "Connections" → "Connect to" → Select your integration
3. Get Database ID from URL:
   ```
   https://notion.so/myworkspace/abc123def456...?v=...
                               ^^^^^^^^^^^^^^^^
                               This is the Database ID
   ```

### 3. Run Setup Command

```bash
/blog-material-gen:setup
```

Agent will ask for the following:

| Item | Required | Description |
|------|----------|-------------|
| Notion API Key | Yes | Key starting with `secret_` |
| Database ID | Yes | 32-character hex string |
| Slack Webhook URL | No | Webhook URL for notifications |
| LLM Provider | No | OpenAI, Anthropic, or Google Gemini for blog draft generation |

Configuration is saved to `~/.config/blog-material-gen/config.json`.

## Slack Notifications (Optional)

### Create Webhook URL

1. [Slack API](https://api.slack.com/apps) → "Create New App" → "From scratch"
2. Enter app name, select workspace
3. "Incoming Webhooks" → "Activate Incoming Webhooks" ON
4. "Add New Webhook to Workspace" → Select channel → "Allow"
5. Copy Webhook URL (`https://hooks.slack.com/services/...`)

### Notification Content

On successful pipeline, Slack receives:

- Date
- Workspace name
- Number of branches analyzed
- Number of blog ideas generated
- Notion page link button

## LLM Providers (Optional)

The plugin supports 3 LLM providers for automatic blog draft generation. Choose one based on your needs:

### Supported Providers

| Provider | Models | Free Tier | API Key URL |
|----------|--------|-----------|-------------|
| **OpenAI** | gpt-4o-mini, gpt-4o | No | [Get API Key](https://platform.openai.com/api-keys) |
| **Anthropic** | Claude 3.5 Haiku, Sonnet, Opus | No | [Get API Key](https://console.anthropic.com/settings/keys) |
| **Google Gemini** | gemini-1.5-flash, gemini-1.5-pro | Yes (15 req/min, 1500/day) | [Get API Key](https://aistudio.google.com/app/apikey) |

### Recommendation

**Google Gemini Flash** is recommended for most users:
- Free tier with generous limits
- Fast response times
- Good quality blog drafts

### Configuration

LLM provider is configured during setup (`/blog-material-gen:setup`) or can be changed later with `/blog-material-gen:change-llm`.

**Config format**:
```json
{
  "api_key": "secret_xxx",
  "database_id": "abc123",
  "llm": {
    "provider": "google",
    "api_key": "AIza...",
    "model": "gemini-1.5-flash"
  }
}
```

### Disabling LLM

To disable LLM features, remove the `llm` object from config.json or use `/blog-material-gen:change-llm` and select "Disable".

## Usage

### Automatic Execution (Recommended)

If your `AGENTS.md` includes the Blog Material Generation Protocol, the agent automatically runs after daily → dev PR merge.

### Manual Execution

```bash
/blog-material-gen
```

Or specify a branch:

```
"Analyze daily/2026-01-24 branch"
"Generate blog material"
```

## Output

### Notion Page Structure

```
📝 2026-01-24 Writing Material

## Today's Summary
Today, through 15 commits across 3 feature branches...

## Blog Ideas
1. Implementing JWT Authentication in TypeScript
2. Optimizing Server State with React Query

## [opengiver-skills] Work Details
### feature/add-auth
- Requirements: Add user authentication
- Tech: TypeScript, React
- Code examples: ...
- Troubleshooting: ...
- Learnings: ...

## [another-project] Work Details  ← Same date, different workspace
### feature/update-ui
...
```

## Plugin Structure

```
blog-material-gen/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── commands/
│   ├── setup.md              # /blog-material-gen:setup
│   └── change-llm.md         # /blog-material-gen:change-llm
├── skills/
│   └── blog-material-gen/
│       └── SKILL.md          # Natural language skill
├── scripts/
│   ├── types.ts              # Type definitions
│   ├── git-analyzer.ts       # Git analysis
│   ├── code-masker.ts        # Sensitive data masking
│   ├── notion-client.ts      # Notion API client
│   ├── llm-client.ts         # LLM provider factory
│   ├── providers/            # LLM provider implementations
│   │   ├── openai.ts
│   │   ├── anthropic.ts
│   │   └── google.ts
│   └── pipeline.ts           # Main pipeline
├── package.json              # Dependencies
├── README.md
└── README.ko.md
```

## Troubleshooting

### "Configuration not complete"

```bash
/blog-material-gen:setup
```

### "Failed to connect to Notion"

1. Verify API Key starts with `secret_`
2. Check Integration is connected to the database
3. Verify Database ID is correct

### Slack notifications not working

1. Verify Webhook URL starts with `https://hooks.slack.com/services/`
2. Ensure Slack App has access to the channel

### LLM draft generation not working

1. Check LLM configuration exists in config.json
2. Verify API key is valid for the selected provider
3. Check provider-specific error messages in console
4. Try switching to a different provider with `/blog-material-gen:change-llm`

**Provider-specific checks**:
- **OpenAI**: Ensure API key starts with `sk-`
- **Anthropic**: Ensure API key starts with `sk-ant-`
- **Google**: Ensure API key starts with `AIza`

## License

MIT
