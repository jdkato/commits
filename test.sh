#!/bin/sh
#
# Each rule carries its cases in a `tests:` block, run in isolation through
# the Commit View by `vale test`, and each style that mirrors a tool has an
# Upstream.test.yml of that tool's fixtures, run under the root .vale.ini.
# This adds the two checks `vale test` cannot make: that every rule has a
# case that expects an alert, and that the message at HEAD passes the
# convention the repository holds itself to.
#
# The coverage check is the load-bearing one. A Vale rule that matches
# nothing loads, runs, and reports success, so a case can only prove a rule
# works by wanting it -- and a rule no case reaches is indistinguishable from
# one that is broken.
set -eu
status=0

root=$(cd "$(dirname "$0")" && pwd)
vale=${VALE:-vale}

(cd "$root" && "$vale" test Commits/styles) || status=1

# `_shared` holds the parents other rules extend; the loader skips it, so
# nothing there can fire. Every other rule carries its cases in a `tests:`
# block, and at least one of them has to expect an alert: a case that wants
# nothing proves nothing on its own.
missing=$(cd "$root/Commits/styles" && for f in $(find . -name '*.yml' ! -name '*.test.yml' ! -path './config/*' ! -path '*/_shared/*' | sort); do
	if ! grep -q '^tests:' "$f" || ! sed -n '/^tests:/,$p' "$f" | grep -qE '^    (want: \|$|contains:)'; then
		echo "$f" | sed 's|^\./||; s|/|.|; s|\.yml$||'
	fi
done)
if [ -n "$missing" ]; then
	echo "FAIL coverage: no case expects an alert from these rules, so nothing shows they work"
	printf '%s\n' "$missing" | sed 's/^/       /'
	status=1
else
	n=$(cd "$root/Commits/styles" && find . -name '*.yml' ! -name '*.test.yml' ! -path './config/*' ! -path '*/_shared/*' | wc -l | tr -d ' ')
	echo "ok   coverage ($n rules, every one exercised)"
fi

# The message at HEAD is what a push carries; messages Git wrote itself are
# skipped, as the hook skips them.
if git -C "$root" rev-parse --verify HEAD >/dev/null 2>&1; then
	head=$(git -C "$root" log -1 --format=%B)
	case "$head" in
	"Merge "* | "Revert "* | "Reapply "* | "fixup! "* | "squash! "* | "amend! "*)
		echo "skip self-lint (HEAD is a message Git wrote)" ;;
	*)
		self=$(cd "$root" && printf '%s\n' "$head" |
			"$vale" --no-global --no-exit --output=line --path=COMMIT_EDITMSG 2>&1 || true)
		if [ -z "$self" ]; then
			echo "ok   self-lint (HEAD: $(printf '%s' "$head" | head -1))"
		else
			echo "FAIL self-lint: the message at HEAD breaks the repository's own convention"
			printf '%s\n' "$self" | head -5
			status=1
		fi ;;
	esac
fi

exit $status
