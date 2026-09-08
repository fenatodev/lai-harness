# Spec: Computer use em desktop dedicado

## Metadata

- Mode: `full`
- Status: `draft`
- Milestone: `A11`
- Planning revision: `2026-09-08`

## Goal

Pilotar screenshot/janelas/mouse/teclado em um desktop/VM dedicado com apps e sessão delimitadas; estado visual limitado e provenance por ação.

## Requirements

### REQ-001

Pilotar screenshot/janelas/mouse/teclado em um desktop/VM dedicado com apps e sessão delimitadas; estado visual limitado e provenance por ação.

### REQ-002

Não usar perfil pessoal nem tecla/click crítico sem intenção verificável; janela/DOM drift exige reavaliação, stop é externo ao modelo e captura exclui secrets.

### REQ-003

Aplicação fixture completa workflow local; troca de janela/captura sensível/prompt injection e cancel impedem ação fora do scope e registram resultado parcial.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Aplicação fixture completa workflow local; troca de janela/captura sensível/prompt injection e cancel impedem ação fora do scope e registram resultado parcial.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Fixtures GUI sintéticas em ambiente dedicado, tolerância de falha/performance registrada antes da ativação; sem contas ou compras reais.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A11 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Automação universal do PC, administração root, desktop nativo do produto ou rollback garantido de GUI.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; companion Gateway activity projection; docs/AUTONOMY-THREAT-MODEL.md.

Fixtures e testes: Fixtures GUI sintéticas em ambiente dedicado, tolerância de falha/performance registrada antes da ativação; sem contas ou compras reais.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A11 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A11.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A11.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
