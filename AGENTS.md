# Repository documentation rules

## Plugin README metadata

- Put a compact metadata table at the top of each plugin `README.md` and `README.ko.md`, directly after the title and language links. Follow the format used in [`plugins/linear-simple/README.ko.md`](plugins/linear-simple/README.ko.md):

  ```markdown
  | | |
  |---|---|
  | **이름** | plugin-name |
  | **설명** | Short description |
  | **버전** | 1.0.0 |
  | **트리거** | Example phrases or commands |
  ```

- This block is a GitHub-Flavored Markdown table, not YAML frontmatter. Do not call it frontmatter. `SKILL.md` has a separate required YAML frontmatter format; preserve its `name` and `description` fields and do not replace them with a Markdown table.

## Command documentation

- Put the body command list in its own Markdown table. Keep the command syntax, natural-language example, behavior, and safety notes in clearly labeled columns.
- Make each command name itself a Markdown link to the real repository-relative file that defines or implements that command. Verify that every linked target exists before finishing.
- Prefer a command definition file such as `commands/<name>.md` when one actually exists. For commands represented as Skill intent aliases, link to the relevant existing `skills/<skill>/SKILL.md` definition. For direct CLI commands, link to the existing helper implementation when appropriate.
- Never create a link to a nonexistent `commands/` path or describe a Skill intent alias as a registered slash command. State the actual registration or invocation limit next to the table when it affects use.
- Use links relative to the README containing them. When listing several forms in one table cell, link every command form, not only the first one.

## Port Manager exception notes

- `port-manager` currently defines `/port-manger:*` as Skill intent aliases in `plugins/port-manager/skills/port-manager/SKILL.md`; there are no `plugins/port-manager/commands/` definitions. Link those aliases to the Skill file and describe them as intent notation, not Codex autocomplete registrations.
- Keep the `port-manager` package/Skill name distinct from the requested typo alias `port-manger`. Preserve the documented `$port-manager` Skill invocation.
