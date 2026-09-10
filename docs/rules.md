# Rules

Each rule carries a `link` to the passage it enforces, and each alert shows
it. A limit written as `[max]` or `[min]` is a parameter, set from the
config: `SevenRules.Limit[max] = 60`. A rule marked *off* ships off in the
package config, as its source leaves it off; `Style.Rule = YES` turns it on.

## Commits

The core, on by default.

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `Commits.Blank` | error | A body that starts on the second line. Git reads it as part of the subject. |
| `Commits.Imperative` | warning | A subject in the past tense, the third person, or the gerund: `Added`, `Fixes`, `Updating`; or one that opens `This commit` or `I`. Any prefix a convention adds is skipped first. |
| `Commits.Whitespace` | error | Whitespace at either edge of the subject. |
| `Commits.Placeholder` | warning | A subject that names the act of committing and not the change: `fix`, `wip`, `update`, `changes`, `fix: fix`. |

## Conventional

The [specification](https://www.conventionalcommits.org/en/v1.0.0/#specification), and only it.

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `Conventional.Type` | error | A subject without a `type:` or `type(scope)!:` prefix. |
| `Conventional.Space` | error | A colon with no space after it. |
| `Conventional.Scope` | error | An empty `()`. |
| `Conventional.Description` | error | A prefix with nothing after it. |
| `Conventional.Breaking` | error | `Breaking change:` in any case but capitals, the one token the spec reads case-sensitively. |
| `Conventional.Token` | error | A footer token with a space in it: `Signed off by`, where the spec wants `Signed-off-by`. |
| `Conventional.Footer` | warning | A footer on the line after the body, with no blank line between. |

## Commitlint

[commitlint's rules](https://commitlint.js.org/reference/rules.html), with
`config-conventional`'s on. Goes with `Conventional`. The
[conversion guide](commitlint.md) maps every commitlint rule.

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `Commitlint.Type` | error | A type outside the eleven: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`. |
| `Commitlint.TypeCase` | error | A type with a capital in it. |
| `Commitlint.SubjectCase` | error | A subject that opens with a capitalized word or is all capitals. `URL parsing` passes. |
| `Commitlint.FullStop` | error | A period at the end of the subject. |
| `Commitlint.HeaderLength` | error | A header past 100 characters, or past `[max]`. |
| `Commitlint.BodyLength` | error | A body line past 100 characters, URLs exempt. |
| `Commitlint.FooterLength` | error | A footer line past 100 characters, URLs exempt. |
| `Commitlint.Scope` | off | A scope outside the list; extend it with yours. |
| `Commitlint.ScopeRequired` | off | A header with no scope. |
| `Commitlint.ScopeCase` | off | A scope with a capital in it. |
| `Commitlint.HeaderCase` | off | A capital anywhere in the header. |
| `Commitlint.HeaderMinLength` | off | A header under `[min]` characters, 10 by default. |
| `Commitlint.SubjectLength` | off | A description, after the prefix, over `[max]` or under `[min]`: 72 and 1 by default. |
| `Commitlint.Body` | off | No body. |
| `Commitlint.BodyMinLength` | off | A body under `[min]` characters, 20 by default, or none. |
| `Commitlint.BodyMaxLength` | off | A body over `[max]` characters in all, 1000 by default. |
| `Commitlint.FooterRequired` | off | No footer. |
| `Commitlint.FooterMaxLength` | off | Footers over `[max]` characters in all, 1000 by default. |
| `Commitlint.References` | off | No `#123` anywhere in the message. |
| `Commitlint.Trailer` | off | No `Signed-off-by:` trailer, or none matching `[token]`. |
| `Commitlint.Exclamation` | off | A `!` before the colon. |
| `Commitlint.BreakingBang` | off | A `BREAKING CHANGE:` footer with no `!` in the header. |

## Angular

Angular's [guidelines](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md). Goes with `Conventional`.

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `Angular.Type` | error | A type outside `build`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `test`, and `revert`. |
| `Angular.Lowercase` | error | A type with a capital in it. |
| `Angular.Capitalized` | error | A summary that opens with a capitalized word. `URL` and `HttpClient` are names and pass. |
| `Angular.Period` | error | A period at the end of the summary. |
| `Angular.Body` | warning | No body, or one under 20 characters, on any type but `docs`. |
| `Angular.Revert` | error | A `revert:` whose body has no `This reverts commit <SHA>`. |

## Gitmoji

The gitmoji [specification](https://gitmoji.dev/specification). The list is
generated from the project's by `script/gitmoji.py`.

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `Gitmoji.Intention` | error | A subject that does not open with one of the 75 gitmojis, as the emoji or its `:shortcode:`, and a space. |
| `Gitmoji.Message` | error | A gitmoji, an optional scope, and nothing after. |

## EmojiLog

The Emoji-Log [README](https://github.com/ahmadawais/Emoji-Log#getting-started).

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `EmojiLog.Type` | error | A subject that does not open with one of `📦 NEW:`, `👌 IMPROVE:`, `🐛 FIX:`, `📖 DOC:`, `🚀 RELEASE:`, `🤖 TEST:`, `‼️ BREAKING:`. |
| `EmojiLog.Case` | error | A label in the wrong case: `📦 new:`. |

## SevenRules

Chris Beams, [How to Write a Git Commit Message](https://cbea.ms/git-commit/#seven-rules).
The first and fifth rules, the blank line and the imperative, are
`Commits.Blank` and `Commits.Imperative`; the seventh, use the body to
explain what and why, is one a linter cannot hold you to.

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `SevenRules.Limit` | warning | A subject past 50 characters, or past `[max]`. |
| `SevenRules.Truncated` | error | A subject past 72, where GitHub truncates it, or past `[max]`. |
| `SevenRules.Capitalize` | error | A subject that opens in lower case. |
| `SevenRules.Period` | error | A period at the end of the subject. |
| `SevenRules.Wrap` | warning | A body line past 72 characters, URLs exempt. |

## Kernel

The kernel's [Submitting patches](https://www.kernel.org/doc/html/latest/process/submitting-patches.html#describe-your-changes).

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `Kernel.Subsystem` | error | A summary with no `subsystem:` prefix. |
| `Kernel.Length` | warning | A summary past 75 characters, or past `[max]`. |
| `Kernel.Wrap` | warning | An explanation line past 75 columns. Tags are exempt. |
| `Kernel.SignedOff` | error | No `Signed-off-by:` tag. |
| `Kernel.Fixes` | error | A `Fixes:` tag without twelve characters of SHA-1 and the summary in parentheses. |
| `Kernel.Closes` | error | A `Closes:` tag without a URL. |
| `Kernel.Commit` | warning | A commit referred to by fewer than twelve characters of SHA-1, or without its summary. |
| `Kernel.ThisPatch` | warning | `This patch` in the subject or the explanation. `This patch depends on` is the document's own phrase and passes. |

## Go

Go's [contribution guide](https://go.dev/doc/contribute#commit_messages).

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `Go.Package` | error | A first line with no `package:` prefix. |
| `Go.Capital` | warning | A summary that opens with a capitalized word. An identifier keeps its case. |
| `Go.Sentence` | warning | A period at the end of the first line. |
| `Go.Wrap` | warning | A description line past 72 columns, URLs exempt. |
| `Go.Issue` | warning | `Fixes: #123`, `Fix #123`, `Closes #123`: not the `Fixes #123` or `Updates #123` the tracker reads. |

## Jira

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `Jira.Key` | error | No issue key, `PROJ-123`, in the subject. |

## Gitlint

gitlint's [built-in rules](https://jorisroovers.com/gitlint/latest/rules/builtin_rules/)
at their defaults, named after them. The [conversion guide](gitlint.md) maps
every one, including those that need Git rather than the message.

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `Gitlint.TitleMaxLength` | error | T1: a title past 72 characters, or past `[max]`. |
| `Gitlint.TitleTrailingPunctuation` | error | T3: a title ending in `?:!.,;`. |
| `Gitlint.TitleMustNotContainWord` | error | T5: `WIP` as a word in the title; extend `tokens` with more. |
| `Gitlint.TitleMinLength` | error | T8: a title under 5 characters, or under `[min]`. |
| `Gitlint.HardTab` | error | T4 and B3: a tab anywhere. |
| `Gitlint.BodyMaxLineLength` | error | B1: a body line past 80 characters. |
| `Gitlint.BodyTrailingWhitespace` | error | B2: whitespace at the end of a body line. |
| `Gitlint.BodyMinLength` | error | B5: a body under 20 characters, or under `[min]`. |
| `Gitlint.BodyIsMissing` | error | B6: no body. |
| `Gitlint.DisallowCleanupCommits` | off | CC2: a `fixup!`, `squash!`, or `amend!` subject. |

## Committed

committed's [defaults](https://github.com/crate-ci/committed/blob/master/docs/reference.md), named after its keys.

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `Committed.SubjectLength` | error | `subject_length`: a subject past 50 columns, or past `[max]`. |
| `Committed.LineLength` | error | `line_length`: a body line past 72 columns. |
| `Committed.SubjectCapitalized` | error | `subject_capitalized`: a subject, or with the conventional style a description, that opens in lower case. |
| `Committed.SubjectNotPunctuated` | error | `subject_not_punctuated`: a subject ending in punctuation. |
| `Committed.NoFixup` | error | `no_fixup`: a `fixup!`, `squash!`, or `amend!` subject. |
| `Committed.NoWip` | error | `no_wip`: a subject that opens `WIP`. |
| `Committed.MergeCommit` | error | `merge_commit`: a merge commit's message. |
| `Committed.Type` | off | `style = "conventional"` with `allowed_types`: a type outside `fix`, `feat`, `chore`, `docs`, `style`, `refactor`, `perf`, `test`. |

## Conform

conform's [commit policy](https://github.com/siderolabs/conform#commit-policy), named after its checks.

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `Conform.HeaderLength` | error | `header.length`: a header past 89 characters, or past `[max]`. |
| `Conform.HeaderCase` | error | `header.case: lower`: a header that opens with a capital. |
| `Conform.InvalidLastCharacter` | error | `header.invalidLastCharacters: .`: a period at the end. |
| `Conform.Body` | error | `body.required`: no body. |
| `Conform.DCO` | error | `dco`: no `Signed-off-by: Name <email>` trailer. |
| `Conform.Jira` | off | `header.jira.keys`: no key from the listed projects; extend it with yours. |
| `Conform.DescriptionLength` | off | `conventional.descriptionLength`: a description past 72 characters, or past `[max]`. |

## Commitizen

| Rule | Level | What it reports |
| ---- | ----- | --------------- |
| `Commitizen.Type` | error | A type outside `cz_conventional_commits`'s: `build`, `bump`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`. Goes with `Conventional`. |
