# Spec: Computer use em desktop dedicado

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A11`
- Planning revision: `2026-09-08`

## Goal

Pilotar screenshot/janelas/mouse/teclado em um desktop/VM dedicado com apps e sessão delimitadas; estado visual limitado e provenance por ação. A entrega atual é um contrato `fixture_desktop` sintético: não controla desktop real, perfil pessoal, apps reais ou ações críticas sem intenção verificável.

## Requirements

### REQ-001

Pilotar screenshot/janelas/mouse/teclado em um desktop/VM dedicado com apps e sessão delimitadas; estado visual limitado e provenance por ação. A entrega atual é um contrato `fixture_desktop` sintético: não controla desktop real, perfil pessoal, apps reais ou ações críticas sem intenção verificável.

### REQ-002

Não usar perfil pessoal nem tecla/click crítico sem intenção verificável; janela/DOM drift exige reavaliação, stop é externo ao modelo e captura exclui secrets.

### REQ-003

Aplicação fixture completa workflow local por contrato HTTP: sessão dedicada `fixture-notes`, screenshot sanitizado, ação permitida com receipt, drift de janela, captura sensível, tecla crítica sem intenção e cancelamento externo impedem ação fora do scope e registram resultado parcial.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Aplicação fixture completa workflow local por contrato HTTP: sessão dedicada `fixture-notes`, screenshot sanitizado, ação permitida com receipt, drift de janela, captura sensível, tecla crítica sem intenção e cancelamento externo impedem ação fora do scope e registram resultado parcial.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Fixtures GUI sintéticas em ambiente dedicado, tolerância de falha/performance registrada antes da ativação; sem contas ou compras reais.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Contrato experimental implementado como fixture sintética. Depende dos gates de A11 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md) para qualquer desktop real futuro. [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta fatia foi fechada como fixture experimental, sem promover desktop real.

## Non-Goals

Automação universal do PC, administração root, desktop nativo do produto ou rollback garantido de GUI.

## Implementation Notes

Áreas implementadas: `src/local-agent`, `tests/test_control_plane.py`, contrato Gateway v1 aditivo e endpoints `/v1/computer-use/*`. Companion Gateway pode consumir a projeção existente sem receber controle do desktop pessoal.

Fixtures e testes: app local sintético `fixture-notes`, screenshot sanitizado, receipt sem segredo, drift de janela, captura sensível, tecla crítica sem intenção e cancel externo; sem contas ou compras reais.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A11 do backlog. Done desta fatia requer status/rotas/capabilities, screenshot sanitizado, receipt sem segredo, bloqueios adversariais e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A11.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A11.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.

## Validation Evidence

- `python3 -m py_compile src/local-agent tests/test_control_plane.py`
- `.venv/bin/python -m pytest -q tests/test_control_plane.py -k 'gateway_contract or computer_use'`

A11 permanece experimental e fixture-only: desktop pessoal, browser real, perfil pessoal, apps reais e automação crítica continuam indisponíveis.
