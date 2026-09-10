# From commitizen

commitizen writes commits, bumps versions, and generates changelogs; `cz
check` is its lint, and matches a message against the chosen rule's
`schema_pattern`. For `cz_conventional_commits`, that is the Conventional
Commits header with commitizen's type list, a blank line, and anything
after. Here that is `Conventional`, `Commits.Blank`, and `Commitizen.Type`.

## Config

```toml
# .cz.toml
[tool.commitizen]
name = "cz_conventional_commits"
```

with a `pre-commit` hook of `cz check --commit-msg-file` becomes

```ini
[COMMIT_EDITMSG]
BasedOnStyles = Commits, Conventional, Commitizen
```

and `vale --path=COMMIT_EDITMSG < "$1"` in the hook.

## Every option

| commitizen | Here |
| ---------- | ---- |
| The schema pattern's types | `Commitizen.Type`: `build`, `bump`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test` |
| The pattern's shape | `Conventional.Type`, `Conventional.Space`, `Conventional.Description` |
| The blank line the pattern requires | `Commits.Blank` |
| `message_length_limit` | `Commitlint.HeaderLength[max]`, or `SevenRules.Truncated` |
| `allowed_prefixes`: `Merge`, `Revert`, `fixup!`, `squash!`, `amend!` | The skip list in [`script/commit-msg`](../script/commit-msg) |
| `--allow-abort` | Git aborts an empty message before a hook sees it |
| `--rev-range` | A loop over `git log`; see [wiring.md](wiring.md) |
| A custom rule's `schema_pattern` | An `existence` rule on `subject` |
| `cz commit`, `cz bump`, `cz changelog` | Not carried: this package lints |

## Differences

`cz check` is one regex against the header. Everything a body or footer
can get wrong is invisible to it and reported here: the blank line, the
wrap, the footer tokens, the `BREAKING CHANGE` case. A message that passes
`cz check` can still fail `Commits.Imperative`, which is the point.

The plugins, `cz-emoji`, `cz-conventional-gitmoji`, and the Jira variants,
are `Gitmoji` and `Jira` here, and `EmojiLog` for a set commitizen lacks.
