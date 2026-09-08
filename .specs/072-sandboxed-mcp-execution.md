# Spec: Execução MCP stdio útil

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A7`
- Planning revision: `2026-09-08`

## Goal

Executar servidor stdio escolhido explicitamente no runtime autorizado, fixando identidade/config/tool schema por run; tool fixture gera artefato útil dentro do workspace.

## Requirements

### REQ-001

Executar servidor stdio escolhido explicitamente no runtime autorizado, fixando identidade/config/tool schema por run; tool fixture gera artefato útil dentro do workspace.

### REQ-002

Mapear capabilities por configuração confiável, não hints; aplicar startup/call/output/budget/cancel e ambiente mínimo; config do repo não instala/inicia servidor e v1 continua non-executing.

### REQ-003

Tool autorizada modifica somente artefato fixture; servidor mentiroso, schema alterado, path escape, timeout e canário são bloqueados/registrados, com executed/unknown corretos.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Tool autorizada modifica somente artefato fixture; servidor mentiroso, schema alterado, path escape, timeout e canário são bloqueados/registrados, com executed/unknown corretos.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Fake MCP stdio local, malformed JSON, output flooding e cancellation; fixar revisão de protocolo/SDK antes de ativar; HTTP autenticado fica em follow-up após 063/070/081.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Implementado como adapter `fixture_stdio` sandboxed e hash-bound. Depende dos gates de A7 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta fatia foi concluída após validação focada e suíte ampla.

## Non-Goals

Servidor real privado, OAuth universal, HTTP remoto nesta fatia, sampling/callbacks, auto-install e wildcard tool trust.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/lai_mcp.py; src/local-agent; tests/test_control_plane.py; tests/test_local_agent.py.

Fixtures e testes: Fake MCP stdio local, malformed JSON, output flooding e cancellation; fixar revisão de protocolo/SDK antes de ativar; HTTP autenticado fica em follow-up após 063/070/081.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A7 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A7.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A7.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.


## Evidence

- Focos: MCP fixture execution/status/Gateway contract OK.
- `make check` OK.
- `test_control_plane`: 66 tests OK.
- `make lint && make test`: 362 tests OK.
