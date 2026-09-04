# Context intelligence

LAI Harness uses a small deterministic ranking layer to reduce repository-discovery rounds for constrained local models. It does not replace `read`, `search`, or `inspect`, and ranked files are never treated as already inspected evidence.

## Where it runs

Context intelligence is enabled before inference for:

- `plan`
- `debug`
- `fix`
- `implement`
- `refactor`

`review`, `security`, `test`, selection/explain, and general mode keep their existing context behavior.

Use the same ranking without calling the model:

```bash
lai context "repair parser timeout"
```

The command prints candidate paths, scores, and reason labels only.
## Inventory bounds

The inventory prefers `git ls-files --cached --others --exclude-standard` and falls back to a bounded filesystem walk when Git listing is unavailable or empty.

The default inventory cap is 400 regular files. LAI excludes symlinks and common generated/dependency directories including `.git`, `.specs`, `node_modules`, virtual environments, build output, coverage output, and cache directories. Every candidate must still resolve inside the current repository.

For text relevance, LAI samples at most 32 KiB from supported text/config/code files and skips files larger than 256 KiB. Sampled text is used only to compute a score; it is not copied into the generated context block.

## Ranking signals

Current weights are additive:

- `git_changed`: +60
- `task_path_match`: +50
- `spec_reference`: +45
- `modified`: +35
- `recent`: +18
- `content_match`: +8 per matched task term, capped at +32
- `manifest`: +10

Generic task words are filtered before matching. Identical scores are ordered by repository-relative path, so identical input/state produces stable ordering.
## Prompt contract

At most eight candidates are rendered, within a 1,800-character metadata budget. The block contains only:

- repository-relative path;
- numeric score;
- reason labels.

The active spec itself is excluded from candidate ranking because its normative text is already injected separately. Paths referenced by the active spec can still receive `spec_reference` weight.

Workspace `recent` and `modified` paths are normalized and revalidated before they influence ranking. Live Git and current task signals carry more weight than persisted hints.

## Trust and limitations

Ranking is advisory. Repository filenames and sampled text can influence candidate order, including malicious or misleading content. The model must still inspect a file before relying on its contents, and all existing repository rules, mode gates, policy decisions, validation requirements, and recovery checks remain authoritative.

LAI Harness does not use embeddings, vector databases, external indexing services, MCP, delegates, or learning for this feature. Rankings are recomputed from current local evidence and are not persisted as a separate index.
