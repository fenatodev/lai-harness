# Spec: Shell, processos, dependências e Git local

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A3`
- Planning revision: `2026-09-08`

## Goal

Permitir shell/filesystem/processos/servidores e Git local no repo independente conforme grant, com sessões e handles bounded; instalação nesta fatia usa pacotes fixture locais offline. Registry externo exige adicionalmente o enforcement de egress da spec 070.

## Requirements

### REQ-001

Permitir shell/filesystem/processos/servidores e Git local no repo independente conforme grant, com sessões e handles bounded; instalação nesta fatia usa pacotes fixture locais offline. Registry externo exige adicionalmente o enforcement de egress da spec 070.

### REQ-002

Microações dentro do grant não exigem ASK; outside roots, Git remoto, fonte protegida e instalação host continuam fora dele; shell não recebe credenciais ambientais.

### REQ-003

Tarefa fake edita, instala pacote fixture offline, testa, falha, corrige, retesta e commita isoladamente; nenhuma microaprovação e nenhum efeito na fonte/host; cancel limpa servidor.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Tarefa fake edita, instala pacote fixture offline, testa, falha, corrige, retesta e commita isoladamente; nenhuma microaprovação e nenhum efeito na fonte/host; cancel limpa servidor.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Fixture ponta a ponta determinística com dependência local, Git hooks adversariais e processos; validar diff/promoção/hash/drift existentes.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A3 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Push/merge/release, browser, dependências baixadas no host ou remoção de guards do repositório de desenvolvimento.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; tests/test_control_plane.py; tests/test_guards_integration.py.

Fixtures e testes: Fixture ponta a ponta determinística com dependência local, Git hooks adversariais e processos; validar diff/promoção/hash/drift existentes.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A3 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A3.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A3.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
