# Compared to other tools

Commitizen, cocogitto, and gitmoji-cli write commits, bump versions, and
generate changelogs, and check a message on the side. commitlint, gitlint,
committed, conform, commitsar, and conventional-pre-commit only check. This
package only checks, and is the one rule set here for a linter you may
already run on the docs.

| | Commits (Vale) | commitlint | gitlint | committed | conform | commitizen, cocogitto, commitsar, conventional-pre-commit |
| --- | --- | --- | --- | --- | --- | --- |
| Runtime | Vale | Node | Python | Rust | Go | Python, Rust, Go, Python |
| Conventions | Conventional, Angular, gitmoji, Emoji-Log, the seven rules, kernel, Go, Jira, and each tool's own rule set | Conventional, Angular | Conventional as an add-on | Conventional as a style | Conventional | Conventional |
| Reads | subject, body, and trailers by name | header, body, footer | title and body | subject and lines | header and body | the header |
| Spelling and prose | a dictionary spell check with the body read as Markdown, plus any Vale style | none | none | none | a wordlist of common misspellings | none |
| Needs Git for | nothing | nothing | author checks | author checks | GPG, commit count | nothing |
| Output | Vale's, or any of theirs; see [output.md](output.md) | its own | its own | its own | its own | its own |
| Also writes commits or changelogs | no | no | no | no | no | commitizen and cocogitto yes |

**Choose this when** the message should be held to the same standard as the
docs: a real spell check, house vocabulary, plain language, and any
convention or tool's rule set with one binary and one config. **Keep the
other when** you need what only Git knows, a signature or an author, or the
interactive prompt and release tooling of commitizen or cocogitto; both run
beside Vale without conflict.

## Speed

One message, from a file, the way a hook runs, on an Apple Silicon Mac.
hyperfine, 30 runs after 3 warm-ups:

| Tool | Mean |
| ---- | ---: |
| committed | 3 ms |
| cocogitto | 4 ms |
| Vale, this package | 12 ms |
| conventional-pre-commit | 58 ms |
| Vale, with `Vale.Spelling` on | 85 ms |
| gitlint | 113 ms |
| conform | 146 ms |
| commitizen | 210 ms |
| commitlint | 228 ms |

Vale's 12 ms is the same with one rule or fifty: it is the cost of starting
Vale and reading the config, and a run does everything commitlint does in a
twentieth of the time. Spelling adds a dictionary load, which none of the
others have to pay for.

Where the lines fall is not a matter of taste. Dan Luu's [terminal
latency](https://danluu.com/term-latency/) measurements found that "when
extra latency is A/B tested, people can and do notice latency in the range
we're discussing here," tens of milliseconds. A 2024
[pre-commit-hooks issue](https://github.com/pre-commit/pre-commit-hooks/issues/1069)
reports "about 50 ms" a hook adding up to "~600 ms for all the hooks" as
sluggish. And [prek](https://prek.j178.dev/benchmark/), a rewrite of
pre-commit, benchmarks 13 hooks over 960 files at 135 ms against pre-commit's
1,737 ms and calls the difference the point of the project. The setup here is in
[`script/bench`](../script/bench).
