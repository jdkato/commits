# Wiring it up

A `commit-msg` hook receives the path of the message file. Vale reads it on
stdin, and `--path` names the section that applies, since the text has no
name of its own:

```sh
#!/bin/sh
# .git/hooks/commit-msg
exec vale --path=COMMIT_EDITMSG < "$1"
```

Vale exits non-zero on an error-level alert, so the commit stops with the
alerts on screen. [`script/commit-msg`](../script/commit-msg) is that hook
with two additions. Messages Git writes itself, merges, reverts, and the
`fixup!` and `squash!` that autosquash reads, are let through, as commitlint
lets them through. And on a fresh clone, where the styles are not there
yet, it runs `vale sync` once, when the `StylesPath` the config names has
no `Commits` directory, so the first commit after a clone fetches the
package and no commit after it does. Lines Git adds as commentary, and the
diff `commit -v` appends, are never seen by a rule.

## For the whole repository

Git keeps `.git/hooks` outside version control, so a hook copied there
protects one clone. To ship it with the repository, put it in a tracked
directory and point `core.hooksPath` at it:

```console
$ git config core.hooksPath script
```

That setting is per clone, so each contributor runs it once, or the
repository runs it for them: a `prepare` script in `package.json`, a
`make setup` target, or the bootstrap step a project already has. The hook
runners below do the same thing under the hood, and the pre-commit
framework installs into `.git/hooks` instead; either way it is a one-time
step per clone. Nothing on the server side can run a hook for a client, so
the check in CI, further down, is the backstop for a clone that skipped it.

## Hook runners

With [husky](https://typicode.github.io/husky/):

```console
$ echo 'vale --path=COMMIT_EDITMSG < "$1"' > .husky/commit-msg
```

With [lefthook](https://lefthook.dev):

```yaml
commit-msg:
  commands:
    vale:
      run: vale --path=COMMIT_EDITMSG < {1}
```

With [pre-commit](https://pre-commit.com):

```yaml
- repo: local
  hooks:
    - id: vale-commit-msg
      name: vale
      entry: sh -c 'vale --path=COMMIT_EDITMSG < "$1"' --
      language: system
      stages: [commit-msg]
```

## CI

Because the message comes in on stdin, the same command works on what was
pushed:

```sh
git log -1 --format=%B | vale --path=COMMIT_EDITMSG
```

On each commit of a pull request, with a checkout deep enough to hold the
range:

```sh
for sha in $(git rev-list "$BASE..HEAD"); do
  git log -1 --format=%B "$sha" | vale --path=COMMIT_EDITMSG || status=1
done
```

And on the request's description, which is a commit message in waiting:

```sh
gh pr view --json body -q .body | vale --path=COMMIT_EDITMSG
```

## Tuning

Levels and toggles work as they do for any Vale rule, and a limit is a
parameter set from the config with the bracket key:

```ini
[COMMIT_EDITMSG]
BasedOnStyles = Commits, Conventional, Commitlint
Commitlint.HeaderLength[max] = 72
Commits.Imperative = error
Conventional.Footer = NO
```

Anything else is authoring, and a rule can be extended in a style of your
own. To accept a type the list does not have, extend the list's rule with
the pattern rewritten and turn the original off:

```yaml
# styles/House/Type.yml
extends: Commitlint.Type
message: "'%s' is not one of ours: build, chore, ci, deps, docs, feat, fix, perf, refactor, revert, style, test."
raw:
  - '^(?!(?i:build|chore|ci|deps|docs|feat|fix|perf|refactor|revert|style|test)(?:[(!:]))\w+(?=(?:\([^()]*\))?!?:)'
```

```ini
[COMMIT_EDITMSG]
BasedOnStyles = Commits, Conventional, Commitlint, House
Commitlint.Type = NO
```
