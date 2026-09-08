# Spec: Full/Trusted experimental

## Metadata

- Mode: `full`
- Status: `draft`
- Milestone: `A10`
- Planning revision: `2026-09-08`

## Goal

Adicionar backend experimental host Linux com identidade de automação/recursos explícitos, comandos/apps permitidos e concessão por sessão/TTL, depois de provar utilidade A3/A4.

## Requirements

### REQ-001

Adicionar backend experimental host Linux com identidade de automação/recursos explícitos, comandos/apps permitidos e concessão por sessão/TTL, depois de provar utilidade A3/A4.

### REQ-002

Protected paths, broker/egress e emergency stop precisam enforcement OS; perfil inaplicável fica indisponível, nunca Safe renomeado Full com garantia fictícia.

### REQ-003

Conta/ambiente host fixture valida roots, processos e revogação; tentativa de acessar credencial ou processo do usuário fora do grant falha; UI declara riscos residuais reais.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Conta/ambiente host fixture valida roots, processos e revogação; tentativa de acessar credencial ou processo do usuário fora do grant falha; UI declara riscos residuais reais.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Fixtures de OS em ambiente descartável, grants e stop; review crítico do threat model antes de dogfood no host pessoal.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A10 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Root irrestrito, Windows nativo, controle do desktop pessoal ou garantia universal de rollback/confirmar todo efeito.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; tests/test_control_plane.py; docs/SECURITY-MODEL.md.

Fixtures e testes: Fixtures de OS em ambiente descartável, grants e stop; review crítico do threat model antes de dogfood no host pessoal.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A10 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A10.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A10.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
