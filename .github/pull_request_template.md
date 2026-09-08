## Summary

## Capability status

Mark any changed capability as one of: implemented, fixture-only, experimental, planned/deferred, out of scope.

## Synthetic reproduction or acceptance criteria

## Validation

Use `lai validation matrix` to choose the risk-proportional evidence for this change.

- [ ] Focused regression or documentation check:
- [ ] `make check`
- [ ] `make lint` when Python/JS/test/hook files changed
- [ ] `make test` or `make test-dev` when runtime behavior changed
- [ ] `make typecheck` when typed modules/hooks changed
- [ ] `make validate` or `make milestone-gate` for release, packaging or milestone freeze
- [ ] No keys, private paths, real logs/state/handoffs, models, prompts, customer data or proprietary source

## Trust-boundary impact

State whether this changes filesystem, shell, Git, sandbox, credentials, network, browser, MCP, external actions, model routing, sessions, delegates, recovery, distribution or release behavior.

## Performance impact

State “not measured” or provide model, hardware, fixture, tokens, tool/API calls and repeated timings.
