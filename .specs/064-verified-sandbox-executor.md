# Spec: Executor inteiro em sandbox Linux/WSL2

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A3`
- Planning revision: `2026-09-08`

## Goal

Executar toda atividade de projeto em um backend Linux/WSL2 verificado, com imagem/toolchain por digest, clone/cópia independente e supervisor fora da fronteira.

## Requirements

### REQ-001

Executar toda atividade de projeto em um backend Linux/WSL2 verificado, com imagem/toolchain por digest, clone/cópia independente e supervisor fora da fronteira.

### REQ-002

Provar ambiente mínimo, mounts mínimos, ausência de sockets/secrets, usuário sem root, limites CPU/memória/PIDs/disco/tempo e cleanup; falta de enforcement recusa perfil sem fallback host.

### REQ-003

Markers externos, symlink race, hooks, fork/detach e daemon access são contidos; cancel termina descendentes e fonte/estado de autoridade permanecem intactos.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Markers externos, symlink race, hooks, fork/detach e daemon access são contidos; cancel termina descendentes e fonte/estado de autoridade permanecem intactos.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Reusar fixtures de workspace/control plane; adicionar integration fixtures de container provisionado explicitamente, com skip separado de evidência de readiness.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A3 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Múltiplos backends, Windows nativo, VM manager, imagem puxada automaticamente ou socket Docker dentro da tarefa.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; tests/test_control_plane.py; docs/SAFE-WORKSPACES.md.

Fixtures e testes: Reusar fixtures de workspace/control plane; adicionar integration fixtures de container provisionado explicitamente, com skip separado de evidência de readiness.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A3 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A3.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A3.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
