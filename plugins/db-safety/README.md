# DB Safety

[English](README.md) | [한국어](README.ko.md)

| | |
|---|---|
| **Name** | db-safety |
| **Description** | Backend/Server/DB Safety Protocol - Dangerous operation approval, SQL query guide, safe migration patterns |
| **Version** | 1.0.0 |
| **Triggers** | "DROP TABLE", "ALTER COLUMN", "DELETE FROM", "마이그레이션", "DB 스키마", "데이터 삭제", "테이블 변경", "SQL 쿼리", "Supabase", "dangerous operation" |

---

A Claude Code plugin for safe database operations. Prevents accidental data loss through mandatory approval workflows, SQL safety guides, and proven migration patterns.

## Features

- **Dangerous Operation Blocking**: Automatic approval requests for DROP, ALTER, DELETE, TRUNCATE operations
- **SQL Query Guide**: Safe vs. unsafe SQL patterns with explanations
- **Safe Migration Patterns**: Proven approaches for column deletion, type changes, and schema evolution
- **Environment Separation**: Dev DB (free experimentation) vs. Prod DB (CI/CD only)
- **Risk Level Classification**: LOW, MEDIUM, HIGH, CRITICAL with appropriate handling
- **Rollback Procedures**: Recovery strategies for migration failures and production incidents

## Installation

### 방법 1: 네 에이전트 공용 Skill 설치 (`npx skills`)

portable `SKILL.md`를 Codex, Claude Code, Hermes Agent, OpenClaw 순서로 설치합니다.

```bash
npx skills add https://github.com/byungsker/opengiver-skills \
  --skill db-safety \
  --agent codex claude-code hermes-agent openclaw \
  --global --copy --yes --full-depth
```

| 에이전트 | 기본 경로 |
|---|---|
| Codex | `~/.agents/skills/db-safety` |
| Claude Code | `~/.claude/skills/db-safety` |
| Hermes Agent | `~/.hermes/skills/db-safety` |
| OpenClaw | `~/.openclaw/skills/db-safety` |

### 방법 2: Codex 네이티브 플러그인 설치

```bash
codex plugin marketplace add byungsker/opengiver-skills --ref main
codex plugin add db-safety@opengiver-skills
```

### 방법 3: Claude Code 네이티브 플러그인 설치

```bash
claude plugin marketplace add byungsker/opengiver-skills
claude plugin install db-safety@opengiver-skills
```

### 방법 4: Hermes Agent 네이티브 Skill 설치

```bash
hermes skills install \
  https://raw.githubusercontent.com/byungsker/opengiver-skills/main/plugins/db-safety/skills/db-safety/SKILL.md \
  --yes
```

### 방법 5: OpenClaw 네이티브 Skill 설치

```bash
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 https://github.com/byungsker/opengiver-skills.git "$repo_dir"
openclaw skills install "$repo_dir/plugins/db-safety/skills/db-safety" \
  --as db-safety --global
```

`openclaw skills install`이 없는 구버전은 OpenClaw를 업데이트하거나 활성 workspace의 `skills/db-safety`에 해당 디렉터리를 배치하세요.

## Usage

The plugin automatically activates when you mention database operations:

### Dangerous Operations (Requires Approval)

```
"DROP TABLE users"
→ Agent: ⚠️ Dangerous operation detected - approval required
  Shows impact analysis, risks, and safe alternatives

"ALTER COLUMN user_id TYPE BIGINT"
→ Agent: ⚠️ High-risk schema change - approval required
  Suggests Expand-Contract pattern instead

"DELETE FROM logs"
→ Agent: ⚠️ Bulk deletion without WHERE clause - approval required
  Asks for confirmation and rollback plan
```

### SQL Query Guide

```
"How do I safely update user names?"
→ Agent: Shows safe UPDATE pattern with WHERE clause
  ✅ UPDATE users SET name = 'New' WHERE id = 123;
  ❌ UPDATE users SET name = 'New';  (dangerous!)

"What's the difference between DELETE and TRUNCATE?"
→ Agent: Explains both with safety implications
  DELETE: Slower, can be rolled back, use WHERE clause
  TRUNCATE: Faster, cannot be rolled back, never use without approval
```

### Safe Migration Patterns

```
"How do I remove a column safely?"
→ Agent: Shows 3-step safe deletion pattern
  Week 1: Stop using column in code
  Week 2: Rename to _deprecated_*
  Week 4: Actually delete (manual approval)

"How do I change a column type?"
→ Agent: Shows Expand-Contract pattern
  Step 1: Add new column with new type
  Step 2: Migrate data (in batches)
  Step 3: Switch code to use new column
  Step 4: Delete old column (after 2 weeks)
```

### Environment Rules

```
"Can I modify the production database?"
→ Agent: Explains environment separation
  ✅ Dev DB: Free to experiment
  ❌ Prod DB: Read-only (SELECT), CI/CD only for changes
  
"Should I test this migration on dev first?"
→ Agent: Yes! Always test on dev before prod
  Checklist: migration test, rollback SQL, build success, data impact
```

## Risk Levels & Handling

| Level | Operations | Agent Behavior |
|-------|-----------|-----------------|
| ✅ **LOW** | SELECT, INSERT, ADD COLUMN (nullable) | Execute immediately |
| ⚠️ **MEDIUM** | UPDATE (with WHERE), ADD INDEX | Confirm before executing |
| 🟠 **HIGH** | ALTER TYPE, RENAME COLUMN | Request approval + rollback plan |
| 🔴 **CRITICAL** | DROP, TRUNCATE, DELETE (no WHERE) | **Block execution**, require explicit approval |

## Approval Request Format

When a dangerous operation is detected:

```
⚠️ **Dangerous Operation Detected - Approval Required**

## Requested Operation
{Operation summary}

## Expected Impact
- **Dev DB**: {Impact description}
- **Prod DB**: {Impact description}
- **Existing Data**: {Impact description}

## Risk Factors
1. {Risk 1}
2. {Risk 2}

## Safe Alternative (Recommended)
{Safer approach if available}

## To Proceed
- [ ] Tested on dev first
- [ ] Prod backup confirmed
- [ ] Rollback SQL prepared

**Proceed with this operation? (yes/no)**
```

## SQL Safety Guide

### Safe Operations (No Approval Needed)

```sql
-- SELECT: Always safe
SELECT * FROM books WHERE user_id = 'abc123';

-- INSERT: Always safe
INSERT INTO books (title, author) VALUES ('Title', 'Author');

-- ADD COLUMN (nullable): Safe
ALTER TABLE books ADD COLUMN memo TEXT;
```

### Dangerous Operations (Approval Required)

```sql
-- DELETE without WHERE: Dangerous!
DELETE FROM books;  -- ❌ Deletes ALL data!

-- UPDATE without WHERE: Dangerous!
UPDATE books SET status = 'archived';  -- ❌ Updates ALL rows!

-- DROP: Irreversible!
DROP TABLE books;  -- ❌ Permanent deletion!

-- ALTER TYPE: Data loss risk!
ALTER TABLE books ALTER COLUMN page_count TYPE BIGINT;  -- ❌ May fail!
```

## Safe Migration Patterns

### Column Addition (Safe)

```sql
-- Step 1: Add nullable column
ALTER TABLE books ADD COLUMN created_at TIMESTAMP;
-- Existing rows get NULL, app starts using new column
```

### Column Deletion (3-Step Safe Pattern)

```
Week 1: Stop using column in code
Week 2: Rename to _deprecated_* (soft delete)
        ALTER TABLE books RENAME COLUMN old_col TO _deprecated_old_col_20260127;
Week 4: Actually delete (manual approval)
        ALTER TABLE books DROP COLUMN _deprecated_old_col_20260127;
```

### Column Type Change (Expand-Contract Pattern)

```
Step 1 - Expand: Add new column with new type
  ALTER TABLE books ADD COLUMN status_new book_status_enum;

Step 2 - Migrate: Convert existing data
  UPDATE books SET status_new = status::book_status_enum;

Step 3 - Switch: Update code to use new column
  // Code changes...

Step 4 - Contract: Delete old column (after 2 weeks)
  ALTER TABLE books DROP COLUMN status;
  ALTER TABLE books RENAME COLUMN status_new TO status;
```

## Pre-Deployment Checklist

Before merging DB changes to production:

- [ ] Migration tested on dev DB
- [ ] Rollback SQL prepared (for destructive changes)
- [ ] App build succeeds
- [ ] No impact on existing data confirmed

For destructive changes, also:

- [ ] 3-step deletion pattern applied (not immediate deletion)
- [ ] Prod backup timing confirmed (PITR available)
- [ ] Number of affected users identified
- [ ] Downtime requirement assessed

## Rollback Procedures

### Migration Failure

1. Check error message
2. Verify partial application (table/column state)
3. Execute rollback SQL or PITR recovery

### Production Incident

1. **Immediately**: Disable affected feature (feature flag)
2. **Within 5 min**: Identify root cause (check logs)
3. **Within 15 min**: Decide on rollback (code or DB)
4. **After recovery**: Write post-mortem

## Plugin Structure

```
db-safety/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── skills/
│   └── db-safety/
│       └── SKILL.md          # Natural language skill
├── README.md
└── README.ko.md
```

## License

MIT
