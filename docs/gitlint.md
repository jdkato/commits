# From gitlint

gitlint's built-in rules are here under `Gitlint`, named after them and at
their defaults. The core, `Commits`, covers the whitespace and blank-line
rules on its own.

## Config

```ini
# .gitlint
[general]
ignore=B6
[title-max-length]
line-length=50
```

becomes

```ini
[COMMIT_EDITMSG]
BasedOnStyles = Commits, Gitlint
Gitlint.BodyIsMissing = NO
Gitlint.TitleMaxLength[max] = 50
```

and the hook, from `gitlint --msg-filename "$1"` to
`vale --path=COMMIT_EDITMSG < "$1"`. A run over history,
`gitlint --commits main..HEAD`, is a loop over `git log`; see
[wiring.md](wiring.md).

## Every rule

| gitlint | Here |
| ------- | ---- |
| T1 `title-max-length` | `Gitlint.TitleMaxLength`, `[max]` |
| T2 `title-trailing-whitespace`, T6 `title-leading-whitespace` | `Commits.Whitespace` |
| T3 `title-trailing-punctuation` | `Gitlint.TitleTrailingPunctuation` |
| T4 `title-hard-tab`, B3 `body-hard-tab` | `Gitlint.HardTab` |
| T5 `title-must-not-contain-word` | `Gitlint.TitleMustNotContainWord`; extend `tokens` for more words |
| T7 `title-match-regex` | `Gitlint.TitleMatchRegex`, off; extend it with your regex in the lookahead |
| T8 `title-min-length` | `Gitlint.TitleMinLength`, `[min]` |
| B1 `body-max-line-length` | `Gitlint.BodyMaxLineLength` |
| B2 `body-trailing-whitespace` | `Gitlint.BodyTrailingWhitespace` |
| B4 `body-first-line-empty` | `Commits.Blank` |
| B5 `body-min-length` | `Gitlint.BodyMinLength`, `[min]` |
| B6 `body-is-missing` | `Gitlint.BodyIsMissing`; the hook skips merges as gitlint does |
| B7 `body-changed-file-mention` | Not carried: it needs the diff, and a rule sees the message |
| B8 `body-match-regex` | `Gitlint.BodyMatchRegex`, off; extend it with your regex as the `token` |
| M1 `author-valid-email` | Not carried: the author is commit metadata, not the message |
| I1 to I4, the ignore rules | The hook's skip list, or `--glob` for a run over files |
| CT1 `contrib-title-conventional-commits` | `Conventional`, with `Commitlint.Type` for the list |
| CC1 `contrib-body-requires-signed-off-by` | `Kernel.SignedOff` or `Commitlint.Trailer` |
| CC2 `contrib-disallow-cleanup-commits` | `Gitlint.DisallowCleanupCommits`, off; turn on for a run over history |
| CC3 `contrib-allowed-authors` | Not carried: metadata |

A user-defined rule in Python is a YAML rule here, and most of them are an
`existence` with one pattern. What gitlint cannot do, and this can, is read
the body as Markdown and run a spelling or house-style rule on it.
