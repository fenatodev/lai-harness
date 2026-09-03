# Git mutation through guarded shell execution

**Status:** decision required before implementation in the v0.4 line.

The dedicated `git` tool exposes only `changes`, `status`, `diff`, and `diff-staged`. The separate `bash` tool can still invoke Git commands that are not matched by its denylist. Therefore LAI is not globally Git read-only.

## Recommendation

Block Git mutation subcommands in guarded shell execution while retaining common inspection commands. This makes accidental model-driven commits and index/history changes less likely without describing the shell as a sandbox.

Suggested blocked set:

- `add`, `commit`, `am`;
- `merge`, `rebase`, `cherry-pick`, `revert`;
- `tag`, `push`, `fetch`, `pull`;
- `reset`, `clean`, `checkout`, `switch`, `restore`;
- `rm`, `mv`;
- mutating forms of `branch`, `remote`, `config`, `update-ref`, and `symbolic-ref`;
- `init` and `clone`, because they write repository or filesystem state.

Suggested inspection set:

- `status`, `diff`, `show`, `log`;
- `rev-parse`, `ls-files`, `grep`, `blame`;
- non-mutating `branch --show-current` and equivalent fixed queries.

## Benefit

The change narrows an inconsistent policy boundary: review through the dedicated tool is read-only, while model-generated shell commands can currently stage or commit. Blocking mutations reduces accidental state changes and makes documentation easier to reason about.

## Compatibility risk

Repository tests sometimes create synthetic Git histories with `git init`, `add`, and `commit`. Those commands would no longer work when requested through the LAI shell tool. Test harnesses invoked outside LAI remain unaffected. User-requested local commits would also require a separate explicitly authorized mechanism rather than generic shell.

Regex-only blocking remains bypassable through scripts, aliases, alternate executables, command construction, or another interpreter. A denylist improvement is defense in depth, not containment.

## Required regression tests

- table-driven block tests for every mutating subcommand;
- options before subcommands, such as `git -C path add` and `git --git-dir=... commit`;
- command chains, newlines, and absolute executable paths;
- allowed read commands with common flags;
- aliases and wrapper limitations documented as residual risk;
- existing project validation commands verified not to require Git mutation.

Longer term, prefer structured validation commands or an allowlisted command runner over expanding a regex denylist indefinitely.
