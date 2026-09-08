# Spec: Skills com requisitos explícitos

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A8`
- Planning revision: `2026-09-08`

## Goal

Evoluir contrato de skill para instruções/contexto/capabilities/tools/validação/saída esperada/version/provenance, preservando loader/fallback legados e schemas progressivos.

## Requirements

### REQ-001

Evoluir contrato de skill para instruções/contexto/capabilities/tools/validação/saída esperada/version/provenance, preservando loader/fallback legados e schemas progressivos.

### REQ-002

Skill não concede grant nem executa hook por instalação; capabilities ausentes são reportadas e code plugin usa boundary de executor, sem privilégios de texto.

### REQ-003

Skill Python debug fixture carrega só contexto necessário e declara validação disponível; skill maliciosa não amplia toolset, instala pacote ou reescreve policy.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Skill Python debug fixture carrega só contexto necessário e declara validação disponível; skill maliciosa não amplia toolset, instala pacote ou reescreve policy.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Ampliar fixtures existentes de skill loading/fallback/mode tools; testar versões desconhecidas e output contract.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A8 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Marketplace, auto-update, plugins host privilegiados ou catálogo amplo antes do dogfood.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; .agents/skills; skills; tests/test_local_agent.py.

Fixtures e testes: Ampliar fixtures existentes de skill loading/fallback/mode tools; testar versões desconhecidas e output contract.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A8 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A8.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A8.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
