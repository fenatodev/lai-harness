# Spec: Graduação da distribuição

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A12`
- Planning revision: `2026-09-08`

## Goal

Graduar bootstrap A4 com diagnóstico de capabilities, upgrade compatível, rollback de configuração/artefatos e uninstall com política de preservação de dados.

## Requirements

### REQ-001

Graduar bootstrap A4 com diagnóstico de capabilities, upgrade compatível, rollback de configuração/artefatos e uninstall com política de preservação de dados.

### REQ-002

Core permanece stdlib e componentes opcionais/provisionamento são explícitos e verificados; versão desconhecida de estado falha sem apagar dados; um runtime de modelo.

### REQ-003

Smoke clean Linux/WSL2 e upgrade de baseline reproduzem primeiro chat, recovery de componente ausente e downgrade compatível sem secrets/artefatos publicados por engano.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Smoke clean Linux/WSL2 e upgrade de baseline reproduzem primeiro chat, recovery de componente ausente e downgrade compatível sem secrets/artefatos publicados por engano.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Install-smoke, package/publication gate pertinente uma vez no freeze, matriz de contratos Harness/Gateway e registros de plataforma efetivamente testada.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A12 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Marketplace, Windows nativo/macOS certificados, autoupdate, downloads de pesos ou reescrita instalador universal.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: scripts/install-local.sh; tests/test_install_smoke.py; docs/INSTALLATION.md; companion Gateway release/installer.

Fixtures e testes: Install-smoke, package/publication gate pertinente uma vez no freeze, matriz de contratos Harness/Gateway e registros de plataforma efetivamente testada.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A12 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A12.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A12.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
