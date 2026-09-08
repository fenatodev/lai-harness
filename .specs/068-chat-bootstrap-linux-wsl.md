# Spec: Bootstrap inicial Linux/WSL2

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A4`
- Planning revision: `2026-09-08`

## Goal

Unir instalador/doctor existentes numa jornada de endpoint local já fornecido, Gateway local, workspace registrado e primeiro chat Safe, com opt-in sandbox apenas quando pronta.

## Requirements

### REQ-001

Unir instalador/doctor existentes numa jornada de endpoint local já fornecido, Gateway local, workspace registrado e primeiro chat Safe, com opt-in sandbox apenas quando pronta.

### REQ-002

Não baixar modelos, iniciar segundo runtime persistente nem instalar componente opcional sem ação explícita; indisponibilidade de Docker/browser não quebra core.

### REQ-003

Smoke em ambiente temporário valida install→configure→open→choose project→chat com fake endpoint; missing backend desabilita só capability pertinente e uninstall preserva dados por padrão.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Smoke em ambiente temporário valida install→configure→open→choose project→chat com fake endpoint; missing backend desabilita só capability pertinente e uninstall preserva dados por padrão.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Reusar install-smoke com diretórios temporários, fake model e Gateway; registrar Linux/WSL2 separadamente sem alegar Windows nativo.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A4 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Marketplace, desktop nativo, runtime Windows, autodownload de pesos ou update automático.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: scripts/install-local.sh; docs/INSTALLATION.md; tests/test_install_smoke.py; companion Gateway installer/doctor.

Fixtures e testes: Reusar install-smoke com diretórios temporários, fake model e Gateway; registrar Linux/WSL2 separadamente sem alegar Windows nativo.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A4 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A4.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A4.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
