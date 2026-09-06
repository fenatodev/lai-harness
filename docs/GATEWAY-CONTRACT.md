# Gateway contract

`lai gateway-contract --json` and authenticated `GET /v1/gateway-contract` expose a stable machine-readable contract for companion gateways such as `lai-gateway`.

The contract exists so a private PWA, Telegram bridge, or Tailscale-facing adapter can discover the harness boundary without scraping README prose or hard-coding endpoint assumptions. The gateway remains a separate project; messaging credentials, user mapping, notification delivery, and transport exposure do not belong in `lai-harness`.

## Local CLI

```bash
lai gateway-contract --json
```

The local CLI command is deterministic and does not call the model server. It includes product/version, schema version, supported control-plane routes, run modes, request/session/run limits, companion expectations, and explicit forbidden capabilities.

## HTTP endpoint

```http
GET /v1/gateway-contract
Authorization: Bearer <control-api-token>
```

The endpoint is served by `lai serve` and uses the same bearer-authenticated JSON boundary as the rest of the control plane. It is still loopback-only; a private gateway may proxy it, but the harness does not bind to LAN, tailnet, or public addresses.

## Secret boundary

The payload must not include bearer tokens, model API keys, secret file contents, host environment variables, private run transcripts, or persistent-session turn bodies. Gateways must keep the control bearer token server-side and must not send it to browsers, chat clients, logs, or model prompts.

## Explicit non-authority

The contract does not grant generic remote shell, direct source-checkout writes, dependency installation, commit/push/merge/PR authority, tag/release publication, browser automation, JavaScript execution, direct llama.cpp exposure, or token disclosure.

Schema file: [`schemas/runtime/gateway_contract.schema.json`](../schemas/runtime/gateway_contract.schema.json).
