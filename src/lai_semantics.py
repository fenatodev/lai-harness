from __future__ import annotations

import json
import re
import unicodedata
from typing import TypedDict


class SemanticSubsystem(TypedDict):
    id: str
    intent: str
    paths: list[str]
    entrypoints: list[str]
    terms: list[str]


class SemanticCodeContract(TypedDict):
    name: str
    purpose: str
    rules: list[str]
    subsystems: list[SemanticSubsystem]


SEMANTIC_CODE_CONTRACT: SemanticCodeContract = {
    "name": "lai harness code semantics",
    "purpose": (
        "Make the repository easier for small local models to navigate by "
        "declaring stable domain terms, subsystem intent, and canonical files."
    ),
    "rules": [
        "semantic contracts are advisory metadata, not inspected evidence",
        "canonical ids remain stable across public lowercase renames",
        "runtime behavior must stay covered by tests before a semantic rename ships",
    ],
    "subsystems": [
        {
            "id": "configuration",
            "intent": "resolve CLI, environment, TOML, XDG paths, server, and model settings",
            "paths": ["src/lai_config.py", "src/local-agent", "src/lai", "docs/CONFIGURATION.md"],
            "entrypoints": ["load_configuration", "render_config_status", "doctor_status"],
            "terms": ["config", "configuration", "toml", "env", "xdg", "server", "host", "port", "model", "api", "key", "doctor"],
        },
        {
            "id": "policy-gateway",
            "intent": "classify tool calls as ALLOW, ASK, or DENY before execution",
            "paths": ["src/local-agent", "docs/SECURITY-MODEL.md", ".agents/rules/core-safety.md"],
            "entrypoints": ["evaluate_tool_policy", "git_mutation_in_shell", "render_policy_check", "render_policy_result"],
            "terms": ["policy", "approval", "allow", "ask", "deny", "bash", "git", "mutation", "safety", "security"],
        },
        {
            "id": "tool-runtime",
            "intent": "execute bounded repository tools for read, write, structured validation, shell, and git inspection",
            "paths": ["src/local-agent", "docs/ARCHITECTURE.md", "docs/MODES.md", "docs/CONTROL-PLANE.md"],
            "entrypoints": ["run_tool", "tool_read", "tool_search", "tool_patch", "tool_validate", "tool_bash", "tool_git", "remote_validation_docker_argv"],
            "terms": ["tool", "runtime", "read", "search", "inspect", "patch", "rewrite", "validate", "sandbox", "workspace", "bash", "git", "validation"],
        },
        {
            "id": "semantic-code-contracts",
            "intent": "declare typed repository navigation metadata and semantic matching helpers outside the monolithic runtime",
            "paths": ["src/lai_semantics.py", "src/local-agent", "docs/SEMANTIC-CODE-CONTRACTS.md"],
            "entrypoints": ["semantic_code_contract_payload", "render_semantic_code_contract", "context_semantic_references"],
            "terms": ["semantic", "semantics", "contract", "contracts", "navigation", "subsystem", "canonical", "metadata", "ranking"],
        },
        {
            "id": "context-intelligence",
            "intent": "rank likely files for a task without treating candidates as evidence",
            "paths": ["src/local-agent", "docs/CONTEXT-INTELLIGENCE.md"],
            "entrypoints": ["rank_context_candidates", "render_context_candidates", "print_context_candidates"],
            "terms": ["context", "ranking", "candidate", "inventory", "semantic", "terms", "workspace", "recent", "modified"],
        },
        {
            "id": "spec-workflow",
            "intent": "load active specs, enforce traceability, and inject implementation requirements",
            "paths": ["src/lai_specs.py", "src/local-agent", ".specs/README.md", "docs/DESIGN-DECISIONS.md"],
            "entrypoints": ["parse_spec", "load_active_spec", "render_active_spec_context"],
            "terms": ["spec", "requirements", "traceability", "workflow", "status", "acceptance", "validation"],
        },
        {
            "id": "model-evaluation",
            "intent": "compare local coding models with versioned disposable fixtures, independent validation, runtime evidence, repeated samples, and scoring",
            "paths": ["src/local-agent", "model-eval/fixtures-v1.json", "docs/MODEL-EVALUATION.md", "docs/MODEL-BAKEOFF-2026-09-05.md"],
            "entrypoints": ["render_model_evaluation_plan", "run_model_evaluation", "run_model_evaluation_fixture", "render_model_evaluation_score"],
            "terms": ["model", "evaluation", "benchmark", "fixture", "score", "scenario", "repeat", "latency", "tokens", "hallucination", "validation", "truncation"],
        },
        {
            "id": "update-intelligence",
            "intent": "observe trusted dependency and reference-agent metadata, then triage structured maintenance evidence without automatic mutation",
            "paths": ["src/local-agent", "updates/sources-v1.json", "docs/UPDATE-INTELLIGENCE.md"],
            "entrypoints": ["render_update_plan", "run_update_check", "render_update_latest", "render_update_triage", "handle_update_intelligence"],
            "terms": ["update", "upstream", "dependency", "release", "version", "vulnerability", "security", "radar", "triage", "urgency", "maintenance", "compatibility", "dependabot", "pypi", "npm", "provenance"],
        },
        {
            "id": "observability-recovery",
            "intent": "record metrics, audit events, checkpoints, workspace status, and recovery state",
            "paths": ["src/local-agent", "docs/OBSERVABILITY.md", "docs/RECOVERY.md"],
            "entrypoints": ["record_metric_event", "record_audit_event", "save_run_checkpoint", "render_recovery_context"],
            "terms": ["metrics", "audit", "checkpoint", "recovery", "resume", "handoff", "workspace", "status"],
        },
        {
            "id": "run-history",
            "intent": "list and inspect recorded local runs without replaying actions or calling the model",
            "paths": ["src/local-agent", "docs/RUN-HISTORY.md", "docs/OBSERVABILITY.md"],
            "entrypoints": ["collect_run_history", "render_run_history_list", "render_run_history_show", "render_run_history_tail"],
            "terms": ["run", "runs", "history", "session", "browser", "show", "tail", "last", "failure", "validation", "audit", "metrics", "timeline"],
        },
        {
            "id": "run-export",
            "intent": "write a sanitized local diagnostic bundle for one recorded run without replaying actions or exposing raw logs",
            "paths": ["src/local-agent", "docs/RUN-HISTORY.md", "docs/OBSERVABILITY.md"],
            "entrypoints": ["render_run_history_export", "write_run_history_export", "sanitize_run_history_export_event"],
            "terms": ["run", "export", "bundle", "diagnostic", "summary", "timeline", "report", "sanitized", "evidence"],
        },
        {
            "id": "release-preflight",
            "intent": "preload release readiness facts and preferred project validation commands for small local models",
            "paths": ["src/local-agent", "src/lai", ".agents/skills/release/SKILL.md", "docs/READINESS.md"],
            "entrypoints": ["render_release_preflight_context", "render_release_check", "release_validation_commands", "collect_readiness_status"],
            "terms": ["release", "preflight", "check", "readiness", "validate", "make", "version", "tag", "branch", "beta"],
        },
        {
            "id": "release-pack",
            "intent": "write a local release publication pack without tagging, pushing, uploading, or publishing",
            "paths": ["src/local-agent", "src/lai", "docs/RELEASE-PACK.md", "docs/RELEASE-NOTES.md", "docs/RELEASE-CHECKLIST.md"],
            "entrypoints": ["render_release_pack", "write_release_pack", "release_pack_payload", "release_pack_files"],
            "terms": ["release", "pack", "package", "github", "body", "notes", "checklist", "vsix", "artifact", "publish"],
        },
        {
            "id": "release-governance",
            "intent": "summarize local release readiness and optionally verify GitHub release governance read-only",
            "paths": ["src/local-agent", "src/lai", "docs/RELEASE-GOVERNANCE.md", "docs/RELEASE-CHECKLIST.md"],
            "entrypoints": ["render_release_governance", "collect_release_governance", "collect_github_release_governance", "release_governance_pack_status"],
            "terms": ["release", "governance", "publication", "branch", "protection", "github", "manual", "pre-release", "status"],
        },
        {
            "id": "project-handoff",
            "intent": "produce a portable next-chat project handoff without model calls or repository mutation",
            "paths": ["src/local-agent", "src/lai", "docs/PROJECT-HANDOFF.md", "docs/RELEASE-GOVERNANCE.md"],
            "entrypoints": ["render_project_handoff", "write_project_handoff", "project_handoff_payload"],
            "terms": ["handoff", "next", "chat", "session", "context", "continuity", "transfer", "summary", "reference"],
        },
        {
            "id": "operational-readiness",
            "intent": "check repository, server, skills, run history, and release posture before a work session",
            "paths": ["src/local-agent", "docs/READINESS.md", "docs/MODES.md", ".agents/skills/diagnose/SKILL.md", ".agents/skills/ci-fix/SKILL.md", ".agents/skills/release/SKILL.md"],
            "entrypoints": ["collect_readiness_status", "render_readiness_status", "load_mode_skill"],
            "terms": ["readiness", "ready", "diagnose", "ci", "release", "skill", "mode", "environment", "server", "git", "health"],
        },
        {
            "id": "safe-workspace",
            "intent": "create and clean disposable dogfood copies so write modes can be tested away from protected branches",
            "paths": ["src/local-agent", "src/lai", "docs/SAFE-WORKSPACES.md", "docs/PROTECTED-BRANCH-WRITES.md"],
            "entrypoints": ["handle_safe_workspace", "create_safe_workspace", "render_safe_workspace_status", "clean_safe_workspace"],
            "terms": ["workspace", "safe", "dogfood", "smoke", "clone", "copy", "branch", "main", "protected", "clean"],
        },
        {
            "id": "remote-sessions",
            "intent": "persist bounded repository-scoped remote conversation context without granting historical text authority over current evidence",
            "paths": ["src/lai_sessions.py", "src/local-agent", "schemas/runtime/control_session.schema.json", "docs/CONTROL-PLANE.md"],
            "entrypoints": ["create_control_session", "load_control_session", "append_control_session_turn", "render_control_session_task", "control_submit_run"],
            "terms": ["session", "persistent", "remote", "conversation", "turn", "history", "context", "gateway", "telegram", "pwa", "continuity"],
        },
        {
            "id": "local-control-plane",
            "intent": "expose authenticated loopback JSON status and bounded shell-free asynchronous model runs for external gateways",
            "paths": ["src/local-agent", "src/lai", "docs/CONTROL-PLANE.md", "docs/SECURITY-MODEL.md"],
            "entrypoints": ["run_control_server", "create_control_server", "LaiControlRequestHandler", "control_submit_run", "control_cancel_run", "render_control_token"],
            "terms": ["control", "serve", "http", "json", "bearer", "token", "loopback", "mobile", "gateway", "status", "readiness", "runs", "async", "queue", "cancel", "plan", "review"],
        },
        {
            "id": "extension-shell",
            "intent": "connect VS Code chat requests to the local CLI while preserving workspace safety",
            "paths": ["vscode-extension/extension.js", "vscode-extension/package.json", "vscode-extension/README.md"],
            "entrypoints": ["activate", "resolveAgentPath", "runAgent"],
            "terms": ["vscode", "extension", "chat", "participant", "selection", "workspace", "agent", "command"],
        },
        {
            "id": "installation-publication",
            "intent": "install local binaries, package the VSIX, and validate release artifacts",
            "paths": ["scripts/install-local.sh", "scripts/validate.sh", "scripts/package-vsix.sh", "docs/INSTALLATION.md", "docs/GITHUB-PUBLISHING.md"],
            "entrypoints": ["install-local.sh", "validate.sh", "package-vsix.sh"],
            "terms": ["install", "package", "vsix", "publication", "release", "ci", "validate", "publishing"],
        },
    ],
}


CONTEXT_STOPWORDS: set[str] = {
    "the", "and", "for", "with", "from", "this", "that", "into", "add",
    "fix", "make", "change", "update", "create", "repair", "test", "tests",
    "file", "files", "code", "repo", "repository", "project", "task",
    "inspect", "search", "context", "src", "para", "com", "arquivo", "arquivos",
    "codigo", "projeto", "teste", "testes",
    "uma", "um", "que", "por", "dos", "das", "de", "do", "da", "sem",
}


def semantic_code_contract_payload(product: str, version: str) -> dict[str, object]:
    return {
        "product": product,
        "version": version,
        "contract": SEMANTIC_CODE_CONTRACT,
    }


def render_semantic_code_contract(product: str, version: str, json_mode: bool = False) -> str:
    payload = semantic_code_contract_payload(product, version)
    if json_mode:
        return json.dumps(payload, indent=2, sort_keys=True)

    lines = [
        "# lai code semantics",
        f"Version: {version}",
        "",
        "Purpose:",
        f"- {SEMANTIC_CODE_CONTRACT['purpose']}",
        "",
        "Rules:",
    ]
    lines.extend(f"- {rule}" for rule in SEMANTIC_CODE_CONTRACT["rules"])
    lines.extend(["", "Subsystems:"])
    for subsystem in SEMANTIC_CODE_CONTRACT["subsystems"]:
        lines.append(f"- {subsystem['id']}: {subsystem['intent']}")
        lines.append("  - paths: " + ", ".join(subsystem["paths"]))
        lines.append("  - entrypoints: " + ", ".join(subsystem["entrypoints"]))
        lines.append("  - terms: " + ", ".join(subsystem["terms"]))
    return "\n".join(lines)


def _fold_text(value: object) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", str(value or ""))
        if not unicodedata.combining(char)
    ).lower()


def _semantic_contract_tokens(subsystem: SemanticSubsystem) -> set[str]:
    values = [
        subsystem["id"],
        " ".join(subsystem["entrypoints"]),
        " ".join(subsystem["terms"]),
    ]
    tokens: set[str] = set()
    for value in values:
        folded = _fold_text(value)
        for token in re.split(r"[^a-z0-9]+", folded):
            if len(token) >= 3 and token not in CONTEXT_STOPWORDS:
                tokens.add(token)
    return tokens


def context_semantic_references(terms: list[str], inventory: list[str]) -> dict[str, list[str]]:
    if not terms or not inventory:
        return {}
    known_paths = set(inventory)
    references: dict[str, list[str]] = {}
    for subsystem in SEMANTIC_CODE_CONTRACT["subsystems"]:
        contract_terms = _semantic_contract_tokens(subsystem)
        if not any(term in contract_terms for term in terms):
            continue
        for rel in subsystem["paths"]:
            if rel in known_paths:
                references.setdefault(rel, []).append(subsystem["id"])
    return references
