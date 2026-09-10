# Speed comparison

`msg.txt` is the message every tool linted. Each tool was installed on its
own runtime and pointed at its default Conventional Commits rules; Vale
ran `Commits, Conventional, Commitlint` through the package's View.
`results.md` is hyperfine's output.

```sh
hyperfine --warmup 3 --runs 30 -N \
  'vale --no-global --path=COMMIT_EDITMSG msg.txt' \
  'node node_modules/.bin/commitlint --edit msg.txt' \
  'gitlint --msg-filename msg.txt' \
  'cz check --commit-msg-file msg.txt' \
  'committed --commit-file msg.txt' \
  'conform enforce --commit-msg-file msg.txt' \
  'cog verify --file msg.txt' \
  'conventional-pre-commit msg.txt'
```

Configs used: commitlint's `config-conventional`; gitlint's defaults with
B6 off; committed with `style = "conventional"`, `subject_length = 72`, and
`subject_capitalized = false`; conform with the README's header, body, DCO,
and conventional blocks and `scopes: [".*"]`; commitizen's
`cz_conventional_commits`; cocogitto and conventional-pre-commit as
installed.

## Where Vale's time goes

Profiled with `VALE_CPUPROFILE` over 120 runs of the command above with
`Commits, Conventional, Commitlint` on, 34 rules loaded. Of a 12 ms run,
about 8 ms is process start: a 43 MB binary carrying tree-sitter grammars,
and 3.4 ms of package initializers, where an empty Go program starts in
2 ms. The rest is reading the config and the rule files, compiling the
rules' regexes, and building the linter; the lint itself is under a
millisecond. Rule count barely moves the total.

An earlier draft of this page reported 26 ms. That was a measurement made
while the machine was busy, and every later run under quiet conditions gave
12.
