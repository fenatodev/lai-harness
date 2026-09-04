# lai harness

**Um harness de programação compacto e auditável para LLMs locais.**

Modelos locais pequenos se tornam muito mais úteis quando a arquitetura do agente é otimizada ao redor deles. O lai harness é um harness experimental para VS Code, construído para reduzir contexto desnecessário, schemas de ferramentas e rodadas repetidas de inferência.

Ele complementa agentes cloud de alto contexto: o lai harness atende ciclos locais rápidos e delimitados; outro agente pode assumir trabalhos amplos usando o handoff persistente.

## Destaques

- ferramentas compactas e específicas por modo;
- inspeção e patch em lote;
- guards de validação e aceitação;
- debug, review e security baseados em evidência;
- sanity check após patches;
- métricas, auditoria forense e contexto por workspace;
- cliente Python sem dependências externas;
- identidade pública padronizada como lai harness, mantendo o comando `lai`;
- avaliação determinística de modelos locais com `lai model` antes de trocar o default;
- mapa semântico determinístico com `lai semantics` para orientar modelos pequenos pelos subsistemas;
- histórico determinístico de execuções com `lai runs`, `lai run show` e exportação sanitizada com `lai run export`;
- verificação operacional com `lai readiness`;
- skills focadas `diagnose`, `ci-fix` e `release`, além de gates de preflight, para operar o beta com menos risco.

## Início rápido

Você precisa de Python 3.11+, Git, ripgrep, VS Code compatível e um servidor `llama.cpp` autenticado com API OpenAI-compatible.

```bash
git clone https://github.com/fenatodev/lai-harness.git
cd lai-harness
./scripts/install-local.sh
mkdir -p ~/.config/lai
umask 077
printf '%s' 'substitua-por-uma-chave-local-aleatoria' > ~/.config/lai/llama-api-key
```

Configure `LAI_HOST`, `LAI_PORT` e `LAI_MODEL`, instale a extensão a partir do código e use, por exemplo:

```text
@lai /plan planeje um teste de regressão focado
@lai /debug reproduza e rastreie o valor incorreto
@lai /diagnose diagnostique por que o CI falhou
@lai /ci-fix corrija a falha de validação
@lai /release verifique se a versão está pronta
@lai /implement implemente a mudança e valide
@lai /review revise minhas alterações Git atuais
@lai /handoff contexto para continuar no Codex
```

Para comparar modelos locais sem trocar o default no escuro:

```bash
lai model plan
lai model sample > model-eval/results.jsonl
lai model score model-eval/results.jsonl
lai semantics
lai runs
lai run last
lai run export --last
lai readiness
lai release-check --target 0.4.0-beta.8 --json
lai release-pack --target 0.4.0-beta.8 --with-vsix --json
lai release-governance --target 0.4.0-beta.8 --remote --json
lai project-handoff --target 0.4.0-beta.8 --json
lai release "verifique se beta.8 está pronto"
```

## Segurança

O lai harness **não é uma sandbox**. As ferramentas de arquivo ficam confinadas à raiz do repositório e a ferramenta Git dedicada é somente leitura, mas `bash` executa com as permissões do usuário e usa uma denylist incompleta por natureza. Use uma conta de menor privilégio, mantenha backups e revise os diffs.

Chaves, modelos, logs, estados, métricas, auditoria e handoffs reais não devem ser publicados. Leia [SECURITY-MODEL.md](docs/SECURITY-MODEL.md).

## Resultados experimentais

As medições documentadas vieram de uma máquina e fixtures específicas. Elas mostram a evolução do experimento, não prometem desempenho universal. Consulte [BENCHMARKS.md](docs/BENCHMARKS.md).

O código original do LAI usa MIT. VS Code, llama.cpp, modelos, GGUF e templates permanecem sob termos próprios e não são redistribuídos. Consulte [THIRD_PARTY.md](THIRD_PARTY.md).

A documentação técnica principal está em inglês no diretório [`docs/`](docs/), incluindo [Beta readiness](docs/BETA-READINESS.md).

Use `lai release-pack` and see [Release pack](docs/RELEASE-PACK.md) before manual publication. See [Protected branch write guard](docs/PROTECTED-BRANCH-WRITES.md) before running write-capable modes on release-sensitive branches.

### Workspace seguro para dogfood

Use uma cópia descartável ao testar modos que escrevem arquivos sem tocar na `main`:

```bash
lai workspace create --name smoke
cd /tmp/lai-harness-workspaces/smoke
lai implement "faça uma alteração pequena e valide"
git diff
```

Veja [Safe workspaces](docs/SAFE-WORKSPACES.md).

Leia também [Project handoff](docs/PROJECT-HANDOFF.md) antes de migrar para outro chat.
