# Output styles

Vale prints alerts in its own format, or as `line` or `JSON`. The package
ships templates for other formats, picked with `--output`; each is a Go
template under `config/templates`, found by name once the package is
synced:

```sh
vale --output=commitlint.tmpl --path=COMMIT_EDITMSG < "$1"
```

| Template | Looks like |
| -------- | ---------- |
| `commitlint.tmpl` | commitlint's report: `✖   message [rule]`, a count of problems and warnings, and a link |
| `gitlint.tmpl` | gitlint's: `1: Rule message: "text"` |
| `committed.tmpl` | committed's: `path: error message` |
| `conform.tmpl` | conform's table: `POLICY  CHECK  STATUS  MESSAGE` |
| `github.tmpl` | GitHub Actions annotations, `::error file=,line=,col=,title=::`, so an alert lands on the pull request |
| `hook.tmpl` | A short form for a hook: the line and column, the message, and the rule and its link underneath |

The commitlint form:

```console
$ vale --output=commitlint.tmpl --path=COMMIT_EDITMSG < .git/COMMIT_EDITMSG
⧗   input: COMMIT_EDITMSG
✖   Start with a type, then a colon: 'fix: ...', 'feat(scope)!: ...'. 'Fixed' is not one. [Conventional.Type]
✖   A subject does not end with a period. [Commitlint.FullStop]
⚠   Write the subject as a command: 'Add', not 'Fixed'. [Commits.Imperative]

✖   found 2 problems, 1 warnings
ⓘ   Get help: https://www.conventionalcommits.org/en/v1.0.0/#specification
```

A template sees each file's path and alerts, with an alert's line, span,
rule, message, severity, matched text, and link, and has the
[sprig](https://masterminds.github.io/sprig/) functions. Copy one into your
own `config/templates` to change it, and pass the path to `--output`.
