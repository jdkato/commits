# From conform

conform's commit policy is here under `Conform`, named after its checks and
at the defaults its README shows. What conform reads from Git rather than
the message, signatures and the commit count, is not carried.

## Config

```yaml
# .conform.yaml
policies:
  - type: commit
    spec:
      header:
        length: 89
        imperative: true
        case: lower
        invalidLastCharacters: .
        jira:
          keys: [PROJ, JIRA]
      body:
        required: true
      dco: true
      spellcheck:
        locale: US
      conventional:
        types: [feat, fix, docs]
        descriptionLength: 72
```

becomes

```ini
[COMMIT_EDITMSG]
BasedOnStyles = Vale, Commits, Conventional, Conform
Conform.Jira = YES
Conform.DescriptionLength = YES
```

with a style of your own for the type list, as in
[wiring.md](wiring.md), and the hook from
`conform enforce --commit-msg-file "$1"` to
`vale --path=COMMIT_EDITMSG < "$1"`.

## Every check

| conform | Here |
| ------- | ---- |
| `header.length` | `Conform.HeaderLength`, `[max]` |
| `header.imperative` | `Commits.Imperative` |
| `header.case` | `Conform.HeaderCase`; for `upper`, extend it with `raw` set to `^[a-z]` |
| `header.invalidLastCharacters` | `Conform.InvalidLastCharacter`; for more characters, extend it with a class |
| `header.jira.keys` | `Conform.Jira`, off; extend its `token` with your projects |
| `body.required` | `Conform.Body` |
| `dco` | `Conform.DCO` |
| `spellcheck` | `Vale.Spelling`, which reads the body as Markdown and skips code |
| `conventional.types` | `Conventional`, with `Commitlint.Type` extended for the list |
| `conventional.scopes` | `Commitlint.Scope`, extended for the list |
| `conventional.descriptionLength` | `Conform.DescriptionLength`, off, `[max]` |
| `gpg` | Not carried: a signature is not in the message |
| `maximumOfOneCommit` | Not carried: a count of commits is a question for Git |

## Differences

`script/differential/run.py` runs conform and Vale over one corpus. They
agree on every comparison but one kind: a header conform cannot parse, with
its own regex, is reported there under both Imperative Mood and Header Case,
and here once, by the rule that names what is missing. The rules read as
conform reads: `header.case` is the first character of the description when
a conventional block is configured, and a digit fails it; `body.required`
takes any line after the header that is not a `Signed-off-by:` line as body,
trailers included; and `dco` looks at every line of the message.

conform tags the first word with a part-of-speech tagger and rejects a past
tense, a gerund, or a third-person form. `Commits.Imperative` looks for the
same forms of the common verbs by their endings, and for `This commit` and
`I`, with any prefix skipped first. conform's spellcheck is a wordlist of
common misspellings; Vale's is a dictionary, with the body parsed so that
code is not spelled.

conform's `body.required` looks past `Signed-off-by:` lines; here the
trailers are a scope of their own, so a body is a body.
