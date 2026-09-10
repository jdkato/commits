#!/usr/bin/env python3
"""Run the other tools and Vale on one corpus and diff the verdicts, rule by rule.

    $ uv run --with pyyaml script/differential/run.py

Each tool is found on PATH or named by an environment variable: COMMITLINT,
GITLINT, COMMITTED, CONFORM, CZ, COG, CPC. A tool that is missing is skipped.
VALE names the Vale binary, and the package's styles are read from the tree.

For every message, each tool runs with the config its guide says the style
mirrors, and Vale runs with that style. A tool's rule is mapped to the rule
here, and the two verdicts are compared: a disagreement is one firing where
the other did not. The report lists every disagreement, then a table per
tool, and exits 1 if any disagreement is not in the documented list below.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
STYLES = ROOT / "Commits" / "styles"


def tool(env, default):
    return os.environ.get(env) or shutil.which(default)


# --- the corpus ------------------------------------------------------------------

BASE = (
    "feat(parser): add streaming reads\n\n"
    "The parser now reads the input in chunks so a large file does not\n"
    "load into memory at once.\n\n"
    "Fixes #12\nSigned-off-by: Jane Doe <jane@example.com>\n"
)

LONG = "a body line that runs on and on well past every margin any of the tools here would allow it to run to"


def corpus():
    yield "base", BASE
    mutants = {
        "type-unknown": BASE.replace("feat(parser)", "wip(parser)"),
        "type-upper": BASE.replace("feat(parser)", "FEAT(parser)"),
        "type-missing": BASE.replace("feat(parser): ", ""),
        "scope-empty": BASE.replace("(parser)", "()"),
        "scope-upper": BASE.replace("(parser)", "(Parser)"),
        "scope-none": BASE.replace("(parser)", ""),
        "scope-mixed": BASE.replace("(parser)", "(a/b,c)"),
        "no-space": BASE.replace("): add", "):add"),
        "no-description": BASE.replace("feat(parser): add streaming reads", "feat(parser):"),
        "subject-capital": BASE.replace("add streaming", "Add streaming"),
        "subject-upper": BASE.replace("add streaming reads", "ADD STREAMING READS"),
        "subject-period": BASE.replace("streaming reads\n", "streaming reads.\n"),
        "subject-past": BASE.replace("add streaming", "added streaming"),
        "subject-long": BASE.replace("add streaming reads", "add streaming reads to the parser " + "and more " * 10),
        "subject-ws": BASE.replace("streaming reads\n", "streaming reads   \n"),
        "subject-lead-ws": "  " + BASE,
        "bang": BASE.replace("feat(parser):", "feat(parser)!:"),
        "bang-footer": BASE.replace("Fixes #12\n", "BREAKING CHANGE: the reader API changed\nFixes #12\n"),
        "bang-both": BASE.replace("feat(parser):", "feat(parser)!:").replace("Fixes #12\n", "BREAKING CHANGE: the reader API changed\nFixes #12\n"),
        "breaking-lower": BASE.replace("Fixes #12\n", "Breaking change: the reader API changed\nFixes #12\n"),
        "no-blank": BASE.replace("reads\n\nThe", "reads\nThe"),
        "no-body": "feat(parser): add streaming reads\n\nFixes #12\nSigned-off-by: Jane Doe <jane@example.com>\n",
        "short-body": BASE.replace("The parser now reads the input in chunks so a large file does not\nload into memory at once.", "Short."),
        "body-long-line": BASE.replace("load into memory at once.", LONG),
        "body-url-line": BASE.replace("load into memory at once.", "See https://example.com/a/very/long/path/that/runs/on/past/every/margin/there/is/and/then/some/more for it."),
        "body-code-span": BASE.replace("load into memory at once.", "load `a_very_long_identifier_that_runs_on_past_the_margin_of_seventy_two_columns` at once."),
        "body-trailing-ws": BASE.replace("at once.", "at once.  "),
        "body-tab": BASE.replace("at once.", "at\tonce."),
        "footer-glued": BASE.replace("at once.\n\nFixes #12", "at once.\nFixes #12"),
        "footer-long": BASE.replace("Fixes #12\n", "BREAKING CHANGE: " + LONG + "\n"),
        "footer-continued": BASE.replace("Fixes #12\n", "BREAKING CHANGE: the reader\n" + LONG + "\n"),
        "no-signoff": BASE.replace("Signed-off-by: Jane Doe <jane@example.com>\n", ""),
        "signoff-spaces": BASE.replace("Signed-off-by:", "Signed off by:"),
        "no-reference": BASE.replace("Fixes #12\n", ""),
        "only-subject": "feat(parser): add streaming reads\n",
        "wip": "wip\n",
        "fixup": "fixup! " + BASE,
        "merge": "Merge branch 'main' into feature\n",
        "comments": BASE + "# Please enter the commit message for your changes.\n#\tmodified:   parser.go\n",
        "scissors": BASE + "# ------------------------ >8 ------------------------\ndiff --git a/x b/x\n+\t" + LONG + "\n",
        "unicode": BASE.replace("load into memory at once.", "lädt die Datei nicht auf einmal in den Speicher, was gut ist"),
        "note-in-body": BASE.replace("at once.", "at once.\nNote: the old path is kept for a release."),
        "this-commit": BASE.replace("The parser now", "This commit makes the parser"),
    }
    for name, text in mutants.items():
        yield name, text
    for f in sorted(STYLES.glob("*/Upstream.test.yml")):
        for c in yaml.safe_load(f.read_text()) or []:
            yield f"{f.parent.name.lower()}/{c['name']}", c["input"]


# --- the tools -----------------------------------------------------------------

def run(cmd, cwd, stdin=None):
    return subprocess.run(cmd, cwd=cwd, input=stdin, capture_output=True, text=True)


class Tool:
    """A tool, the config it runs with, the Vale style it mirrors, and the map
    from its rule names to ours. `fires(path)` returns the rule names the tool
    reported for the message at path."""

    name = ""
    style = ""      # BasedOnStyles for the Vale run
    toggles = ""    # extra ini lines for the Vale run
    rules = {}      # tool rule -> Vale rule
    files = {}      # config files to write in the work dir

    def __init__(self, work):
        self.work = work
        for fname, body in self.files.items():
            (work / fname).write_text(body)
        # More than one of the tools wants the message inside a repository.
        run(["git", "init", "-q", "."], work)
        self.setup()

    def setup(self):
        pass

    def fires(self, path):
        raise NotImplementedError


class Commitlint(Tool):
    name = "commitlint (config-conventional)"
    style = "Commits, Conventional, Commitlint"
    rules = {
        "type-enum": "Commitlint.Type", "type-case": "Commitlint.TypeCase", "type-empty": "Conventional.Type",
        "subject-empty": "Conventional.Description", "subject-case": "Commitlint.SubjectCase",
        "subject-full-stop": "Commitlint.FullStop", "header-max-length": "Commitlint.HeaderLength",
        "header-trim": "Commits.Whitespace", "body-leading-blank": "Commits.Blank",
        "footer-leading-blank": "Conventional.Footer", "body-max-line-length": "Commitlint.BodyLength",
        "footer-max-line-length": "Commitlint.FooterLength",
    }
    files = {"commitlint.config.js": 'export default { extends: ["@commitlint/config-conventional"] };\n', "package.json": '{"type":"module"}\n'}
    exe = tool("COMMITLINT", "commitlint")

    def setup(self):
        # A config's `extends` resolves from the working directory, so the
        # install the binary came from is linked in beside it.
        modules = Path(self.exe).parent.parent  # node_modules/.bin/commitlint, unresolved
        if modules.name == "node_modules":
            (self.work / "node_modules").symlink_to(modules)

    def fires(self, path):
        r = run([self.exe, "--edit", str(path)], self.work)
        return set(re.findall(r"\[([a-z-]+)\]\s*$", r.stdout + r.stderr, re.M))


class CommitlintAll(Commitlint):
    name = "commitlint (every rule on)"
    toggles = "\n".join(f"Commitlint.{r} = YES" for r in "Scope ScopeRequired ScopeCase HeaderCase HeaderMinLength SubjectLength Body BodyMinLength BodyMaxLength FooterRequired FooterMaxLength References Trailer Exclamation ScopeLength TypeLength BodyCase BodyFullStop".split())
    rules = {**Commitlint.rules,
        "scope-enum": "Commitlint.Scope", "scope-empty": "Commitlint.ScopeRequired", "scope-case": "Commitlint.ScopeCase",
        "header-case": "Commitlint.HeaderCase", "header-min-length": "Commitlint.HeaderMinLength",
        "subject-max-length": "Commitlint.SubjectLength", "subject-min-length": "Commitlint.SubjectLength",
        "body-empty": "Commitlint.Body", "body-min-length": "Commitlint.BodyMinLength", "body-max-length": "Commitlint.BodyMaxLength",
        "footer-empty": "Commitlint.FooterRequired", "footer-max-length": "Commitlint.FooterMaxLength",
        "references-empty": "Commitlint.References", "signed-off-by": "Commitlint.Trailer", "trailer-exists": "Commitlint.Trailer",
        "subject-exclamation-mark": "Commitlint.Exclamation", "scope-max-length": "Commitlint.ScopeLength",
        "scope-min-length": "Commitlint.ScopeLength", "type-max-length": "Commitlint.TypeLength",
        "type-min-length": "Commitlint.TypeLength", "body-case": "Commitlint.BodyCase", "body-full-stop": "Commitlint.BodyFullStop",
    }
    files = {"package.json": '{"type":"module"}\n', "commitlint.config.js": """export default {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "scope-enum": [2, "always", ["api", "cli", "docs"]],
    "scope-empty": [2, "never"],
    "scope-case": [2, "always", "lower-case"],
    "header-case": [2, "always", "lower-case"],
    "header-min-length": [2, "always", 10],
    "subject-max-length": [2, "always", 72],
    "subject-min-length": [2, "always", 1],
    "body-empty": [2, "never"],
    "body-min-length": [2, "always", 20],
    "body-max-length": [2, "always", 1000],
    "footer-empty": [2, "never"],
    "footer-max-length": [2, "always", 1000],
    "references-empty": [2, "never"],
    "signed-off-by": [2, "always", "Signed-off-by:"],
    "trailer-exists": [2, "always", "Signed-off-by:"],
    "subject-exclamation-mark": [2, "never"],
    "scope-max-length": [2, "always", 72],
    "scope-min-length": [2, "always", 1],
    "type-max-length": [2, "always", 72],
    "type-min-length": [2, "always", 1],
    "body-case": [2, "always", "lower-case"],
    "body-full-stop": [2, "never", "."]
  }
};
"""}


class Gitlint(Tool):
    name = "gitlint (defaults)"
    style = "Commits, Gitlint"
    rules = {
        "T1": "Gitlint.TitleMaxLength", "T2": "Commits.Whitespace", "T3": "Gitlint.TitleTrailingPunctuation",
        "T4": "Gitlint.HardTab", "T5": "Gitlint.TitleMustNotContainWord", "T6": "Commits.Whitespace",
        "T8": "Gitlint.TitleMinLength", "B1": "Gitlint.BodyMaxLineLength", "B2": "Gitlint.BodyTrailingWhitespace",
        "B3": "Gitlint.HardTab", "B4": "Commits.Blank", "B5": "Gitlint.BodyMinLength", "B6": "Gitlint.BodyIsMissing",
    }
    files = {".gitlint": "[general]\n"}
    exe = tool("GITLINT", "gitlint")

    def fires(self, path):
        r = run([self.exe, "--msg-filename", str(path)], self.work)
        return set(re.findall(r"^\d+: ([TB]\d) ", r.stdout + r.stderr, re.M))


class Committed(Tool):
    name = "committed (defaults)"
    style = "Commits, Committed"
    # The `type` of each JSON line committed prints; `merge_commit` and
    # `invalid_commit_format` belong to options this run leaves off.
    rules = {
        "subject_too_long": "Committed.SubjectLength", "line_too_long": "Committed.LineLength",
        "capitalize_subject": "Committed.SubjectCapitalized", "no_punctuation": "Committed.SubjectNotPunctuated",
        "wip": "Committed.NoWip", "fixup": "Committed.NoFixup",
    }
    files = {"committed.toml": "merge_commit = true\n"}
    exe = tool("COMMITTED", "committed")

    def fires(self, path):
        r = run([self.exe, "--commit-file", str(path), "--format", "json"], self.work)
        kinds = set()
        for line in (r.stdout + r.stderr).splitlines():
            m = re.search(r'"type":"([a-z_]+)"', line)
            if m:
                kinds.add(m.group(1))
        return kinds


class Conform(Tool):
    name = "conform (README policy)"
    # Commitlint.Type stands in for conform's type list, which is the same
    # eleven here.
    style = "Commits, Conventional, Conform, Commitlint"
    toggles = "Commitlint.Type = YES\nCommitlint.TypeCase = YES\nConform.DescriptionLength = YES"
    rules = {
        "Header Length": "Conform.HeaderLength", "Imperative Mood": "Commits.Imperative",
        "Header Case": "Conform.HeaderCase", "Header Last Character": "Conform.InvalidLastCharacter",
        "DCO": "Conform.DCO", "Commit Body": "Conform.Body",
        "Conventional Commit": "Conventional.Type|Conventional.Space|Conventional.Description|Conventional.Scope|Commitlint.Type|Commitlint.TypeCase|Conform.DescriptionLength",
    }
    files = {".conform.yaml": """policies:
  - type: commit
    spec:
      header:
        length: 89
        imperative: true
        case: lower
        invalidLastCharacters: .
      body:
        required: true
      dco: true
      conventional:
        types: ["build","chore","ci","docs","feat","fix","perf","refactor","revert","style","test"]
        scopes: [".*"]
"""}
    exe = tool("CONFORM", "conform")

    def fires(self, path):
        r = run([self.exe, "enforce", "--commit-msg-file", str(path)], self.work)
        return {m.group(1).strip() for m in re.finditer(r"^commit\s+(.+?)\s{2,}FAILED", r.stdout + r.stderr, re.M)}


class Commitizen(Tool):
    name = "commitizen (cz check)"
    style = "Commits, Conventional, Commitizen"
    rules = {"schema": "Conventional.Type|Conventional.Space|Conventional.Description|Conventional.Scope|Commitizen.Type|Commits.Blank"}
    files = {".cz.toml": '[tool.commitizen]\nname = "cz_conventional_commits"\n'}
    exe = tool("CZ", "cz")

    def fires(self, path):
        r = run([self.exe, "check", "--commit-msg-file", str(path)], self.work)
        return {"schema"} if r.returncode != 0 else set()


TOOLS = [Commitlint, CommitlintAll, Gitlint, Committed, Conform, Commitizen]

def documented(tool, rule, text, theirs):
    """Disagreements the guides describe: a parser reading a message another
    way, not a rule saying something else. Each returns the guide's reason."""
    head = text.split("\n", 1)[0]
    parsed = re.match(r"^\w+(?:\([^()]*\))?!?: \S", head)
    if tool.startswith("Commitlint"):
        if re.match(r"^(?:Merge |fixup! |squash! |amend! |Revert |Reapply )", head):
            return "commitlint ignores merges, reverts, and fixups by default; the hook skips them"
        if rule in ("type-empty", "subject-empty") and not parsed:
            return "commitlint derives type-empty and subject-empty from a header its regex cannot parse; here that is one alert"
        if rule == "type-enum" and "type-case" in theirs:
            return "commitlint reports a capitalized type as both type-case and type-enum; here that is one alert"
        if not parsed:
            return "a header commitlint cannot parse has no type, scope, or subject for its rules to see; here each part is read on its own"
        if rule.startswith(("footer-", "body-", "signed-off-by", "trailer-")) and re.search(r"(?m)^\S.*\n(?:BREAKING CHANGE|[\w-]+)(?:: | #)", text):
            return "commitlint takes any `Token: value` line as the start of the footer; the View takes a trailer block to open a paragraph"
        if re.search(r"(?m)^#", text):
            return "commitlint reads Git's comment lines and the diff as the message; the View reads past them"
    if tool == "Committed":
        if re.match(r"^\s*(?:wip\b|WIP\b|\[WIP\]|Draft\b|\[Draft\]|\(Draft\)|fixup! |squash! |amend! )", head) and rule not in ("wip", "fixup"):
            return "committed stops at a WIP or fixup subject and runs no other check; here each rule reports"
    if tool == "Conform":
        # conform's own header regex: a scope has to hold something.
        if not re.match(r"^\w*(?:\([^)]+\))?!?: .", head) and rule in ("Imperative Mood", "Header Case"):
            return "conform reports a header it cannot parse under Imperative Mood and Header Case; here that is one alert"
        if re.search(r"(?m)^#", text):
            return "conform reads Git's comment lines as the message; the View reads past them"
    if tool == "Commitizen":
        if re.match(r"^(?:Merge |Revert |Pull request|fixup! |squash! |amend! )", head):
            return "cz check skips its allowed prefixes, merges, reverts, and fixups; the hook skips them"
        if head != head.lstrip():
            return "cz check strips the message before matching; here the whitespace is reported"
    return ""


def vale_fires(exe, work, ini, path):
    # The file is named relative to the work directory: a section's glob is
    # matched against the path as given, and `COMMIT_EDITMSG` does not match
    # an absolute one.
    r = run([exe, "--no-global", "--config", str(ini), "--output=line", path.name], work)
    if r.returncode == 2:
        sys.exit(f"vale: {r.stderr.strip() or r.stdout.strip()}")
    return set(re.findall(r"^[^:]+:\d+:\d+:([\w.]+):", r.stdout, re.M))


def matches(pattern, fired):
    """Whether a mapped Vale rule, or any of a `|`-joined set, some with a
    `Style.*` wildcard, fired."""
    for alt in pattern.split("|"):
        if alt.endswith(".*"):
            if any(f.startswith(alt[:-1]) for f in fired):
                return True
        elif alt in fired:
            return True
    return False


def main():
    vale = tool("VALE", "vale")
    messages = list(corpus())
    work = Path(tempfile.mkdtemp())
    shutil.copytree(STYLES, work / "styles")

    # The package's own section turns its optional rules off; those lines
    # go into each run's config, and a tool's `toggles` turn some back on.
    pkg = (ROOT / "Commits" / ".vale.ini").read_text()
    off = "\n".join(l for l in pkg[pkg.index("[COMMIT_EDITMSG]"):].splitlines() if " = NO" in l)

    status = 0
    for cls in TOOLS:
        if not cls.exe:
            print(f"skip {cls.name}: not installed")
            continue
        tdir = work / cls.__name__
        tdir.mkdir()
        t = cls(tdir)
        ini = tdir / ".vale.ini"
        ini.write_text(f"StylesPath = ../styles\nMinAlertLevel = suggestion\n\n[COMMIT_EDITMSG]\nBasedOnStyles = {t.style}\nView = Commit\n{off}\n{t.toggles}\n")

        agree = disagree = 0
        unmapped = set()
        rows = []
        fired_theirs = fired_ours = 0
        explained = {}
        for name, text in messages:
            path = tdir / "COMMIT_EDITMSG"
            path.write_text(text)
            theirs = t.fires(path)
            ours = vale_fires(vale, tdir, ini, path)
            fired_theirs += len(theirs)
            fired_ours += len(ours)
            for rule in theirs:
                if rule not in t.rules:
                    unmapped.add(rule)
            # Two of a tool's rules can map to one of ours (a min and a max
            # length), so the comparison is per rule of ours: did any of the
            # tool's rules for it fire, and did it.
            groups = {}
            for rule, ours_rule in t.rules.items():
                if ours_rule is not None:
                    groups.setdefault(ours_rule, []).append(rule)
            for ours_rule, rules in groups.items():
                fired = [r for r in rules if r in theirs]
                a, b = bool(fired), matches(ours_rule, ours)
                if a == b:
                    agree += 1
                    continue
                disagree += 1
                why = documented(cls.__name__, fired[0] if fired else rules[0], text, theirs)
                if why:
                    explained[why] = explained.get(why, 0) + 1
                    continue
                status = 1
                rows.append((name, "/".join(fired or rules), ours_rule, "they fire" if a else "we fire"))
        # A tool that never fires on a corpus built to make it fire is a
        # broken setup, and two empty verdicts agree with each other.
        if not fired_theirs or not fired_ours:
            sys.exit(f"{t.name}: {'the tool' if not fired_theirs else 'vale'} reported nothing over the whole corpus")
        print(f"\n== {t.name}: {agree} agree, {disagree} disagree over {len(messages)} messages, {len(rows)} unexplained")
        for why, n in sorted(explained.items(), key=lambda kv: -kv[1]):
            print(f"   {n:3d}  documented: {why}")
        for row in rows:
            print("   %-28s %-26s %-28s %s" % row)
        if unmapped:
            print("   unmapped:", ", ".join(sorted(unmapped)))
    shutil.rmtree(work)
    sys.exit(status)


if __name__ == "__main__":
    main()
