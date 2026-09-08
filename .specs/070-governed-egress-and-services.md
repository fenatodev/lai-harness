# Spec: Egress e serviços locais governados

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A6`
- Planning revision: `2026-09-08`

## Goal

Aplicar egress por backend/broker: offline, registries, pesquisa pública e serviços locais registrados, com quotas e identidade de destino; preservar web evidence leve atual.

## Requirements

### REQ-001

Aplicar egress por backend/broker: offline, registries, pesquisa pública e serviços locais registrados, com quotas e identidade de destino; preservar web evidence leve atual.

### REQ-002

Bloquear LAN/loopback/metadata/model/control não concedidos, revalidar DNS/IPv6/redirect/proxy e impedir bypass pelo shell; domínio permitido não é garantia contra exfiltração.

### REQ-003

Fake DNS/rebinding/redirect/metadata e acesso ao host falham; registry/serviço fixture concedido funciona e quotas/cancel fecham novas saídas.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Fake DNS/rebinding/redirect/metadata e acesso ao host falham; registry/serviço fixture concedido funciona e quotas/cancel fecham novas saídas.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Ampliar fake network/web fixtures e integration do runtime A3; provar enforcement efetivo, não só classificação de URL.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A6 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Rede irrestrita por default, browser pessoal ou contas externas autenticadas.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/lai_web.py; src/local-agent; tests/test_web_evidence.py; tests/test_control_plane.py.

Fixtures e testes: Ampliar fake network/web fixtures e integration do runtime A3; provar enforcement efetivo, não só classificação de URL.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A6 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A6.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A6.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
