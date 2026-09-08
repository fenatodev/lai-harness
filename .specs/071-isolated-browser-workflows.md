# Spec: Browser isolado e workflows bounded

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A6`
- Planning revision: `2026-09-08`

## Goal

Executar browser isolado com perfil descartável, navegação/extract/screenshots e aplicação local fixture; downloads em quarentena com size/type/TTL.

## Requirements

### REQ-001

Executar browser isolado com perfil descartável, navegação/extract/screenshots e aplicação local fixture; downloads em quarentena com size/type/TTL.

### REQ-002

Sandbox do browser permanece ativa; egress/grants/credentials governam efeitos; preview e UI de autoridade têm origens diferentes; ação crítica ambígua exige adapter/humano.

### REQ-003

Página fixture solicita secret/controle, popup/redirect muda destino e DOM muda antes de submit: não obtém autoridade nem efeito crítico não aprovado; screenshot é bounded/sanitizada.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Página fixture solicita secret/controle, popup/redirect muda destino e DOM muda antes de submit: não obtém autoridade nem efeito crítico não aprovado; screenshot é bounded/sanitizada.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Fixtures locais sem contas reais para navegação, downloads, prompt injection e cancel; qualquer workflow autenticado depende adicionalmente de 081/adapters próprios.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A6 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Perfil pessoal, computer use, compra/envio real ou prometer atomicidade de click genérico.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; src/lai_web.py; tests/test_control_plane.py; companion Gateway activity projection.

Fixtures e testes: Fixtures locais sem contas reais para navegação, downloads, prompt injection e cancel; qualquer workflow autenticado depende adicionalmente de 081/adapters próprios.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A6 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A6.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A6.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
