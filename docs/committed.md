# From committed

committed's checks are here under `Committed`, named after its config keys
and at its defaults.

## Config

```toml
# committed.toml
subject_length = 72
style = "conventional"
subject_capitalized = false
```

becomes

```ini
[COMMIT_EDITMSG]
BasedOnStyles = Commits, Conventional, Committed
Committed.SubjectLength[max] = 72
Committed.Type = YES
Committed.SubjectCapitalized = NO
```

and the hook, from `committed --commit-file "$1"` to
`vale --path=COMMIT_EDITMSG < "$1"`.

## Every key

| committed | Here |
| --------- | ---- |
| `subject_length` | `Committed.SubjectLength`, `[max]` |
| `line_length` | `Committed.LineLength` |
| `hard_line_length` | `Committed.HardLineLength`, off as it is there; a URL line counts, where `line_length` exempts it |
| `subject_capitalized` | `Committed.SubjectCapitalized` |
| `subject_not_punctuated` | `Committed.SubjectNotPunctuated` |
| `imperative_subject` | `Commits.Imperative` |
| `no_fixup` | `Committed.NoFixup` |
| `no_wip` | `Committed.NoWip` |
| `merge_commit` | `Committed.MergeCommit` |
| `style = "conventional"` | `Conventional`, with `Committed.Type` on for `allowed_types` |
| `allowed_types` | `Committed.Type`; extend it with your list |
| `allowed_scopes` | `Commitlint.Scope`; extend it with your list |
| `ignore_author_re`, `allowed_author_re` | Not carried: the author is commit metadata, not the message |

## Differences

committed checks the imperative with a dictionary of verbs;
`Commits.Imperative` looks for the past tense, the third person, and the
gerund of the common ones, and for `This commit` and `I`. Both are
heuristics; theirs rejects an unknown verb, this one lets it through.

`no_fixup` and `merge_commit` are on, as they are in committed, and make
sense in a run over history, where a leftover `fixup!` means an autosquash
never happened. In a hook they would block the commits autosquash needs, so
[`script/commit-msg`](../script/commit-msg) lets those messages through
before Vale sees them.
