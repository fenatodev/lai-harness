# Git mutation through guarded shell execution

**Status:** implemented for the v0.4.0-alpha.1 candidate.

The dedicated `git` tool exposes only `changes`, `status`, `diff`, and `diff-staged`. Guarded shell execution now recognizes direct Git invocations and blocks known mutating subcommands before starting `bash`.

## Implemented policy

Git mutation subcommands are blocked in guarded shell execution while common inspection commands remain available. This makes accidental model-driven commits and index/history changes less likely without describing the shell as a sandbox.

Blocked set:

- `add`, `commit`, `am`;
- `merge`, `rebase`, `cherry-pick`, `revert`;
- `tag`, `push`, `fetch`, `pull`;
- `reset`, `clean`, `checkout`, `switch`, `restore`;
- `rm`, `mv`;
- mutating forms of `branch`, `remote`, `config`, `update-ref`, and `symbolic-ref`;
- `init` and `clone`, because they write repository or filesystem state.

Tested inspection set:

- `status`, `diff`, `show`, `log`;
- `rev-parse`, `ls-files`, `grep`, `blame`;
- non-mutating `branch --show-current` and equivalent fixed queries.

## Benefit

The change narrows an inconsistent policy boundary: review through the dedicated tool is read-only, while model-generated shell commands can currently stage or commit. Blocking mutations reduces accidental state changes and makes documentation easier to reason about.

## Compatibility risk

Repository tests sometimes create synthetic Git histories with `git init`, `add`, and `commit`. Those commands would no longer work when requested through the LAI shell tool. Test harnesses invoked outside LAI remain unaffected. User-requested local commits would also require a separate explicitly authorized mechanism rather than generic shell.

Regex-only blocking remains bypassable through scripts, aliases, alternate executables, command construction, or another interpreter. A denylist improvement is defense in depth, not containment.

## Regression tests

- table-driven blocking covers every required mutation plus `fetch`;
- options before subcommands include `git -C path add`, `git -c key=value commit`, and `git --git-dir=... reset`;
- command chains, newlines, and absolute executable paths are covered;
- status, diff, rev-parse, branch inspection, and config reads are allowed;
- mutating branch, remote, and config forms are covered;
- the full project suite verifies that existing validation does not require Git mutation through the agent shell.

The parser is defense in depth, not a complete shell parser or containment boundary. Aliases, wrapper scripts, alternate executables, and indirect interpreter execution remain residual risks. Longer term, prefer structured validation commands or an allowlisted command runner over expanding command detection indefinitely.
