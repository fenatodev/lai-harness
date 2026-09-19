# PR61: Write-mode response budget

## Goal

Evitar truncamentos prematuros do modelo local antes de tool calls completos
em fix, implement, refactor e ci-fix.

## Requirements

- aumentar apenas o orçamento de resposta dos write modes;
- preservar rounds, ferramentas, políticas e authority boundaries;
- manter no máximo um retry por resposta truncada;
- manter teto absoluto de retry em 4096 tokens;
- instruir write modes a preferirem tool calls completos e análise curta;
- não alterar remote-work child limits;
- não alterar permissões, sandbox, promotion ou apply.

## Validation

- fix e implement iniciam com 2048 tokens;
- ci-fix e refactor iniciam com 1536 tokens;
- remote work continua usando REMOTE_WORK_MAX_TOKENS;
- retry continua limitado a 4096;
- testes e checks existentes continuam verdes.
