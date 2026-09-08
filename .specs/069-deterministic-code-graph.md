# Spec: Graph determinístico incremental

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A5`
- Planning revision: `2026-09-08`

## Goal

Resolver primeiro imports/definitions/dependências/test relations Python por AST, com edges de provenance/hash e resolved/heuristic/unknown; retorno bounded integrado ao ranker.

## Requirements

### REQ-001

Resolver primeiro imports/definitions/dependências/test relations Python por AST, com edges de provenance/hash e resolved/heuristic/unknown; retorno bounded integrado ao ranker.

### REQ-002

Cache descartável por root/parser/hashes invalida edit/rename/delete; arquivos excluídos e symlinks não escapam; metadados nunca substituem inspeção.

### REQ-003

Aliases/ciclos/dynamic imports/rename geram relações esperadas sem declarar completude; fixture de descoberta melhora métrica previamente fixada sem piorar correctness.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Aliases/ciclos/dynamic imports/rename geram relações esperadas sem declarar completude; fixture de descoberta melhora métrica previamente fixada sem piorar correctness.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Fixtures de context/semantics e comparação local antes/depois com mesma configuração; JS/TS exige corte/parser separado se AST Python não bastar.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A5 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Embeddings, vector DB, graph completo de linguagens dinâmicas ou broad scanning de arquivos pessoais.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; src/lai_semantics.py; tests/test_local_agent.py; model-eval/fixtures-v1.json.

Fixtures e testes: Fixtures de context/semantics e comparação local antes/depois com mesma configuração; JS/TS exige corte/parser separado se AST Python não bastar.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A5 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A5.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A5.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
