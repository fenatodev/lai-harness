# Spec: Validação proporcional e matriz justificada

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A12`
- Planning revision: `2026-09-08`

## Goal

Inventariar checks/evidência/custo e propor eliminar repetições equivalentes sem remover regressões, stdlib-runtime smoke, typing, lint ou publication signal necessários.

## Requirements

### REQ-001

Inventariar checks/evidência/custo e propor eliminar repetições equivalentes sem remover regressões, stdlib-runtime smoke, typing, lint ou publication signal necessários.

### REQ-002

Justificar piso Python 3.11 por tomllib e versão adicional suportada; required-check IDs/runtime release governance/documentação/testes evoluem juntos; remote settings continuam ação separada.

### REQ-003

Fixture de falha em cada classe continua quebrando gate; matriz/contrato identifica checks esperados; comparação mostra menos trabalho duplicado com a mesma cobertura exigida.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Fixture de falha em cada classe continua quebrando gate; matriz/contrato identifica checks esperados; comparação mostra menos trabalho duplicado com a mesma cobertura exigida.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Tests de quality sensors/GitHub hardening/release checks, CI fixture e Makefile dependency inspection; freeze gate completo uma vez após mudança real.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A12 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Enfraquecer teste, alterar proteção remota automaticamente, reduzir matriz só por hábito ou executar novas instalações nesta revisão documental.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: Makefile; .github/workflows/ci.yml; scripts/validate.sh; src/local-agent; tests/test_quality_sensors.py; companion Gateway checks.

Fixtures e testes: Tests de quality sensors/GitHub hardening/release checks, CI fixture e Makefile dependency inspection; freeze gate completo uma vez após mudança real.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A12 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A12.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A12.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
