# From cocogitto, commitsar, and conventional-pre-commit

Three tools that check the Conventional Commits header and stop. Each is
`Conventional` here, with the type list its config held, and the body and
footer rules it never had.

## cocogitto

`cog verify` parses the header; `cog check` does the same over history.
The types come from `cog.toml`:

```toml
[commit_types]
hotfix = { changelog_title = "Hotfixes" }
```

The spec's types and any you add are a style of your own extending
`Commitlint.Type`, as in [wiring.md](wiring.md):

```ini
[COMMIT_EDITMSG]
BasedOnStyles = Commits, Conventional, House
```

`cog verify --ignore-merge-commits --ignore-fixup-commits` is the skip list
in [`script/commit-msg`](../script/commit-msg). `cog bump`, `cog changelog`,
and `cog commit` are not lint and stay with cocogitto; the two run side by
side, cocogitto owning the release and Vale the message.

## commitsar

commitsar checks the commits of a branch against the spec in CI, and
nothing about their bodies. The equivalent run is the loop in
[wiring.md](wiring.md) with `Commits, Conventional` on, and a hook, which
commitsar does not offer, catches the message before it is pushed.

## conventional-pre-commit

A `commit-msg` hook for the pre-commit framework, with the eleven types of
`config-conventional`, `--scopes` for a list, `--force-scope`, and
`--strict` to reject `fixup!` and merges:

```yaml
- repo: https://github.com/compilerla/conventional-pre-commit
  hooks:
    - id: conventional-pre-commit
      stages: [commit-msg]
      args: [--force-scope, --scopes, "api,cli"]
```

becomes the pre-commit form in [wiring.md](wiring.md) with

```ini
[COMMIT_EDITMSG]
BasedOnStyles = Commits, Conventional, Commitlint
Commitlint.ScopeRequired = YES
```

and `Commitlint.Scope` extended with `api` and `cli`. `--strict` is
`Committed.NoFixup` and `Committed.MergeCommit`, on in `Committed`.
