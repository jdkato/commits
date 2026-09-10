# How it works

A commit message has no markup, so to a linter it is a run of lines that
all look the same. The package ships a
[View](https://docs.vale.sh/topics/views), a TextFSM template that reads the
message line by line and names what it finds: the subject, the line after
it, the body, and the trailers. A rule reaches a part by its scope, the way
it reaches a heading in Markdown:

```yaml
extends: existence
message: "A subject does not end with a period."
scope: subject
raw:
  - '\.$'
```

The body is typed as Markdown, so a code span or fence in it is skipped as
it would be anywhere else, and `Vale.Spelling` leaves an identifier in
backticks alone. A trailer block is a paragraph that opens with a `Token:
value` or `Token #ref` line and runs to the next blank line, since a
footer's value may span lines, and a value the template never fills is
still a scope, one empty value at the top of the file, which is where a rule
that requires something reports that it is missing. Lines Git adds as commentary
are never seen, and the scissors line that `commit -v` puts before the diff
ends the read.

[vale.sh/blog/commits](https://vale.sh/blog/commits) walks through the
template.

## The margin

The one exception is line length. Markdown masks a URL, and a rule that
measures a line has to see one to exempt it, so the wrap rules are a
`script` on the raw message that reads it the way the View does, skips the
subject, Git's lines, and the trailer blocks, stops at the scissors line, and
counts every character as a terminal would.

## Shared rules

The conventions agree more than they differ, and where they say the same
thing the rule is written once.
[`Commits/_shared`](../Commits/styles/Commits/_shared) holds the shared
patterns, a period at the end, a capitalized type or description, the
subject's length, a body line past the margin, and a style's rule extends
one with its own message, link, level, and limit:

```yaml
# SevenRules/Limit.yml
extends: Commits._shared.SubjectLength
message: "A subject of %d characters. Shoot for 50; 72 is the hard limit."
link: https://cbea.ms/git-commit/#limit-50
level: warning
max: 50
```

The underscore keeps the directory out of the load, so the parents never
fire on their own. A limit given as `max` or `min` is a parameter, which is
what lets a config set it with the bracket key.

## Off by default

A tool's rule that the tool itself leaves off is off here too, in the
package's own `.vale.ini`: commitlint's beyond `config-conventional`,
gitlint's contrib rule, committed's conventional style, conform's optional
blocks. A user's section turns one on with `= YES`, and the package's
setting never wins over the project's.

## Tests beside the rules

A rule's cases sit in its own file, under `tests:`, and `vale test` runs
each with nothing loaded but that rule. A rule scoped to `subject` needs the
View to have a subject, so each case names it:

```yaml
tests:
  - name: before
    format: COMMIT_EDITMSG
    view: Commit
    input: |
      fix: some message.
    want: |
      1:18:Commitlint.FullStop:A subject does not end with a period.
```

The `view:` key is on Vale's `v3` branch until the next release.
