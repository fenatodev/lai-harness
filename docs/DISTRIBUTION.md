# Distribution, upgrade and uninstall

Distribution support is diagnostic and local. It does not publish releases or update the host automatically.

## Installed state

`install-local.sh` writes schema-versioned state under:

```text
$LAI_DATA_DIR/distribution/installed-state.json
```

The state records installed components, current/previous harness version, one-model-runtime policy, publication non-effects and rollback metadata for replaced local artifacts.

## Inspect state

```bash
lai distribution status
lai distribution status --json
```

The command is metadata-only. It does not contact the model, download models, install optional components, start a browser, create tags, push, publish a VSIX or perform autoupdate.

Future unknown state schemas fail closed and preserve existing data/config.

## Repeat install and rollback metadata

A repeat local install backs up previous installed binaries under:

```text
$LAI_DATA_DIR/distribution/rollback/previous
```

Rollback metadata is local evidence for the operator. It is not a GitHub release rollback or remote deployment mechanism.

## Uninstall

`install-local.sh` installs `lai-uninstall`. Running it without flags removes installed binaries and preserves config/data/distribution state. Use `--delete-data` only for explicit local state removal.
