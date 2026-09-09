# Architecture diagrams

These diagrams describe implemented post-A12 behavior. They intentionally exclude A10 trusted-host and A11 computer-use drafts.

## System overview

![System overview](assets/diagrams/system-overview.svg)

```mermaid
flowchart LR
    Developer --> CLI[lai CLI]
    CLI --> Core[src/local-agent]
    Gateway --> ControlPlane[loopback control plane]
    ControlPlane --> Core
    Core --> Model[local OpenAI-compatible model]
    Core --> Records[(XDG records)]
    Core --> Workspace[Safe workspace]
    Core --> Sandbox[Verified sandbox]
```

## Harness and Gateway

![Gateway local-chat flow](assets/diagrams/gateway-local-chat.svg)

```mermaid
sequenceDiagram
    participant G as Gateway/local client
    participant CP as lai control plane
    participant H as Harness runtime
    participant W as Registered workspace
    G->>CP: GET /v1/local-chat/contract
    CP-->>G: version/capabilities
    G->>CP: GET /v1/local-chat/workspaces
    CP-->>G: server-owned workspace_id
    G->>CP: POST /v1/local-chat/runs + CSRF
    CP->>H: enqueue bounded run
    H->>W: inspect or work in safe workspace
    G->>CP: GET events?cursor=N
    CP-->>G: metadata-only events
    G->>CP: GET review
    CP-->>G: diff preview + patch_sha256
    G->>CP: POST promotion + patch_sha256
    CP->>H: Harness-owned promotion path
```

## Control plane

```mermaid
flowchart TD
    Auth[Bearer auth]
    Local[Host/Origin/CSRF for local-chat]
    Router[HTTP route router]
    Runs[Runs and events]
    Sessions[Sessions]
    Review[Review/promotion]
    Authority[Authority/approvals]
    Credentials[Credential broker]
    External[egress/browser/MCP/external actions]

    Auth --> Router
    Local --> Router
    Router --> Runs
    Router --> Sessions
    Router --> Review
    Router --> Authority
    Router --> Credentials
    Router --> External
```

## Execution and security boundary

![Authority and execution boundary](assets/diagrams/authority-execution-boundary.svg)

```mermaid
flowchart LR
    Intent --> Policy{Policy}
    Policy -->|ALLOW| Budget[Budget ledger]
    Policy -->|ASK| Approval[Hash-bound approval intent]
    Policy -->|DENY| Stop[Fail closed]
    Budget --> Sandbox[Verified sandbox / safe workspace]
    Sandbox --> Records[trajectory + audit + metrics]
    Records --> Review[review + promotion proposal]
```

## Context intelligence and model lifecycle

![Context and model lifecycle](assets/diagrams/context-model-lifecycle.svg)

```mermaid
flowchart TD
    Task --> Map[context map]
    Task --> Changes[git changes metadata]
    Task --> Symbols[symbol metadata]
    Task --> Graph[Python AST graph]
    Map --> Ranker[explainable ranking]
    Changes --> Ranker
    Symbols --> Ranker
    Graph --> Ranker
    Ranker --> Prompt[bounded prompt]
    Prompt --> Model[model call]
    Model --> Tool[policy-gated tool]
    Tool --> Validation[validation]
    Tool --> Records[trajectory/budget records]
```

## MCP, browser, egress and external actions

![External boundaries](assets/diagrams/external-boundaries.svg)

```mermaid
flowchart LR
    Web[web search/fetch] --> Egress[Egress broker]
    Browser[fixture_browser] --> Egress
    MCP[fixture_stdio MCP] --> Sandbox[Verified sandbox]
    SecretRef[credential ref] --> FakeGit[fake_git_remote]
    FakeGit --> Receipt[receipt]
    RealAccounts[real external accounts]:::disabled
    RealBrowser[personal browser profile]:::disabled
    classDef disabled fill:#fee2e2,stroke:#991b1b,color:#7f1d1d;
```

## Installation/runtime topology

```mermaid
flowchart TD
    Repo[Source checkout]
    Installer[scripts/install-local.sh]
    Bin[~/.local/bin/lai + local-agent]
    Config[~/.config/lai]
    Data[~/.local/share/lai]
    Model[separate model server]
    Serve[lai serve loopback]
    Gateway[optional Gateway]

    Repo --> Installer --> Bin
    Installer --> Data
    Bin --> Config
    Bin --> Model
    Bin --> Serve
    Gateway --> Serve
```


## Private companion boundary

![Private companion boundary and approved promotion](assets/private-mobile-access.png)

SVG source: [private-mobile-access.svg](assets/private-mobile-access.svg).

This visual describes the companion `lai-gateway` path as a separate private transport around `lai serve`; it does not make PWA, Telegram or Tailscale part of the harness runtime. Promotion remains hash-bound and creates a durable feature worktree instead of changing the active checkout.

## Screenshots

CLI screenshots rendered from real sanitized command output are listed in [Screenshots](SCREENSHOTS.md).
