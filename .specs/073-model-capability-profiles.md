# Spec: Perfis de capacidade e seleção por evidência

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A8`
- Planning revision: `2026-09-08`

## Goal

Versionar perfil por modelo/quantização/runtime/template/hardware/suite/repetições, separando planning/coding/debug/tools/context/patch/latency/refusal/truncation/hallucination/validation.

## Requirements

### REQ-001

Versionar perfil por modelo/quantização/runtime/template/hardware/suite/repetições, separando planning/coding/debug/tools/context/patch/latency/refusal/truncation/hallucination/validation.

### REQ-002

Seleção manual precede router; falta de evidência mantém modelo atual, sem download/cloud/default automático; custo de carga e budget acompanham recomendação.

### REQ-003

Fixture antiga/seis cenários incompletos não decide troca; resultados repetidos produzem perfil reproduzível com unknown explícito; mesma sessão mantém grant ao selecionar modelo.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Fixture antiga/seis cenários incompletos não decide troca; resultados repetidos produzem perfil reproduzível com unknown explícito; mesma sessão mantém grant ao selecionar modelo.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Reusar fixtures model-eval e fake server; evidência real só via endpoint já autorizado e suite fixada em spec, sem claim de superioridade nesta entrega.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A8 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Router automático implementado nesta fatia, benchmark dependente de rede ou troca do modelo padrão.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; model-eval/fixtures-v1.json; tests/test_local_agent.py; docs/MODEL-EVALUATION.md.

Fixtures e testes: Reusar fixtures model-eval e fake server; evidência real só via endpoint já autorizado e suite fixada em spec, sem claim de superioridade nesta entrega.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A8 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A8.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A8.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
